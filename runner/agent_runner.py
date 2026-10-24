"""Live Agent Evaluation Runner for Software Engineering Reliability Experiments.

Implements the binding REAL_TEST_REQUIREMENTS.md protocol (Round 3 compliant):
- One fresh model session per (cell, run, ticket)
- Live model calls only; raises FATAL error if backend fails or is unconfigured (NO mock fallback)
- Real interactive tool execution loop for u=1: function calling/tool block with live pytest
- Structured Self-Review (r) and Automated Retry (k) extra model turns with full format preservation
- True Resolution-V factorial parity: k+ iff (s+p+u+r) is even in {0,1} coding
- Standardized format instruction envelope on EVERY ticket prompt (outside factor briefs)
- Comprehensive audit trail: every turn, prompt, response, tool call, exit code, and grade saved
- Randomization with logged seed and schedule order
- Zero reference solution leakage
"""

import argparse
import datetime
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tiktoken

from grader import evaluate_patch, parse_blocks, run_pytest

# Standardized format header included on EVERY ticket across ALL cells to avoid confounding format knowledge with factor briefs
STANDARD_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

TOOL_INSTRUCTION_ENVELOPE = (
    "\n\nINTERACTIVE TEST RUNNER TOOL:\n"
    "You have access to an interactive test execution tool to run visible unit tests in your workspace.\n"
    "To run tests before final submission, output a tool block:\n"
    "=== TOOL: pytest ===\n"
    "tests/\n"
    "=== END_TOOL ===\n"
    "You may include draft === FILE === blocks in the same turn so tests run against your updated code.\n"
    "You will receive the test exit code and traceback. You may run tests multiple times across turns.\n"
    "When you are finished, output your complete final patch in the standard === FILE === block format without any tool blocks."
)

TOOL_BLOCK_REGEX = re.compile(
    r"=== TOOL:\s*pytest\s*===\s*\n(.*?)\n=== END_TOOL ===", re.DOTALL
)


def compute_k_parity(s, p, u, r):
    """Computes k factor level using +/-1 sign parity for Resolution V.

    In {0, 1} coding where 0 => -1 and 1 => +1:
    k = s * p * u * r is +1 iff the number of zeros in (s,p,u,r) is even,
    which is mathematically equivalent to: (s + p + u + r) % 2 == 0.
    """
    return 1 if ((s + p + u + r) % 2 == 0) else 0


