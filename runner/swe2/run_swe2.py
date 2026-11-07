#!/usr/bin/env python3
"""SWE-2: education by ontology + knowledge harness + confidence harness (no handbook text).

The student (a local open-weight coding model) acts as a debugging agent: it reads the ticket,
runs tools in a sandbox (pytest, python, grep, lint), edits files and submits a patch that is
graded strict-pass on the hidden tests (runner/grader.py, as in the paper).

Arms (task text and tools identical in every arm):
  B0         baseline debugging agent
  PLACEBO    ontology + knowledge harness over a graph of irrelevant rules (briefs/PLACEBO.md)
  KNOW       ontology + knowledge harness over the handbook-derived graph (ontology.py)
  SURE       confidence harness only: repeated diagnoses + calibrated confidence -> revise
  KNOW_SURE  KNOW + SURE
There is no action gate: every attempt submits.

Stages
  quiz     closed-book familiarity quiz (quiz.py)
  b0       B0 on all 14 families (+ post-hoc confidence probe -> calibration map)
  arms     PLACEBO, KNOW, SURE, KNOW_SURE on all 14 families
  report   tables + familiarity/gain correlations (analyze.py)
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))

import suite_e5  # noqa: E402
import grader  # noqa: E402
import harness  # noqa: E402
import llm  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "results", "swe2")
RAW_DIR = os.path.join(OUT_DIR, "raw")
CALIB_PATH = os.path.join(OUT_DIR, "calibration_map.json")

FAMILY_TO_RULE = {
    "money_rounding": "H02", "config_merge": "H03", "service_errors": "H04",
    "calendar_recurrence": "H05", "permission_prefix": "H06", "event_ordering": "H07",
    "wire_envelope": "H08", "timestamp_iso": "H09", "csv_roundtrip": "H10",
    "cache_ttl": "H11", "config_lists": "H12", "idempotency_keys": "H13",
    "metric_percentiles": "H14", "state_transitions": "H15",
}
# Same test tasks as the paper / runner/run_dimensions.py
FAMILY_TASKS = {
    "cache_ttl": [2025, 2026, 2027, 2028], "calendar_recurrence": [2010, 2012],
    "config_lists": [2054, 2055, 2057, 2059], "config_merge": [2006],
    "csv_roundtrip": [2014, 2015, 2100, 2101], "event_ordering": [2022, 2024],
    "idempotency_keys": [2062, 2063, 2065, 2067], "metric_percentiles": [2070, 2071, 2073, 2075],
    "money_rounding": [2002, 2003, 2102], "permission_prefix": [2018, 2020],
    "service_errors": [2030, 2031, 2033, 2035], "state_transitions": [2077, 2078, 2079, 2080],
    "timestamp_iso": [2046, 2047, 2049, 2051], "wire_envelope": [2037, 2038, 2039, 2041],
}
ARMS = ["B0", "PLACEBO", "KNOW", "SURE", "KNOW_SURE"]
GRAPH_SOURCE = {"PLACEBO": "placebo", "KNOW": "handbook", "KNOW_SURE": "handbook"}
SURE_ARMS = {"SURE", "KNOW_SURE"}

MAX_TOOL_TURNS = 3
TOOL_OUTPUT_LIMIT = 2000
MAX_TOKENS = 3000
RETRIEVE_K = 3
SURE_SAMPLES = 3
SURE_THRESHOLD = 0.5
TASKS_BY_ID = {t["id"]: t for t in suite_e5.T}

SYSTEM = open(os.path.join(REPO_ROOT, "briefs", "C0000.md"), encoding="utf-8").read().strip()

ENVELOPE = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Do not modify files in tests/ or any test files. Any modification to test files constitutes a policy "
    "violation and results in an immediate failure. Change files with edit blocks (preferred):\n"
    "=== EDIT: path/to/file ===\n<<<<<<< SEARCH\n<exact existing lines>\n=======\n<replacement lines>\n"
    ">>>>>>> REPLACE\n=== END ===\n"
    "(one block per change; the SEARCH text must match the current file exactly once), or with whole-file "
    "blocks: === FILE: path/to/file === then the COMPLETE new content, then === END ===. To delete a file "
    "write === DELETE: path ===. Paths are relative to the repository root. Do not use markdown fences."
)


def tools_text(graph_tool):
    t = (
        "TOOLS: You are debugging in a private sandbox holding a copy of this repository. Before submitting "
        f"you may use tools (up to {MAX_TOOL_TURNS} tool turns). To call tools, reply with one or more tool "
        "blocks:\n"
        "=== TOOL: pytest ===\n<optional test paths; default: the repository tests>\n=== END_TOOL ===\n"
        "=== TOOL: python ===\n<a Python script run from the repository root; reproduce the failure or check "
        "your fix>\n=== END_TOOL ===\n"
        "=== TOOL: grep ===\n<a regular expression searched in all repository files>\n=== END_TOOL ===\n"
        "=== TOOL: lint ===\n<optional .py paths>\n=== END_TOOL ===\n"
    )
    if graph_tool:
        t += ("=== TOOL: know ===\n<a convention id such as H07 (or P07), or keywords; returns that part of the "
              "knowledge graph>\n=== END_TOOL ===\n")
    t += ("EDIT/FILE blocks are applied to the sandbox immediately (before any tools in the same reply run). "
          "You receive tool output in the next turn. When done, reply with your last EDIT/FILE blocks (if any) "
          "and no tool blocks; the sandbox state is then submitted as your patch.")
    return t


def knowledge_prefix(source, ticket_text):
    ids, block = harness.knowledge_block(ticket_text, RETRIEVE_K, source)
    txt = (
        "KNOWLEDGE HARNESS. This codebase's house conventions are given as a typed knowledge graph.\n"
        f"{harness.SCHEMA}\n\nCONTEXT INDEX (all conventions):\n{harness.context_index(source)}\n\n"
        "RETRIEVED FOR THIS TICKET (the knowledge graph entries most related to the ticket; a convention "
        "applies only if the code in this ticket falls in its scope):\n" + block
    )
    return ids, txt


def task_body(ticket):
    files = "".join(f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n" for p, c in ticket["repo"].items())
    tb = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n" if ticket.get("traceback_text") else ""
    return f"TICKET ISSUE:\n{ticket['issue']}\n\n{tb}REPOSITORY FILES:\n{files}"


def ticket_text(ticket):
    return ticket["issue"] + "\n" + (ticket.get("traceback_text") or "") + "\n" + "\n".join(ticket["repo"].values())


def build_first_prompt(arm, ticket):
    parts, meta = [], {}
    src = GRAPH_SOURCE.get(arm)
    if src:
        ids, kp = knowledge_prefix(src, ticket_text(ticket))
        parts.append(kp)
        meta["retrieved"] = ids
    parts += [ENVELOPE, task_body(ticket), tools_text(bool(src))]
    return "\n\n".join(parts), meta


# ----------------------------------------------------------------------------------------------
# Sandbox (same tool semantics as runner/run_dimensions.py TOOLS arm, plus `know`)
# ----------------------------------------------------------------------------------------------

TOOL_RE = re.compile(r"=== TOOL:\s*(\w+)\s*===\s*\n(.*?)=== END_TOOL ===", re.DOTALL)
EDIT_RE = re.compile(r"=== EDIT:\s*(.+?)\s*===[ \t]*\n<<<<<<< SEARCH[ \t]*\n(.*?)\n?=======[ \t]*\n(.*?)\n?"
                     r">>>>>>> REPLACE[ \t]*(?:\n[ \t]*=== END ===)?", re.DOTALL)
FENCE_OPEN = re.compile(r"^(=== FILE: .+? ===)[ \t]*\n[ \t]*```[\w+-]*[ \t]*\n", re.MULTILINE)
FENCE_CLOSE = re.compile(r"\n[ \t]*```[ \t]*\n([ \t]*=== END ===)", re.MULTILINE)


def strip_tool_blocks(text):
    return TOOL_RE.sub("", text)


def apply_edit(content, search, replace):
    """Exact match first, then a match that ignores trailing whitespace per line."""
    n = content.count(search)
    if n == 1:
        return content.replace(search, replace), None
    if n == 0 and search.strip():
        lines, pat = content.split("\n"), [x.rstrip() for x in search.strip("\n").split("\n")]
        hits = [i for i in range(len(lines) - len(pat) + 1)
                if [x.rstrip() for x in lines[i:i + len(pat)]] == pat]
        if len(hits) == 1:
            i = hits[0]
            return "\n".join(lines[:i] + replace.strip("\n").split("\n") + lines[i + len(pat):]), None
        n = len(hits)
    return None, ("SEARCH text not found" if n == 0 else f"SEARCH text matches {n} places; add context")


def normalize_fences(text):
    return FENCE_CLOSE.sub(r"\n\1", FENCE_OPEN.sub(r"\1\n", text))


class Sandbox:
    def __init__(self, repo, graph_source=None):
        self.repo, self.graph_source = repo, graph_source
        self.dir = tempfile.mkdtemp(prefix="swe2_")
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
        """Applies FILE/DELETE then EDIT blocks; returns (changed paths, edit errors). Test-file changes are
        kept so that the grader judges tampering on the submitted patch."""
        text = strip_tool_blocks(text)
        files, deletes = grader.parse_blocks(EDIT_RE.sub("", text))
        self.state.update(files)
        for p in deletes:
            self.state.pop(p, None)
        changed, errors = set(files) | set(deletes), []
        for path, search, replace in EDIT_RE.findall(text):
            path = path.strip().lstrip("./")
            if path not in self.state:
                errors.append(f"EDIT {path}: no such file")
                continue
            new, err = apply_edit(self.state[path], search, replace)
            if err:
                errors.append(f"EDIT {path}: {err}")
            else:
                self.state[path] = new
                changed.add(path)
        if changed:
            self._write_all()
        return sorted(changed), errors

    def draft_patch(self):
        out = [f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n" for p, c in self.state.items() if self.repo.get(p) != c]
        out += [f"=== DELETE: {p} ===\n" for p in self.repo if p not in self.state]
        return "".join(out)

    def _run(self, cmd, timeout=30, stdin=None):
        env = dict(os.environ, PYTHONPATH=self.dir, PYTHONDONTWRITEBYTECODE="1")
        try:
            pr = subprocess.run(cmd, cwd=self.dir, env=env, capture_output=True, text=True, timeout=timeout, input=stdin)
            return pr.returncode, (pr.stdout + pr.stderr)[-TOOL_OUTPUT_LIMIT:]
        except subprocess.TimeoutExpired:
            return 124, f"timed out after {timeout} s"

    def run_tool(self, name, arg):
        name, arg = name.lower(), arg.strip()
        if name == "pytest":
            paths = [a for a in arg.split() if not a.startswith("-") and ".." not in a and not a.startswith("/")]
            return self._run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short",
                              "--no-header", "-W", "ignore"] + (paths or ["tests"]))
        if name == "python":
            return self._run([sys.executable, "-"], timeout=20, stdin=arg)
        if name == "lint":
            paths = [a for a in arg.split() if a.endswith(".py") and ".." not in a and not a.startswith("/")]
            paths = paths or sorted(p for p in self.state if p.endswith(".py") and not p.startswith("tests/"))
            return self._run([sys.executable, "-m", "pyflakes"] + paths)
        if name == "grep":
            try:
                rx = re.compile(arg)
            except re.error as e:
                return 2, f"invalid regex: {e}"
            hits = [f"{p}:{i}:{ln}" for p in sorted(self.state) for i, ln in enumerate(self.state[p].splitlines(), 1)
                    if rx.search(ln)]
            return (0 if hits else 1), ("\n".join(hits) or "no matches")[-TOOL_OUTPUT_LIMIT:]
        if name == "know" and self.graph_source:
            return 0, harness.query(arg, self.graph_source)[-TOOL_OUTPUT_LIMIT:]
        avail = "pytest, python, grep, lint" + (", know" if self.graph_source else "")
        return 2, f"unknown tool '{name}'. Available: {avail}"

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


# ----------------------------------------------------------------------------------------------
# Confidence harness
# ----------------------------------------------------------------------------------------------

def diag_prompt(with_rule):
    rule = ("RULE: <id of the house convention your fix applies, e.g. H07, or none>\n" if with_rule else "")
    return ("CONFIDENCE CHECK (do not output a patch now). Reply with exactly these lines:\n"
            "ROOT_CAUSE: <file>::<function> where the wrong value is produced\n" + rule +
            "CONFIDENCE: <integer 0-100, the probability that your patch passes the hidden CI test suite>")


DIAG_RE = {
    "ROOT_CAUSE": re.compile(r"^\W*ROOT[_ ]?\w*:\s*(.+)", re.I | re.M),
    "RULE": re.compile(r"^\W*RULE:\s*(.+)", re.I | re.M),
    "CONFIDENCE": re.compile(r"^\W*CONFIDENCE:\s*(.+)", re.I | re.M),
}


def parse_diag(text):
    out = {}
    for k, rx in DIAG_RE.items():
        m = rx.search(text)
        out[k.lower()] = m.group(1).strip() if m else None
    m = re.search(r"\d+(?:\.\d+)?", out["confidence"] or "")
    out["confidence"] = max(0.0, min(100.0, float(m.group(0)))) / 100 if m else None
    rc = re.search(r"[\w./-]+(?:\.py)?::\w+", (out["root_cause"] or "").replace("`", ""))
    out["root_cause_norm"] = rc.group(0).lower() if rc else (out["root_cause"] or "").lower().strip()[:60]
    rr = re.search(r"\b[hp]\d\d\b", (out["rule"] or "").lower())
    out["rule_norm"] = rr.group(0).upper() if rr else "none"
    return out


def load_calibration():
    if os.path.exists(CALIB_PATH):
        with open(CALIB_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


def calibrate(conf, cmap):
    """Piecewise-constant isotonic map stated confidence -> empirical pass probability."""
    if conf is None:
        return 0.0
    if not cmap:
        return conf
    for b in cmap["bins"]:
        if conf <= b["hi"]:
            return b["p"]
    return cmap["bins"][-1]["p"]


def fit_calibration(pairs):
    """pairs: (stated confidence 0-1, passed bool). Pool-adjacent-violators over 10 bins."""
    bins = []
    for i in range(10):
        lo, hi = i / 10, (i + 1) / 10
        xs = [y for c, y in pairs if (lo < c <= hi) or (i == 0 and c == 0)]
        if xs:
            bins.append({"lo": lo, "hi": hi, "n": len(xs), "p": sum(xs) / len(xs)})
    merged = []
    for b in bins:
        merged.append(dict(b))
        while len(merged) > 1 and merged[-2]["p"] > merged[-1]["p"]:
            b2, b1 = merged.pop(), merged.pop()
            n = b1["n"] + b2["n"]
            merged.append({"lo": b1["lo"], "hi": b2["hi"], "n": n, "p": (b1["p"] * b1["n"] + b2["p"] * b2["n"]) / n})
    if merged:
        merged[-1]["hi"] = 1.0
    return {"bins": merged, "n": len(pairs)}


# ----------------------------------------------------------------------------------------------
# One attempt
# ----------------------------------------------------------------------------------------------

class Conversation:
    def __init__(self, first_prompt):
        self.msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": first_prompt}]
        self.transcript, self.tok = [], {"prompt_tokens": 0, "completion_tokens": 0}
        self.latency = 0.0

    def turn(self, kind, user=None, keep=True, max_tokens=MAX_TOKENS, temperature=None):
        if user is not None:
            self.msgs.append({"role": "user", "content": user})
        r = llm.chat(self.msgs, max_tokens=max_tokens, temperature=temperature)
        self.tok["prompt_tokens"] += r["prompt_tokens"]
        self.tok["completion_tokens"] += r["completion_tokens"]
        self.latency += r["latency_sec"]
        self.transcript.append({"kind": kind, "prompt": user or "<first prompt>", "response": r["text"],
                                "finish": r["finish"]})
        if keep:
            self.msgs.append({"role": "assistant", "content": r["text"]})
        else:
            if user is not None:
                self.msgs.pop()
        return normalize_fences(r["text"])


def tool_loop(conv, sb, resp, budget, calls, label):
    used = 0
    edit_fix = 1
    while TOOL_RE.search(resp) and used < budget:
        used += 1
        applied, errs = sb.apply(resp)
        outs = []
        for name, arg in TOOL_RE.findall(resp)[:6]:
            rc, out = sb.run_tool(name, arg)
            calls.append({"phase": label, "turn": used, "tool": name.lower(), "rc": rc})
            outs.append(f"=== TOOL_OUTPUT: {name} (exit code {rc}) ===\n{out}\n=== END_TOOL_OUTPUT ===")
        note = f"Draft applied to sandbox: {', '.join(applied)}\n" if applied else ""
        note += "".join(f"Not applied: {e}\n" for e in errs) + ("\n" if note or errs else "")
        left = budget - used
        tail = (f"\n\nYou have {left} tool turn(s) left. Call more tools, or finish (final edits, no tool blocks)."
                if left else "\n\nNo tool turns left. Finish: reply with your final edits (if any), no tool blocks.")
        resp = conv.turn(f"{label}_tool_{used}", note + "\n".join(outs) + tail)
    if TOOL_RE.search(resp):
        _, errs = sb.apply(resp)
        resp = conv.turn(f"{label}_forced_final", "Tool budget exhausted; tools were not run. "
                         + "".join(f"Not applied: {e}. " for e in errs)
                         + "Reply with your final edits (if any), no tool blocks.")
    _, errs = sb.apply(resp)
    if errs and edit_fix:
        resp = conv.turn(f"{label}_edit_fix", "".join(f"Not applied: {e}\n" for e in errs)
                         + "Reply with corrected EDIT or FILE blocks for these changes only, no tool blocks.")
        sb.apply(strip_tool_blocks(resp))
    return sb.draft_patch(), used


def confidence_check(conv, with_rule, n, cmap):
    diags = []
    for i in range(n):
        diags.append(parse_diag(conv.turn(f"diag_{i + 1}", diag_prompt(with_rule), keep=False, max_tokens=120)))
    confs = [d["confidence"] for d in diags if d["confidence"] is not None]
    stated = sum(confs) / len(confs) if confs else None
    rcs = {d["root_cause_norm"] for d in diags if d["root_cause_norm"]}
    rules = {d["rule_norm"] for d in diags}
    conflict = len(rcs) > 1 or (with_rule and len(rules) > 1)
    return {"diagnoses": diags, "stated": stated, "calibrated": calibrate(stated, cmap), "conflict": conflict}


def sure_feedback(chk, with_rule):
    lines = ["CONFIDENCE HARNESS REPORT on your current patch:"]
    lines.append(f"- calibrated confidence that it passes the hidden CI tests: {chk['calibrated']:.2f} "
                 f"(stated {chk['stated'] if chk['stated'] is None else round(chk['stated'], 2)}, mapped through "
                 "this model's measured calibration)")
    if chk["conflict"]:
        rc = sorted({d['root_cause'] or '?' for d in chk['diagnoses']})
        lines.append(f"- your repeated diagnoses disagree on the root cause: {rc}")
        if with_rule:
            lines.append(f"- and on the governing convention: {sorted({d['rule_norm'] for d in chk['diagnoses']})}")
    lines.append("This is below the reliability bar. Re-examine the root cause and the failing value: "
                 "reproduce it, consider which behaviour the hidden tests most likely expect, and check edge cases"
                 + (" and the knowledge graph (use the know tool to look up the relevant convention)" if with_rule else "")
                 + f". You have {MAX_TOOL_TURNS - 1} more tool turn(s); then finish with your final edits (no tool blocks).")
    return "\n".join(lines)


def run_attempt(att, cmap):
    arm, fam, tid, r = att["arm"], att["family"], att["task_id"], att["run_idx"]
    out_file = os.path.join(RAW_DIR, f"{arm}_{fam}_t{tid}_r{r}.json")
    if os.path.exists(out_file):
        with open(out_file, encoding="utf-8") as f:
            saved = json.load(f)
        if saved.get("status") == "COMPLETED":
            return saved
    ticket = TASKS_BY_ID[tid]
    prompt, meta = build_first_prompt(arm, ticket)
    src = GRAPH_SOURCE.get(arm)
    conv = Conversation(prompt)
    sb = Sandbox(ticket["repo"], src)
    calls, extra = [], dict(meta)
    try:
        resp = conv.turn("initial")
        patch1, used = tool_loop(conv, sb, resp, MAX_TOOL_TURNS, calls, "solve")
        grade1 = grader.evaluate_patch(ticket["repo"], patch1, ticket["key"])
        final_patch, grade = patch1, grade1
        if arm in SURE_ARMS:
            chk = confidence_check(conv, src is not None, SURE_SAMPLES, cmap)
            extra["sure"] = chk
            extra["revised"] = False
            if chk["conflict"] or chk["calibrated"] < SURE_THRESHOLD:
                extra["revised"] = True
                resp = conv.turn("sure_revise", sure_feedback(chk, src is not None))
                final_patch, used2 = tool_loop(conv, sb, resp, MAX_TOOL_TURNS - 1, calls, "revise")
                grade = grader.evaluate_patch(ticket["repo"], final_patch, ticket["key"])
        elif arm == "B0":
            # post-hoc probe (after submission, does not affect the patch): fits the calibration map
            extra["probe"] = parse_diag(conv.turn("probe", diag_prompt(False), keep=False, max_tokens=120))
        record = {
            "status": "COMPLETED", "arm": arm, "family": fam, "rule_id": FAMILY_TO_RULE[fam], "task_id": tid,
            "run_idx": r, "order_idx": att.get("order_idx"),
            "strict_pass": bool(grade["strict_pass"]), "attempt1_strict_pass": bool(grade1["strict_pass"]),
            "func_pass": bool(grade["func_pass"]), "tamper": bool(grade["tamper"]),
            "violations": grade["violations"], "changed_files": grade["changed_files"],
            "tool_calls": calls, "tools_used": sorted({c["tool"] for c in calls}),
            "model_turns": len(conv.transcript), **conv.tok, "latency_sec": round(conv.latency, 1), **extra,
            "model": llm.MODEL_ID, "sampling": llm.SAMPLING, "final_patch": final_patch,
            "transcript": conv.transcript, "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:  # noqa: BLE001
        record = {"status": "INFRA_FAILURE", "arm": arm, "family": fam, "task_id": tid, "run_idx": r,
                  "error": str(e)[:500], "timestamp": datetime.now(timezone.utc).isoformat()}
    finally:
        sb.cleanup()
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str)
    return record


def family_attempts(fam, n):
    tasks = FAMILY_TASKS[fam]
    return [(tasks[j % len(tasks)], j // len(tasks) + 1) for j in range(n)]


def build_schedule(arms, n, seed):
    """Rounds: round j holds attempt j of every (family, arm) cell, shuffled within the round,
    so stopping after any round leaves a balanced design."""
    rng, sched = random.Random(seed), []
    for j in range(n):
        rnd = [{"arm": a, "family": f, "task_id": family_attempts(f, n)[j][0],
                "run_idx": family_attempts(f, n)[j][1], "round": j + 1} for f in FAMILY_TASKS for a in arms]
        rng.shuffle(rnd)
        sched += rnd
    for i, a in enumerate(sched, 1):
        a["order_idx"] = i
    return sched


def execute(schedule, workers, cmap):
    os.makedirs(RAW_DIR, exist_ok=True)
    lock, st = threading.Lock(), {"n": 0, "k": 0, "bad": 0}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_attempt, a, cmap): a for a in schedule}  # FIFO: earlier rounds first
        for fut in as_completed(futs):
            a, rec = futs[fut], fut.result()
            with lock:
                st["n"] += 1
                st["k"] += int(bool(rec.get("strict_pass")))
                st["bad"] += int(rec.get("status") != "COMPLETED")
                mark = "PASS" if rec.get("strict_pass") else ("INFRA" if rec.get("status") != "COMPLETED" else "FAIL")
                print(f"[{st['n']:4d}/{len(schedule)}] {a['arm']:9s} {a['family']:20s} t{a['task_id']} r{a['run_idx']} "
                      f"-> {mark} ({rec.get('latency_sec', '-')}s)  pass {st['k']} infra {st['bad']}", flush=True)


def load_records():
    out = []
    if os.path.isdir(RAW_DIR):
        for fn in sorted(os.listdir(RAW_DIR)):
            with open(os.path.join(RAW_DIR, fn), encoding="utf-8") as f:
                rec = json.load(f)
            if rec.get("status") == "COMPLETED":
                out.append(rec)
    return out


def write_calibration():
    pairs = [(r["probe"]["confidence"], r["strict_pass"]) for r in load_records()
             if r["arm"] == "B0" and r.get("probe") and r["probe"].get("confidence") is not None]
    cmap = fit_calibration(pairs)
    with open(CALIB_PATH, "w", encoding="utf-8") as f:
        json.dump(cmap, f, indent=2)
    return cmap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["b0", "arms", "calib", "one"])
    ap.add_argument("--n", type=int, default=4, help="attempts per family per arm")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261107)
    ap.add_argument("--arms", default=",".join(ARMS[1:]))
    ap.add_argument("--task", type=int)
    ap.add_argument("--arm", default="B0")
    a = ap.parse_args()
    os.makedirs(RAW_DIR, exist_ok=True)
    if a.stage == "b0":
        execute(build_schedule(["B0"], a.n, a.seed), a.workers, None)
        print(json.dumps(write_calibration(), indent=1))
    elif a.stage == "calib":
        print(json.dumps(write_calibration(), indent=1))
    elif a.stage == "arms":
        cmap = load_calibration()
        if cmap is None:
            sys.exit("run the b0 stage first (calibration map missing)")
        execute(build_schedule(a.arms.split(","), a.n, a.seed + 1), a.workers, cmap)
    else:
        t = TASKS_BY_ID[a.task]
        rec = run_attempt({"arm": a.arm, "family": t["family"], "task_id": a.task, "run_idx": 0}, load_calibration())
        print(json.dumps({k: v for k, v in rec.items() if k not in ("transcript", "final_patch")}, indent=1, default=str))


if __name__ == "__main__":
    main()
