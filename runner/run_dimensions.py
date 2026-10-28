#!/usr/bin/env python3
"""Diagnose-then-teach across all five education dimensions.

Extends the staged protocol of the paper ("Instruction Gains Track the Knowledge Gap")
from the Books dimension alone to all five dimensions of the education vector:

  Books    : PLACEBO (length-matched irrelevant text), RULE (the one relevant rule),
             FULL (the whole 16-rule handbook)            -- as in the paper
  Practice : PRACTICE  worked examples (ticket + traceback + before/after code) taken
             from tasks of every family that are NOT in the test set
  Tools    : TOOLS     interactive sandbox: pytest, python snippets, pyflakes lint, grep
  Review   : REVIEW    one self-review turn before submitting
  Retry    : RETRY     one more attempt after CI feedback on a failed submission

Each arm is baseline + one dimension; the task text is identical across arms.

Stages (same as the paper's Gemini replication):
  ranking  : B0 on all 14 families -> rank by baseline pass rate (diagnostic)
  extremes : all arms on ranking positions 1-5 and 10-14
  middle   : all arms on ranking positions 6-9
  report   : full table, gains, Spearman rho per arm
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))

import suite_e5  # noqa: E402
import grader  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "results", "dimensions")
RAW_DIR = os.path.join(OUT_DIR, "raw")

MODEL_CONFIG = {
    "model_id": "gemini-2.5-flash",
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 16384,
    "thinking_budget": 2048,
}

STANDARD_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Do not modify files in tests/ or any test files. Any modification to test files constitutes a policy violation and results in an immediate failure. "
    "Output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

FAMILY_TO_RULE = {
    "money_rounding": "H02", "config_merge": "H03", "service_errors": "H04",
    "calendar_recurrence": "H05", "permission_prefix": "H06", "event_ordering": "H07",
    "wire_envelope": "H08", "timestamp_iso": "H09", "csv_roundtrip": "H10",
    "cache_ttl": "H11", "config_lists": "H12", "idempotency_keys": "H13",
    "metric_percentiles": "H14", "state_transitions": "H15",
}

# Taught and Transfer tasks, first N in identifier order (identical to the paper / Stage 0)
FAMILY_TASKS = {
    "cache_ttl": {"tasks": [2025, 2026, 2027, 2028], "runs_per_task": 4},
    "calendar_recurrence": {"tasks": [2010, 2012], "runs_per_task": 8},
    "config_lists": {"tasks": [2054, 2055, 2057, 2059], "runs_per_task": 4},
    "config_merge": {"tasks": [2006], "runs_per_task": 8},
    "csv_roundtrip": {"tasks": [2014, 2015, 2100, 2101], "runs_per_task": 4},
    "event_ordering": {"tasks": [2022, 2024], "runs_per_task": 8},
    "idempotency_keys": {"tasks": [2062, 2063, 2065, 2067], "runs_per_task": 4},
    "metric_percentiles": {"tasks": [2070, 2071, 2073, 2075], "runs_per_task": 4},
    "money_rounding": {"tasks": [2002, 2003, 2102], "runs_per_task": 6},
    "permission_prefix": {"tasks": [2018, 2020], "runs_per_task": 8},
    "service_errors": {"tasks": [2030, 2031, 2033, 2035], "runs_per_task": 4},
    "state_transitions": {"tasks": [2077, 2078, 2079, 2080], "runs_per_task": 4},
    "timestamp_iso": {"tasks": [2046, 2047, 2049, 2051], "runs_per_task": 4},
    "wire_envelope": {"tasks": [2037, 2038, 2039, 2041], "runs_per_task": 4},
}
TEST_TASK_IDS = {t for spec in FAMILY_TASKS.values() for t in spec["tasks"]}

ARMS = ["B0", "PLACEBO", "RULE", "FULL", "PRACTICE", "TOOLS", "REVIEW", "RETRY"]
ARM_DIMENSION = {
    "B0": "Baseline", "PLACEBO": "Books (control)", "RULE": "Books", "FULL": "Books",
    "PRACTICE": "Practice", "TOOLS": "Tools", "REVIEW": "Review", "RETRY": "Retry",
}
TREATMENT_ARMS = [a for a in ARMS if a != "B0"]

MAX_TOOL_TURNS = 4
TOOL_OUTPUT_LIMIT = 2500
FEEDBACK_LIMIT = 2500

TASKS_BY_ID = {t["id"]: t for t in suite_e5.T}


# --------------------------------------------------------------------------------------
# Brief components
# --------------------------------------------------------------------------------------

def _read(path):
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
        return f.read().strip()


def load_texts():
    b0 = _read("briefs/C0000.md")
    placebo = _read("briefs/PLACEBO.md")
    handbook = _read("briefs/HANDBOOK.md")
    rules = {}
    for fam, rid in FAMILY_TO_RULE.items():
        m = re.search(rf"(### Rule {rid}:.*?(?=(?:\n### |\n## |\Z)))", handbook, re.DOTALL)
        if not m:
            raise ValueError(f"rule {rid} not found")
        rules[fam] = m.group(1).strip()
    practice_path = os.path.join(REPO_ROOT, "briefs", "PRACTICE.md")
    if not os.path.exists(practice_path):
        build_practice_brief()
    practice = _read("briefs/PRACTICE.md")
    return {"b0": b0, "placebo": placebo, "handbook": handbook, "rules": rules, "practice": practice}


def select_practice_tasks():
    """One worked example per family, from tasks outside the test set.

    Preference: TAUGHT (applies the house convention silently) > STATED > TRANSFER.
    DISTRACTOR tasks are excluded (they require the opposite of the rule).
    cache_ttl has no task outside the test set and therefore gets no example.
    """
    pref = {"TAUGHT": 0, "STATED": 1, "TRANSFER": 2}
    chosen = {}
    for fam in FAMILY_TASKS:
        cands = [
            t for t in suite_e5.T
            if t["family"] == fam and t["id"] not in TEST_TASK_IDS and t["class_tag"] in pref
        ]
        if cands:
            chosen[fam] = sorted(cands, key=lambda t: (pref[t["class_tag"]], t["id"]))[0]
    return chosen


def build_practice_brief():
    chosen = select_practice_tasks()
    parts = [
        "# Practice Workbook: Worked Examples",
        "",
        "Before the real ticket, study these solved tickets from this codebase. Each shows the "
        "incident, the failing test output, the original code of the file that had to change, and "
        "the accepted fix. Work through each one: note what the failing value reveals and which "
        "convention the accepted fix applies.",
    ]
    for i, fam in enumerate(sorted(chosen, key=lambda f: chosen[f]["id"]), 1):
        t = chosen[fam]
        parts.append("")
        parts.append(f"## Worked Example {i}")
        parts.append(f"TICKET ISSUE:\n{t['issue']}")
        if t.get("traceback_text"):
            parts.append(f"FAILING TEST TRACEBACK:\n{t['traceback_text']}")
        for path, new in t["ref"].items():
            old = t["repo"].get(path)
            if old is not None:
                parts.append(f"ORIGINAL {path}:\n{old.rstrip()}")
            parts.append(f"ACCEPTED FIX {path}:\n{new.rstrip()}")
    text = "\n".join(parts) + "\n"
    with open(os.path.join(REPO_ROOT, "briefs", "PRACTICE.md"), "w", encoding="utf-8") as f:
        f.write(text)
    meta = {fam: {"task_id": t["id"], "class_tag": t["class_tag"]} for fam, t in chosen.items()}
    with open(os.path.join(REPO_ROOT, "briefs", "PRACTICE_SOURCES.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return text


def arm_prefix(arm, family, texts):
    b0 = texts["b0"]
    if arm == "PLACEBO":
        return f"{b0}\n\n{texts['placebo']}"
    if arm == "RULE":
        return f"{b0}\n\n# Engineering Standards and House Conventions (HANDBOOK.md)\n\n{texts['rules'][family]}"
    if arm == "FULL":
        return f"{b0}\n\n{texts['handbook']}"
    if arm == "PRACTICE":
        return f"{b0}\n\n{texts['practice']}"
    return b0


def task_body(ticket):
    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n" for p, c in ticket["repo"].items()
    )
    tb = ""
    if ticket.get("traceback_text"):
        tb = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n"
    return f"TICKET ISSUE:\n{ticket['issue']}\n\n{tb}REPOSITORY FILES:\n{repo_listing}"


TOOLS_INSTRUCTIONS = (
    "TOOLS: You have a private sandbox that holds a copy of this repository. Before submitting you "
    "may use these tools (up to " + str(MAX_TOOL_TURNS) + " tool turns). To call tools, reply with one "
    "or more tool blocks instead of a final patch:\n"
    "=== TOOL: pytest ===\n<optional space-separated test paths; default: the repository tests>\n=== END_TOOL ===\n"
    "=== TOOL: python ===\n<a Python script, run from the repository root with it on sys.path; use it to "
    "reproduce the failure or check your fix>\n=== END_TOOL ===\n"
    "=== TOOL: lint ===\n<optional space-separated .py paths; default: all source files>\n=== END_TOOL ===\n"
    "=== TOOL: grep ===\n<a regular expression searched in all repository files>\n=== END_TOOL ===\n"
    "Any === FILE: path === ... === END === blocks in a tool turn are applied to the sandbox as a draft "
    "before the tools run, so you can test a draft fix. You will receive the tool output in the next turn. "
    "When you are done, reply with the final patch only (no tool blocks), in the required format."
)


def build_first_prompt(arm, family, ticket, texts):
    prefix = arm_prefix(arm, family, texts)
    prompt = f"{prefix}\n\n{STANDARD_TASK_ENVELOPE_HEADER}\n\n{task_body(ticket)}"
    if arm == "TOOLS":
        prompt += "\n" + TOOLS_INSTRUCTIONS
    return prompt


REVIEW_PROMPT = (
    "Before this patch is submitted, review it yourself. Re-read the ticket, the failing test "
    "traceback and every repository file, then check: (1) Does the patch make the failing value in "
    "the traceback come out right, and does it fix the root cause in the module where the wrong "
    "value is produced rather than only at the call site? (2) Does it break any other caller, the "
    "visible tests, or the documented contracts in the docstrings? (3) Are edge cases handled "
    "(empty input, zero, ties, boundaries)? (4) Is every file syntactically valid, with every import "
    "available in this repository? (5) Did you leave every test file untouched? "
    "Then output your complete final patch in the required === FILE: path === ... === END === format "
    "(repeat it unchanged if it is already correct). Do not write any explanation outside the file blocks."
)


# --------------------------------------------------------------------------------------
# Backends
# --------------------------------------------------------------------------------------

class GeminiBackend:
    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.name = "gemini"

    def call(self, turns):
        """turns: list of (role, text) with role in {user, model}."""
        from google.genai import types
        cfg = types.GenerateContentConfig(
            temperature=MODEL_CONFIG["temperature"],
            top_p=MODEL_CONFIG["top_p"],
            max_output_tokens=MODEL_CONFIG["max_output_tokens"],
            thinking_config=types.ThinkingConfig(thinking_budget=MODEL_CONFIG["thinking_budget"]),
        )
        if len(turns) == 1:
            contents = turns[0][1]
        else:
            contents = [types.Content(role=r, parts=[types.Part(text=t)]) for r, t in turns]
        t0 = time.time()
        res = self.client.models.generate_content(
            model=MODEL_CONFIG["model_id"], contents=contents, config=cfg
        )
        text = ""
        try:
            text = res.text or ""
        except Exception:
            text = ""
        if not text and getattr(res, "candidates", None):
            parts = getattr(getattr(res.candidates[0], "content", None), "parts", None) or []
            text = "".join(getattr(p, "text", "") or "" for p in parts)
        usage = getattr(res, "usage_metadata", None)
        stop = str(res.candidates[0].finish_reason) if getattr(res, "candidates", None) else "NONE"
        return {
            "text": text,
            "prompt_tokens": getattr(usage, "prompt_token_count", 0) or 0,
            "candidate_tokens": getattr(usage, "candidates_token_count", 0) or 0,
            "thoughts_tokens": getattr(usage, "thoughts_token_count", 0) or 0,
            "stop_reason": stop,
            "latency_sec": round(time.time() - t0, 2),
        }


class MockBackend:
    """Offline plumbing check. Mode 'ref' answers with the reference patch, 'empty' with nothing
    useful; in TOOLS it first calls every tool once."""

    def __init__(self, mode):
        self.mode = mode
        self.name = f"mock-{mode}"

    def call(self, turns):
        first = turns[0][1]
        issues = re.findall(r"TICKET ISSUE:\n(.*?)\n\n", first, re.DOTALL)
        ticket = next(t for t in suite_e5.T if issues and t["issue"] == issues[-1])
        patch = "".join(f"=== FILE: {p} ===\n{c}=== END ===\n" for p, c in ticket["ref"].items())
        if self.mode == "empty":
            patch = "=== FILE: notes.txt ===\nno fix\n=== END ===\n"
        if "TOOLS:" in first and len(turns) == 1:
            text = (patch + "=== TOOL: pytest ===\n\n=== END_TOOL ===\n"
                    "=== TOOL: python ===\nprint('hello from sandbox')\n=== END_TOOL ===\n"
                    "=== TOOL: lint ===\n\n=== END_TOOL ===\n=== TOOL: grep ===\ndef \n=== END_TOOL ===\n")
        else:
            text = patch
        return {"text": text, "prompt_tokens": len(first) // 4, "candidate_tokens": len(text) // 4,
                "thoughts_tokens": 0, "stop_reason": "STOP", "latency_sec": 0.0}


def call_with_retry(backend, turns, log):
    """Infrastructure retries: rate limits / 5xx / empty output. Never counted as model retries."""
    delay = 5.0
    last = None
    for i in range(8):
        try:
            r = backend.call(turns)
            if not r["text"].strip():
                raise RuntimeError(f"empty response (stop_reason={r['stop_reason']})")
            if "MAX_TOKENS" in r["stop_reason"]:
                raise RuntimeError("truncated response (MAX_TOKENS)")
            return r
        except Exception as e:  # noqa: BLE001
            last = str(e)[:300]
            log.append({"infra_error": last, "try": i + 1})
            time.sleep(delay + random.random() * 2)
            delay = min(delay * 2, 90)
    raise RuntimeError(f"infrastructure failure after retries: {last}")


# --------------------------------------------------------------------------------------
# Tools sandbox
# --------------------------------------------------------------------------------------

TOOL_RE = re.compile(r"=== TOOL:\s*(\w+)\s*===\s*\n(.*?)=== END_TOOL ===", re.DOTALL)


def strip_tool_blocks(text):
    return TOOL_RE.sub("", text)


class Sandbox:
    def __init__(self, repo):
        self.repo = repo
        self.dir = tempfile.mkdtemp(prefix="dim_tools_")
        self.state = dict(repo)
        self._write_all()

    def _write_all(self):
        shutil.rmtree(self.dir, ignore_errors=True)
        os.makedirs(self.dir)
        for p, c in self.state.items():
            fp = os.path.join(self.dir, p)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(c)
        open(os.path.join(self.dir, "conftest.py"), "a").close()

    def apply(self, text):
        files, deletes = grader.parse_blocks(strip_tool_blocks(text))
        files = {p: c for p, c in files.items() if not grader.bad_path(p)}
        if not files and not deletes:
            return []
        self.state.update(files)
        for p in deletes:
            if not grader.bad_path(p):
                self.state.pop(p, None)
        self._write_all()
        return sorted(files) + sorted(deletes)

    def draft_patch(self):
        out = []
        for p, c in self.state.items():
            if self.repo.get(p) != c:
                out.append(f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n")
        for p in self.repo:
            if p not in self.state:
                out.append(f"=== DELETE: {p} ===\n")
        return "".join(out)

    def _run(self, cmd, timeout=30, stdin=None):
        env = dict(os.environ, PYTHONPATH=self.dir, PYTHONDONTWRITEBYTECODE="1")
        env.pop("GEMINI_API_KEY", None)
        try:
            pr = subprocess.run(cmd, cwd=self.dir, env=env, capture_output=True, text=True,
                                timeout=timeout, input=stdin)
            out = (pr.stdout + pr.stderr)
            return pr.returncode, out[-TOOL_OUTPUT_LIMIT:]
        except subprocess.TimeoutExpired:
            return 124, f"timed out after {timeout} s"

    def run_tool(self, name, arg):
        name = name.lower()
        arg = arg.strip()
        if name == "pytest":
            paths = [a for a in arg.split() if not a.startswith("-") and ".." not in a and not a.startswith("/")]
            return self._run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                              "--tb=short", "--no-header", "-W", "ignore"] + (paths or ["tests"]))
        if name == "python":
            return self._run([sys.executable, "-"], timeout=20, stdin=arg)
        if name == "lint":
            paths = [a for a in arg.split() if a.endswith(".py") and ".." not in a and not a.startswith("/")]
            if not paths:
                paths = sorted(p for p in self.state if p.endswith(".py") and not p.startswith("tests/"))
            return self._run([sys.executable, "-m", "pyflakes"] + paths)
        if name == "grep":
            try:
                rx = re.compile(arg)
            except re.error as e:
                return 2, f"invalid regex: {e}"
            hits = []
            for p in sorted(self.state):
                for i, line in enumerate(self.state[p].splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{p}:{i}:{line}")
            return (0 if hits else 1), ("\n".join(hits) or "no matches")[-TOOL_OUTPUT_LIMIT:]
        return 2, f"unknown tool '{name}'. Available: pytest, python, lint, grep"

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


# --------------------------------------------------------------------------------------
# Retry feedback (CI report on the submitted patch)
# --------------------------------------------------------------------------------------

def ci_feedback(ticket, patch_text, grade):
    files, deletes = grader.parse_blocks(patch_text)
    files = {p: c for p, c in files.items() if not grader.bad_path(p)}
    deletes = [p for p in deletes if not grader.bad_path(p)]
    lines = ["CI REPORT: your submitted patch was rejected."]
    if grade["violations"]:
        lines.append("Policy violations:\n- " + "\n- ".join(grade["violations"]))
    if grade["visible_rc"] != 0:
        lines.append(f"Repository tests (exit code {grade['visible_rc']}):\n{grade['visible_output'][-FEEDBACK_LIMIT:]}")
    if not grade["func_pass"]:
        v = ticket["key"]["variants"][0]
        d = grader.build_isolated_dir(ticket["repo"], files, deletes, overlay=v.get("overlay"))
        try:
            rc, out = grader.run_pytest(d, v.get("paths", ["tests"]))
        finally:
            shutil.rmtree(d, ignore_errors=True)
        lines.append(f"CI test suite (exit code {rc}):\n{out[-FEEDBACK_LIMIT:]}")
    lines.append(
        "Fix the problem and reply with your complete corrected patch in the required "
        "=== FILE: path === ... === END === format. Do not write any explanation outside the file blocks."
    )
    return "\n\n".join(lines)


# --------------------------------------------------------------------------------------
# One attempt
# --------------------------------------------------------------------------------------

def run_attempt(att, backend, texts):
    arm, fam, tid, run_idx = att["arm"], att["family"], att["task_id"], att["run_idx"]
    out_file = os.path.join(RAW_DIR, f"{arm}_{fam}_t{tid}_r{run_idx}.json")
    if os.path.exists(out_file):
        with open(out_file, encoding="utf-8") as f:
            saved = json.load(f)
        if saved.get("status") == "COMPLETED":
            return saved

    ticket = TASKS_BY_ID[tid]
    infra_log = []
    turns = [("user", build_first_prompt(arm, fam, ticket, texts))]
    transcript = []
    tok = {"prompt_tokens": 0, "candidate_tokens": 0, "thoughts_tokens": 0}
    extra = {}

    def model_turn(kind):
        r = call_with_retry(backend, turns, infra_log)
        for k in tok:
            tok[k] += r[k]
        turns.append(("model", r["text"]))
        transcript.append({"kind": kind, "prompt": turns[-2][1] if len(turns) > 2 else "<first prompt>",
                           "response": r["text"], "stop_reason": r["stop_reason"]})
        return r["text"]

    try:
        resp = model_turn("initial")
        attempt1_patch = resp

        if arm == "TOOLS":
            sb = Sandbox(ticket["repo"])
            tool_calls = []
            try:
                tool_turns = 0
                while TOOL_RE.search(resp) and tool_turns < MAX_TOOL_TURNS:
                    tool_turns += 1
                    applied = sb.apply(resp)
                    outputs = []
                    for name, arg in TOOL_RE.findall(resp)[:6]:
                        rc, out = sb.run_tool(name, arg)
                        tool_calls.append({"turn": tool_turns, "tool": name, "rc": rc})
                        outputs.append(f"=== TOOL_OUTPUT: {name} (exit code {rc}) ===\n{out}\n=== END_TOOL_OUTPUT ===")
                    note = f"Draft applied to sandbox: {', '.join(applied)}\n\n" if applied else ""
                    remaining = MAX_TOOL_TURNS - tool_turns
                    turns.append(("user", note + "\n".join(outputs) + (
                        f"\n\nYou have {remaining} tool turn(s) left. Call more tools, or reply with the final patch only."
                        if remaining else "\n\nNo tool turns left. Reply with the final patch only.")))
                    resp = model_turn(f"tool_turn_{tool_turns}")
                if TOOL_RE.search(resp):
                    sb.apply(resp)
                    turns.append(("user", "Tool budget exhausted. Reply with your complete final patch only, "
                                          "in the required === FILE: path === ... === END === format."))
                    resp = model_turn("forced_final")
                final_files, final_dels = grader.parse_blocks(strip_tool_blocks(resp))
                if not final_files and not final_dels:
                    resp = sb.draft_patch()
                    extra["final_from_sandbox_draft"] = True
                extra["tool_calls"] = tool_calls
                extra["tool_turns"] = tool_turns
                extra["tools_used"] = sorted({c["tool"] for c in tool_calls})
            finally:
                sb.cleanup()
            attempt1_patch = strip_tool_blocks(resp)
            final_patch = attempt1_patch
            grade1 = grader.evaluate_patch(ticket["repo"], attempt1_patch, ticket["key"])
            grade_final = grade1

        elif arm == "REVIEW":
            grade1 = grader.evaluate_patch(ticket["repo"], attempt1_patch, ticket["key"])
            turns.append(("user", REVIEW_PROMPT))
            final_patch = model_turn("review")
            grade_final = grader.evaluate_patch(ticket["repo"], final_patch, ticket["key"])
            extra["review_changed_patch"] = grader.parse_blocks(final_patch) != grader.parse_blocks(attempt1_patch)

        elif arm == "RETRY":
            grade1 = grader.evaluate_patch(ticket["repo"], attempt1_patch, ticket["key"])
            final_patch, grade_final = attempt1_patch, grade1
            extra["retried"] = False
            if not grade1["strict_pass"]:
                turns.append(("user", ci_feedback(ticket, attempt1_patch, grade1)))
                final_patch = model_turn("retry_1")
                grade_final = grader.evaluate_patch(ticket["repo"], final_patch, ticket["key"])
                extra["retried"] = True
        else:
            final_patch = attempt1_patch
            grade1 = grader.evaluate_patch(ticket["repo"], attempt1_patch, ticket["key"])
            grade_final = grade1

        record = {
            "status": "COMPLETED",
            "arm": arm, "dimension": ARM_DIMENSION[arm], "family": fam,
            "rule_id": FAMILY_TO_RULE[fam], "task_id": tid, "run_idx": run_idx,
            "stage": att.get("stage"), "order_idx": att.get("order_idx"),
            "strict_pass": bool(grade_final["strict_pass"]),
            "attempt1_strict_pass": bool(grade1["strict_pass"]),
            "func_pass": bool(grade_final["func_pass"]),
            "tamper": bool(grade_final["tamper"]),
            "violations": grade_final["violations"],
            "changed_files": grade_final["changed_files"],
            "model_turns": sum(1 for r, _ in turns if r == "model"),
            **tok, **extra,
            "infra_log": infra_log,
            "backend": backend.name, **{f"cfg_{k}": v for k, v in MODEL_CONFIG.items()},
            "final_patch": final_patch,
            "transcript": transcript,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:  # noqa: BLE001
        record = {"status": "INFRA_FAILURE", "arm": arm, "family": fam, "task_id": tid,
                  "run_idx": run_idx, "error": str(e)[:500], "infra_log": infra_log,
                  "timestamp": datetime.now(timezone.utc).isoformat()}
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return record


# --------------------------------------------------------------------------------------
# Schedules and stages
# --------------------------------------------------------------------------------------

def build_schedule(families, arms, stage, seed):
    sched = []
    for fam in families:
        spec = FAMILY_TASKS[fam]
        for arm in arms:
            for tid in spec["tasks"]:
                for r in range(spec["runs_per_task"]):
                    sched.append({"arm": arm, "family": fam, "task_id": tid, "run_idx": r + 1, "stage": stage})
    random.Random(seed).shuffle(sched)
    for i, a in enumerate(sched):
        a["order_idx"] = i + 1
    return sched


def execute(schedule, backend, texts, workers):
    os.makedirs(RAW_DIR, exist_ok=True)
    lock = threading.Lock()
    done = {"n": 0, "k": 0, "infra": 0}
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_attempt, a, backend, texts): a for a in schedule}
        for fut in as_completed(futs):
            a = futs[fut]
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001
                r = {"status": "INFRA_FAILURE", "error": str(e)}
            with lock:
                results.append(r)
                done["n"] += 1
                done["k"] += int(bool(r.get("strict_pass")))
                done["infra"] += int(r.get("status") != "COMPLETED")
                mark = "PASS" if r.get("strict_pass") else ("INFRA" if r.get("status") != "COMPLETED" else "FAIL")
                print(f"[{done['n']:4d}/{len(schedule)}] {a['arm']:8s} {a['family']:20s} t{a['task_id']} r{a['run_idx']} -> {mark}"
                      f"  (pass {done['k']}, infra {done['infra']})", flush=True)
    return results


def load_all_records():
    recs = []
    if not os.path.isdir(RAW_DIR):
        return recs
    for fn in sorted(os.listdir(RAW_DIR)):
        if fn.endswith(".json"):
            with open(os.path.join(RAW_DIR, fn), encoding="utf-8") as f:
                r = json.load(f)
            if r.get("status") == "COMPLETED":
                recs.append(r)
    return recs


def cell(recs, arm, fam, key="strict_pass"):
    rs = [r for r in recs if r["arm"] == arm and r["family"] == fam]
    return sum(1 for r in rs if r.get(key)), len(rs)


def compute_ranking(recs):
    rows = []
    for fam in FAMILY_TASKS:
        k, n = cell(recs, "B0", fam)
        rows.append({"family": fam, "rule_id": FAMILY_TO_RULE[fam], "k": k, "n": n,
                     "baseline_pct": 100.0 * k / n if n else float("nan")})
    rows.sort(key=lambda x: (x["baseline_pct"], x["family"]))
    for i, r in enumerate(rows, 1):
        r["position"] = i
    return rows


def save_ranking(rows):
    with open(os.path.join(OUT_DIR, "ranking.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    with open(os.path.join(OUT_DIR, "ranking.csv"), "w", encoding="utf-8") as f:
        f.write("position,family,rule_id,k,n,baseline_pct\n")
        for r in rows:
            f.write(f"{r['position']},{r['family']},{r['rule_id']},{r['k']},{r['n']},{r['baseline_pct']:.2f}\n")


def stage_families(stage):
    with open(os.path.join(OUT_DIR, "ranking.json"), encoding="utf-8") as f:
        rows = json.load(f)
    pos = {"extremes": set(range(1, 6)) | set(range(10, 15)), "middle": set(range(6, 10))}[stage]
    return [r["family"] for r in rows if r["position"] in pos]


# --------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------

def spearman(x, y):
    from scipy.stats import spearmanr
    if len(x) < 3:
        return float("nan")
    return float(spearmanr(x, y).correlation)


def write_report(recs, families_scope=None):
    with open(os.path.join(OUT_DIR, "ranking.json"), encoding="utf-8") as f:
        ranking = json.load(f)
    fams = [r["family"] for r in ranking if (families_scope is None or r["family"] in families_scope)]
    pos = {r["family"]: r["position"] for r in ranking}

    table = []
    for fam in fams:
        bk, bn = cell(recs, "B0", fam)
        row = {"position": pos[fam], "family": fam, "rule_id": FAMILY_TO_RULE[fam],
               "B0": [bk, bn]}
        for arm in TREATMENT_ARMS:
            k, n = cell(recs, arm, fam)
            row[arm] = [k, n]
            row[f"gain_{arm}"] = (100.0 * k / n - 100.0 * bk / bn) if n and bn else None
        for arm in ("REVIEW", "RETRY"):
            k1, n1 = cell(recs, arm, fam, "attempt1_strict_pass")
            row[f"{arm}_attempt1"] = [k1, n1]
        table.append(row)

    rho = {}
    for arm in TREATMENT_ARMS:
        xs = [100.0 * r["B0"][0] / r["B0"][1] for r in table if r[arm][1] and r["B0"][1]]
        ys = [r[f"gain_{arm}"] for r in table if r[arm][1] and r["B0"][1]]
        rho[arm] = spearman(xs, ys) if len(xs) >= 3 else None

    totals = {}
    for arm in ARMS:
        k = sum(r[arm][0] for r in table)
        n = sum(r[arm][1] for r in table)
        totals[arm] = [k, n]

    tok = {}
    for arm in ARMS:
        rs = [r for r in recs if r["arm"] == arm and r["family"] in fams]
        tok[arm] = sum(r["prompt_tokens"] + r["candidate_tokens"] + r["thoughts_tokens"] for r in rs)

    summary = {"table": table, "spearman_rho_gain_vs_baseline": rho, "totals": totals,
               "tokens": tok, "model": MODEL_CONFIG, "n_attempts": len(recs),
               "generated": datetime.now(timezone.utc).isoformat()}
    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    def kn(c):
        return f"{c[0]}/{c[1]}" if c[1] else "–"

    def g(v):
        return "–" if v is None else f"{v:+.0f}"

    hdr = ["Pos", "Family", "Rule", "Baseline"] + TREATMENT_ARMS
    lines = ["| " + " | ".join(hdr) + " |", "|" + "|".join([":-:", ":--", ":-:"] + [":-:"] * (len(hdr) - 3)) + "|"]
    for r in table:
        cells = [str(r["position"]), f"`{r['family']}`", r["rule_id"], kn(r["B0"])]
        for arm in TREATMENT_ARMS:
            cells.append(f"{kn(r[arm])} ({g(r['gain_' + arm])})" if r[arm][1] else "–")
        lines.append("| " + " | ".join(cells) + " |")
    tot_cells = ["", "**All families**", "", kn(totals["B0"])]
    for arm in TREATMENT_ARMS:
        if not totals[arm][1]:
            tot_cells.append("–")
            continue
        gain = None
        if totals["B0"][1]:
            gain = 100.0 * (totals[arm][0] / totals[arm][1] - totals["B0"][0] / totals["B0"][1])
        tot_cells.append(f"{kn(totals[arm])} ({g(gain)})")
    lines.append("| " + " | ".join(tot_cells) + " |")
    rho_cells = ["", "**Spearman rho (gain vs baseline)**", "", ""]
    for arm in TREATMENT_ARMS:
        rho_cells.append("–" if rho[arm] is None else f"{rho[arm]:.2f}")
    lines.append("| " + " | ".join(rho_cells) + " |")
    md_table = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "TABLE.md"), "w", encoding="utf-8") as f:
        f.write(md_table + "\n")
    with open(os.path.join(OUT_DIR, "table.csv"), "w", encoding="utf-8") as f:
        f.write("position,family,rule_id," + ",".join(f"{a}_k,{a}_n" for a in ARMS) + ","
                + ",".join(f"gain_{a}" for a in TREATMENT_ARMS) + "\n")
        for r in table:
            f.write(f"{r['position']},{r['family']},{r['rule_id']},"
                    + ",".join(f"{r[a][0]},{r[a][1]}" for a in ARMS) + ","
                    + ",".join("" if r[f'gain_{a}'] is None else f"{r[f'gain_{a}']:.2f}" for a in TREATMENT_ARMS) + "\n")
    return md_table, summary


# --------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["ranking", "extremes", "middle", "report", "practice-brief"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--mock", choices=["ref", "empty"], default=None,
                    help="offline plumbing check (writes to results/dimensions_mock)")
    ap.add_argument("--families", default=None, help="comma-separated override of the stage's families")
    ap.add_argument("--arms", default=None, help="comma-separated override of arms")
    ap.add_argument("--limit", type=int, default=None, help="run only the first N scheduled attempts")
    args = ap.parse_args()

    global OUT_DIR, RAW_DIR
    if args.mock:
        OUT_DIR = os.path.join(REPO_ROOT, "results", f"dimensions_mock_{args.mock}")
        RAW_DIR = os.path.join(OUT_DIR, "raw")
    os.makedirs(RAW_DIR, exist_ok=True)

    if args.stage == "practice-brief":
        build_practice_brief()
        print(json.dumps({f: t["id"] for f, t in select_practice_tasks().items()}, indent=2))
        return

    if args.stage == "report":
        md, s = write_report(load_all_records())
        print(md)
        return

    texts = load_texts()
    backend = MockBackend(args.mock) if args.mock else GeminiBackend()
    if not args.mock:
        probe = call_with_retry(backend, [("user", "Respond with 'READY' and nothing else.")], [])
        print(f"startup probe: {probe['text'].strip()[:20]!r}")

    if args.stage == "ranking":
        fams, arms, seed = list(FAMILY_TASKS), ["B0"], 42
    else:
        fams = stage_families(args.stage)
        arms, seed = TREATMENT_ARMS, {"extremes": 43, "middle": 44}[args.stage]
    if args.families:
        fams = args.families.split(",")
    if args.arms:
        arms = args.arms.split(",")
    sched = build_schedule(fams, arms, args.stage, seed)
    if args.limit:
        sched = sched[: args.limit]
    with open(os.path.join(OUT_DIR, f"schedule_{args.stage}.json"), "w", encoding="utf-8") as f:
        json.dump(sched, f, indent=2)
    print(f"stage={args.stage} families={fams} arms={arms} attempts={len(sched)} workers={args.workers}")
    t0 = time.time()
    execute(sched, backend, texts, args.workers)
    print(f"elapsed {time.time() - t0:.0f}s")

    recs = load_all_records()
    if args.stage == "ranking":
        rows = compute_ranking(recs)
        save_ranking(rows)
        for r in rows:
            print(f"{r['position']:2d} {r['family']:20s} {r['k']}/{r['n']} {r['baseline_pct']:.1f}%")
    else:
        md, _ = write_report(recs)
        print(md)


if __name__ == "__main__":
    main()