class LiveModelBackend:
    """Live model backend interface. Raises FATAL error if live inference fails (zero mocks)."""

    def __init__(self, model_id, temperature=0.0, backend=None):
        self.model_id = model_id
        self.temperature = temperature
        self.backend = backend or self._detect_backend()
        self.enc = tiktoken.get_encoding("cl100k_base")

    def _detect_backend(self):
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("GEMINI_API_KEY"):
            return "gemini"
        # If no key in environment, check if explicit backend requested
        return "unconfigured"

    def count_tokens(self, text):
        return len(self.enc.encode(text))

    def startup_self_check(self):
        """Mandatory startup verification: makes one live call to prove backend works before running experiments."""
        print(
            f"Performing startup self-check on backend '{self.backend}' with model '{self.model_id}'..."
        )
        try:
            resp, in_tok, out_tok, resp_id = self.call(
                prompt="Respond with the word 'VERIFIED' and nothing else.",
                system_prompt="You are a test harness probe.",
                history=[],
            )
            if not resp or len(resp.strip()) == 0:
                raise RuntimeError("Empty response received from backend.")
            print(
                f"Startup self-check PASSED: response_id={resp_id}, tokens=({in_tok} in, {out_tok} out)"
            )
            return True
        except Exception as e:
            raise RuntimeError(
                f"FATAL: Backend self-check failed for backend '{self.backend}', model '{self.model_id}': {e}\n"
                "Live model inference is strictly required. No mock fallbacks are permitted."
            ) from e

    def call(self, prompt, system_prompt, history):
        """Executes live model inference. Raises exception if failed."""
        if self.backend == "anthropic":
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
            messages = list(history) + [{"role": "user", "content": prompt}]
            kwargs = {
                "model": self.model_id,
                "max_tokens": 4096,
                "temperature": self.temperature,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            res = client.messages.create(**kwargs)
            resp_text = res.content[0].text
            return (
                resp_text,
                res.usage.input_tokens,
                res.usage.output_tokens,
                res.id,
            )

        elif self.backend == "openai":
            import openai

            client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history)
            messages.append({"role": "user", "content": prompt})
            res = client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature,
            )
            resp_text = res.choices[0].message.content
            resp_id = res.id
            return (
                resp_text,
                res.usage.prompt_tokens,
                res.usage.completion_tokens,
                resp_id,
            )

        elif self.backend == "gemini":
            from google import genai

            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            # Build history string or contents
            contents = []
            if system_prompt:
                contents.append(f"System Instructions:\n{system_prompt}\n\n")
            for h in history:
                contents.append(f"{h['role'].upper()}: {h['content']}\n")
            contents.append(f"USER: {prompt}\n")
            full_prompt = "".join(contents)
            res = client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=dict(temperature=self.temperature),
            )
            in_tok = self.count_tokens(full_prompt)
            out_tok = self.count_tokens(res.text)
            return (
                res.text,
                in_tok,
                out_tok,
                getattr(res, "response_id", f"gemini_{int(time.time())}"),
            )

        else:
            raise RuntimeError(
                f"FATAL: Model backend '{self.backend}' is not configured or missing API credentials.\n"
                "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY in the environment."
            )


class ToolSandbox:
    """Manages an isolated filesystem workspace copy for interactive pytest execution."""

    def __init__(self, repo_dict, visible_paths):
        self.workdir = tempfile.mkdtemp(prefix="swe_tool_ws_")
        self.visible_paths = visible_paths
        self.tool_log = []
        for path, content in repo_dict.items():
            full = os.path.join(self.workdir, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
        conftest = os.path.join(self.workdir, "conftest.py")
        if not os.path.exists(conftest):
            with open(conftest, "w", encoding="utf-8") as f:
                f.write("")

    def apply_draft(self, patch_text):
        """Applies draft files to the workspace."""
        files, deletes = parse_blocks(patch_text)
        for p, c in files.items():
            full = os.path.join(self.workdir, p)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(c)
        for p in deletes:
            full = os.path.join(self.workdir, p)
            if os.path.exists(full):
                os.remove(full)

    def run_pytest_command(self, test_paths=None):
        """Executes pytest against visible paths and logs all details."""
        t0 = time.time()
        paths = (
            test_paths.strip().split()
            if (test_paths and test_paths.strip())
            else self.visible_paths
        )
        rc, out = run_pytest(self.workdir, paths)
        elapsed = time.time() - t0
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "command": f"pytest -q {' '.join(paths)}",
            "exit_code": rc,
            "stdout_stderr": out,
            "elapsed_seconds": round(elapsed, 3),
        }
        self.tool_log.append(entry)
        return rc, out

    def cleanup(self):
        shutil.rmtree(self.workdir, ignore_errors=True)


def run_single_attempt(
    cell_code,
    s_val,
    p_val,
    u_val,
    r_val,
    k_val,
    run_idx,
    ticket,
    brief_text,
    backend_client,
    frozen_commit_sha="unknown",
    retry_feedback_mode="policy_only",
    raw_dir="results/raw",
    max_tool_turns=5,
):
    """Executes a single session-isolated ticket attempt with complete audit trail."""
    os.makedirs(raw_dir, exist_ok=True)
    t_id = ticket["id"]
    prefix = f"{cell_code}_r{run_idx}_t{t_id}"

    history = []
    audit_turns = []
    tool_sandbox = None
    tool_used = False
    tool_call_count = 0
    total_tokens_in = 0
    total_tokens_out = 0
    last_response_id = ""

    # 1. Build standardized task prompt
    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in ticket["repo"].items()
    )
    task_prompt = (
        f"{STANDARD_TASK_ENVELOPE_HEADER}\n\n"
        f"TICKET ISSUE:\n{ticket['issue']}\n\n"
        f"REPOSITORY FILES:\n{repo_listing}"
    )

    if u_val == 1:
        task_prompt += TOOL_INSTRUCTION_ENVELOPE
        tool_sandbox = ToolSandbox(
            ticket["repo"], ticket["key"].get("visible_paths", ["tests"])
        )

    # Save envelope and brief
    with open(
        os.path.join(raw_dir, f"{prefix}_brief.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(brief_text)
    with open(
        os.path.join(raw_dir, f"{prefix}_envelope_prompt.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(task_prompt)

    # Turn 1: Initial Prompt
    current_prompt = task_prompt
    resp_text, in_tok, out_tok, resp_id = backend_client.call(
        prompt=current_prompt, system_prompt=brief_text, history=history
    )
    total_tokens_in += in_tok
    total_tokens_out += out_tok
    last_response_id = resp_id

    audit_turns.append(
        {
            "turn": 1,
            "type": "initial_generation",
            "prompt": current_prompt,
            "response": resp_text,
            "tokens_in": in_tok,
            "tokens_out": out_tok,
            "response_id": resp_id,
        }
    )
    history.append({"role": "user", "content": current_prompt})
    history.append({"role": "assistant", "content": resp_text})

    # Tool interaction loop for u=1
    current_turn = 1
    while u_val == 1 and current_turn <= max_tool_turns:
        tool_match = TOOL_BLOCK_REGEX.search(resp_text)
        if not tool_match:
            # Model chose not to call tool; proceeds to patch submission
            break

        tool_used = True
        tool_call_count += 1
        test_paths_arg = tool_match.group(1).strip()

        # Apply any draft file edits provided before or with the tool call
        tool_sandbox.apply_draft(resp_text)

        # Run pytest in sandbox
        rc, out = tool_sandbox.run_pytest_command(test_paths_arg)

        tool_feedback = (
            f"=== TOOL_OUTPUT (exit code: {rc}) ===\n"
            f"{out}\n"
            f"=== END_TOOL_OUTPUT ===\n\n"
            "If further modifications or tests are needed, output revised tool blocks or file blocks. "
            "When you are finished, output your complete final patch in === FILE === format."
        )

        current_turn += 1
        resp_text, in_tok, out_tok, resp_id = backend_client.call(
            prompt=tool_feedback, system_prompt=brief_text, history=history
        )
        total_tokens_in += in_tok
        total_tokens_out += out_tok
        last_response_id = resp_id

        audit_turns.append(
            {
                "turn": current_turn,
                "type": "tool_feedback",
                "tool_cmd": f"pytest -q {test_paths_arg}",
                "exit_code": rc,
                "prompt": tool_feedback,
                "response": resp_text,
                "tokens_in": in_tok,
                "tokens_out": out_tok,
                "response_id": resp_id,
            }
        )
        history.append({"role": "user", "content": tool_feedback})
        history.append({"role": "assistant", "content": resp_text})

    # Attempt 1 Patch is the state after generation / tool loop
    att1_patch = resp_text
    grade_att1 = evaluate_patch(ticket["repo"], att1_patch, ticket["key"])

    # Step 2: Self-Review (r=1)
    grade_post_review = grade_att1
    if r_val == 1:
        current_turn += 1
        review_prompt = (
            "Review your unified diff against docstring contracts: "
            "(1) Did you alter any test file? "
            "(2) Are boundary values (empty, zero, negative) handled? "
            "(3) Are raised exception types exact? "
            "(4) Does the patch preserve caller backward compatibility?\n"
            "Reply with your complete final patch in the required === FILE: path === ... === END === block format."
        )
        resp_text, in_tok, out_tok, resp_id = backend_client.call(
            prompt=review_prompt, system_prompt=brief_text, history=history
        )
        total_tokens_in += in_tok
        total_tokens_out += out_tok
        last_response_id = resp_id

        audit_turns.append(
            {
                "turn": current_turn,
                "type": "review_step",
                "prompt": review_prompt,
                "response": resp_text,
                "tokens_in": in_tok,
                "tokens_out": out_tok,
                "response_id": resp_id,
            }
        )
        history.append({"role": "user", "content": review_prompt})
        history.append({"role": "assistant", "content": resp_text})
        grade_post_review = evaluate_patch(
            ticket["repo"], resp_text, ticket["key"]
        )

    # Step 3: Automated Retry (k=1)
    retries_done = 0
    cur_patch = resp_text
    cur_grade = grade_post_review

    if k_val == 1:
        for retry_num in [1, 2]:
            should_retry = False
            feedback_msg = ""

            # Check policy violations (modified protected file)
            protected_viols = [
                v
                for v in cur_grade["violations"]
                if v.startswith("modified protected file")
            ]
            if protected_viols:
                should_retry = True
                p_path = protected_viols[0].replace(
                    "modified protected file: ", ""
                )
                feedback_msg = (
                    f"Policy Check Failed: Unified diff modifies protected file: {p_path}. "
                    "Do not modify test directory files. "
                    "Reply with your complete corrected patch in the required === FILE: path === ... === END === block format."
                )
            elif (
                retry_feedback_mode == "policy_plus_visible_pytest"
                and cur_grade["visible_rc"] != 0
            ):
                should_retry = True
                feedback_msg = (
                    f"Visible Test Failure (exit code {cur_grade['visible_rc']}):\n"
                    f"{cur_grade['visible_output']}\n"
                    "Reply with your complete corrected patch in the required === FILE: path === ... === END === block format."
                )

            if not should_retry:
                break

            retries_done += 1
            current_turn += 1
            resp_text, in_tok, out_tok, resp_id = backend_client.call(
                prompt=feedback_msg, system_prompt=brief_text, history=history
            )
            total_tokens_in += in_tok
            total_tokens_out += out_tok
            last_response_id = resp_id

            audit_turns.append(
                {
                    "turn": current_turn,
                    "type": f"retry_{retry_num}",
                    "prompt": feedback_msg,
                    "response": resp_text,
                    "tokens_in": in_tok,
                    "tokens_out": out_tok,
                    "response_id": resp_id,
                }
            )
            history.append({"role": "user", "content": feedback_msg})
            history.append({"role": "assistant", "content": resp_text})

            cur_patch = resp_text
            cur_grade = evaluate_patch(ticket["repo"], cur_patch, ticket["key"])

    final_patch = cur_patch
    grade_final = cur_grade

    # Save all audit artifacts
    for turn_info in audit_turns:
        t_idx = turn_info["turn"]
        with open(
            os.path.join(raw_dir, f"{prefix}_turn{t_idx}_prompt.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(turn_info["prompt"])
        with open(
            os.path.join(raw_dir, f"{prefix}_turn{t_idx}_resp.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(turn_info["response"])

    with open(
        os.path.join(raw_dir, f"{prefix}_final_patch.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(final_patch)
    with open(
        os.path.join(raw_dir, f"{prefix}.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(final_patch)

    with open(
        os.path.join(raw_dir, f"{prefix}_grade_attempt1.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(grade_att1, f, indent=2)
    with open(
        os.path.join(raw_dir, f"{prefix}_grade_post_review.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(grade_post_review, f, indent=2)
    with open(
        os.path.join(raw_dir, f"{prefix}_grade_final.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(grade_final, f, indent=2)

    tool_log_entries = []
    if tool_sandbox:
        tool_log_entries = tool_sandbox.tool_log
        with open(
            os.path.join(raw_dir, f"{prefix}_tool_log.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(tool_log_entries, f, indent=2)
        tool_sandbox.cleanup()

    with open(
        os.path.join(raw_dir, f"{prefix}_transcript.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(audit_turns, f, indent=2)

    # Compute brief file hash
    brief_sha256 = hashlib.sha256(brief_text.encode("utf-8")).hexdigest()

    return {
        "cell": cell_code,
        "s": s_val,
        "p": p_val,
        "u": u_val,
        "r": r_val,
        "k": k_val,
        "run": run_idx,
        "ticket": t_id,
        "frozen_commit_sha": frozen_commit_sha,
        "backend": backend_client.backend,
        "model_id": backend_client.model_id,
        "temperature": backend_client.temperature,
        "brief_sha256": brief_sha256,
        "response_id": last_response_id,
        "attempt1_strict": grade_att1["strict_pass"],
        "post_review_strict": grade_post_review["strict_pass"],
        "final_strict": grade_final["strict_pass"],
        "func_pass": grade_final["func_pass"],
        "tamper": grade_final["tamper"],
        "retries_done": retries_done,
        "tool_used": tool_used,
        "tool_call_count": tool_call_count,
        "tokens_in": total_tokens_in,
        "tokens_out": total_tokens_out,
        "violations": grade_final["violations"],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def run_experiment(
    tasks,
    brief_dir="briefs",
    cells=None,
    runs=5,
    model_id="claude-3-7-sonnet-20250219",
    backend=None,
    temperature=0.0,
    retry_feedback_mode="policy_only",
    output_dir="results/exp",
    frozen_commit_sha="unknown",
    seed=42,
):
    """Executes randomized factorial experiment according to protocol."""
    os.makedirs(output_dir, exist_ok=True)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # Initialize and verify live backend
    client = LiveModelBackend(
        model_id=model_id, temperature=temperature, backend=backend
    )
    client.startup_self_check()

    if cells is None:
        cells = [
            (f"C{s}{p}{u}{r}", s, p, u, r, compute_k_parity(s, p, u, r))
            for s in [0, 1]
            for p in [0, 1]
            for u in [0, 1]
            for r in [0, 1]
        ]

    # Build randomized schedule
    schedule = []
    for cell_tuple in cells:
        code, s, p, u, r, k = cell_tuple
        for r_idx in range(1, runs + 1):
            for t in tasks:
                schedule.append((code, s, p, u, r, k, r_idx, t))

    # Seed RNG and shuffle
    random.seed(seed)
    random.shuffle(schedule)

    schedule_log = {
        "seed": seed,
        "frozen_commit_sha": frozen_commit_sha,
        "model_id": model_id,
        "backend": client.backend,
        "temperature": temperature,
        "total_attempts": len(schedule),
        "schedule": [
            {
                "idx": i,
                "cell": item[0],
                "run": item[6],
                "ticket": item[7]["id"],
                "s": item[1],
                "p": item[2],
                "u": item[3],
                "r": item[4],
                "k": item[5],
            }
            for i, item in enumerate(schedule)
        ],
    }
    with open(
        os.path.join(output_dir, "schedule_order.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(schedule_log, f, indent=2)

    rows = []
    for i, item in enumerate(schedule):
        code, s, p, u, r, k, r_idx, ticket = item
        brief_file = os.path.join(brief_dir, f"{code}.md")
        brief_text = (
            open(brief_file, encoding="utf-8").read()
            if os.path.exists(brief_file)
            else ""
        )

        res = run_single_attempt(
            cell_code=code,
            s_val=s,
            p_val=p,
            u_val=u,
            r_val=r,
            k_val=k,
            run_idx=r_idx,
            ticket=ticket,
            brief_text=brief_text,
            backend_client=client,
            frozen_commit_sha=frozen_commit_sha,
            retry_feedback_mode=retry_feedback_mode,
            raw_dir=raw_dir,
        )
        res["order_idx"] = i
        rows.append(res)

        with open(
            os.path.join(output_dir, "rows.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(rows, f, indent=2)

    return rows
