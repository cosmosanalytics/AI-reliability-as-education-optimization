"""Live Agent Evaluation Runner for Software Engineering Reliability Experiments.

Implements the binding REAL_TEST_REQUIREMENTS.md protocol (Round 4 compliant):
- One fresh model session per (cell, run, ticket)
- Live model calls only; raises FATAL error if backend fails or is unconfigured (NO mock fallback)
- Real interactive tool execution loop for u=1 with safe argument validation (rejects flags/traversals)
- Enforces forced final patch submission if tool budget is exhausted (R4-D)
- Tracks whether final patch differs from last tool-tested draft (R4-D)
- max_tokens >= 16k with explicit stop_reason verification; rejects/flags truncated turns (R4-B)
- Structured Self-Review (r) and Automated Retry (k, exactly 1 retry) model turns (R4-F)
- True Resolution-V factorial parity: k+ iff (s+p+u+r) is even in {0,1} coding
- Standardized format instruction envelope on EVERY ticket prompt (outside factor briefs)
- Comprehensive turn-by-turn audit trail: prompts, responses, tool logs, exit codes, stop_reasons
- Lazy/hermetic token counting that functions offline without network access (R4-G)
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
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from grader import evaluate_patch, parse_blocks, run_pytest

# Standardized format header included on EVERY ticket across ALL cells
STANDARD_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

TOOL_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "You have access to an interactive test execution tool (pytest). In your first turn, invoke the test runner "
    "(see INTERACTIVE TEST RUNNER TOOL instructions at bottom). "
    "When ready to submit your final patch, output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

TOOL_INSTRUCTION_ENVELOPE = (
    "\n\nINTERACTIVE TEST RUNNER TOOL:\n"
    "You have access to an interactive test execution tool in your workspace.\n"
    "WORKFLOW REQUIREMENT:\n"
    "In your first turn, you must invoke the test runner to observe test behavior in the repository by outputting:\n"
    "=== TOOL: pytest ===\n"
    "tests/\n"
    "=== END_TOOL ===\n"
    "You will receive the test execution exit code and traceback in the next turn.\n"
    "When you are finished testing and ready to submit your final patch, output ONLY the patch in the standard format:\n"
    "=== FILE: path/to/file ===\n"
    "... complete file content ...\n"
    "=== END ===\n"
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
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


def count_tokens_safe(text):
    """Counts tokens using tiktoken if available; falls back to 4-chars/token if offline."""
    if not text:
        return 0
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(str(text)))
    except Exception:
        # Hermetic offline fallback
        return max(1, len(str(text)) // 4)


class LiveModelBackend:
    """Live model backend interface. Raises FATAL error if live inference fails (zero mocks)."""

    def __init__(self, model_id, temperature=0.0, backend=None):
        self.model_id = model_id
        self.temperature = temperature
        self.backend = backend or self._detect_backend()
        self.last_thoughts_tok = None

    def _detect_backend(self):
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("GEMINI_API_KEY"):
            return "gemini"
        return "unconfigured"

    def count_tokens(self, text):
        return count_tokens_safe(text)

    def startup_self_check(self):
        """Mandatory startup verification: makes one live call to prove backend works before running experiments."""
        print(
            f"Performing startup self-check on backend '{self.backend}' with model '{self.model_id}'..."
        )
        try:
            resp, in_tok, out_tok, resp_id, stop_reason = self.call(
                prompt="Respond with the word 'VERIFIED' and nothing else.",
                system_prompt="You are a test harness probe.",
                history=[],
            )
            if not resp or len(resp.strip()) == 0:
                raise RuntimeError("Empty response received from backend.")
            print(
                f"Startup self-check PASSED: response_id={resp_id}, stop_reason={stop_reason}, tokens=({in_tok} in, {out_tok} out)"
            )
            return True
        except Exception as e:
            raise RuntimeError(
                f"FATAL: Backend self-check failed for backend '{self.backend}', model '{self.model_id}': {e}\n"
                "Live model inference is strictly required. No mock fallbacks are permitted."
            ) from e

    def call(self, prompt, system_prompt, history):
        """Executes live model inference. Raises exception if failed or truncated."""
        if self.backend == "anthropic":
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
            messages = list(history) + [{"role": "user", "content": prompt}]
            kwargs = {
                "model": self.model_id,
                "max_tokens": 16384,
                "temperature": self.temperature,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            res = client.messages.create(**kwargs)
            # Concatenate all text blocks
            resp_text = "".join(
                b.text for b in res.content if getattr(b, "type", "") == "text"
            )
            stop_reason = res.stop_reason or "end_turn"
            if stop_reason == "max_tokens":
                raise RuntimeError(
                    f"FATAL: Response was truncated by provider (stop_reason={stop_reason})."
                )
            return (
                resp_text,
                res.usage.input_tokens,
                res.usage.output_tokens,
                res.id,
                stop_reason,
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
                max_tokens=16384,
            )
            choice = res.choices[0]
            resp_text = choice.message.content or ""
            stop_reason = choice.finish_reason or "stop"
            if stop_reason == "length":
                raise RuntimeError(
                    f"FATAL: Response was truncated by provider (stop_reason={stop_reason})."
                )
            return (
                resp_text,
                res.usage.prompt_tokens,
                res.usage.completion_tokens,
                res.id,
                stop_reason,
            )

        elif self.backend == "gemini":
            from google import genai
            from google.genai import types

            client = getattr(self, "_client", None) or genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            contents = []
            if system_prompt:
                contents.append(f"System Instructions:\n{system_prompt}\n\n")
            for h in history:
                contents.append(f"{h['role'].upper()}: {h['content']}\n")
            contents.append(f"USER: {prompt}\n")
            full_prompt = "".join(contents)

            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=16384,
                thinking_config=types.ThinkingConfig(thinking_budget=2048),
            )
            res = client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=config,
            )
            resp_text = ""
            if getattr(res, "text", None):
                resp_text = res.text
            elif hasattr(res, "candidates") and res.candidates:
                c0 = res.candidates[0]
                content = getattr(c0, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts is not None:
                    resp_text = "".join(
                        getattr(p, "text", "") or "" for p in parts if getattr(p, "text", None)
                    )

            usage = getattr(res, "usage_metadata", None)
            thoughts_tok = (
                getattr(usage, "thoughts_token_count", None)
                if (usage and getattr(usage, "thoughts_token_count", None) is not None)
                else 0
            )
            self.last_thoughts_tok = thoughts_tok or 0

            in_tok = (
                getattr(usage, "prompt_token_count", None)
                if (usage and getattr(usage, "prompt_token_count", None) is not None)
                else None
            )
            if in_tok is None:
                in_tok = self.count_tokens(full_prompt)

            out_tok = (
                getattr(usage, "candidates_token_count", None)
                if (usage and getattr(usage, "candidates_token_count", None) is not None)
                else None
            )
            if out_tok is None:
                out_tok = self.count_tokens(resp_text)

            stop_reason = "STOP"
            if hasattr(res, "candidates") and res.candidates:
                raw_finish = res.candidates[0].finish_reason
                stop_reason = str(raw_finish)
                is_max = False
                if getattr(raw_finish, "name", None) == "MAX_TOKENS":
                    is_max = True
                elif "MAX_TOKENS" in str(raw_finish):
                    is_max = True
                if is_max:
                    raise RuntimeError(
                        f"FATAL: Response truncated by provider (stop_reason={stop_reason})."
                    )
            resp_id = getattr(res, "response_id", None) or f"gemini_{int(time.time())}"
            return (
                resp_text,
                in_tok,
                out_tok,
                resp_id,
                stop_reason,
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

    def run_pytest_command(self, test_paths_raw=None):
        """Executes pytest against visible paths with strict argument validation (R4-E)."""
        t0 = time.time()
        tokens = test_paths_raw.strip().split() if test_paths_raw else []

        # Validate arguments: reject flags ('-') and path traversals ('..')
        invalid_args = []
        safe_paths = []
        for tok in tokens:
            if tok.startswith("-"):
                invalid_args.append(f"Flag rejected: {tok}")
            elif ".." in tok or tok.startswith(("/", "\\")) or ":" in tok:
                invalid_args.append(f"Directory traversal rejected: {tok}")
            else:
                # Check path is relative to workspace
                norm = os.path.normpath(tok).replace("\\", "/")
                safe_paths.append(norm)

        if invalid_args:
            err_msg = (
                "Tool Error: Invalid pytest arguments.\n"
                + "\n".join(invalid_args)
                + "\nSpecify only relative paths to visible test files within the workspace."
            )
            entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "command": f"pytest [rejected: {test_paths_raw}]",
                "exit_code": 2,
                "stdout_stderr": err_msg,
                "elapsed_seconds": 0.0,
            }
            self.tool_log.append(entry)
            return 2, err_msg

        paths_to_run = safe_paths if safe_paths else self.visible_paths
        rc, out = run_pytest(self.workdir, paths_to_run)
        elapsed = time.time() - t0
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "command": f"pytest -q {' '.join(paths_to_run)}",
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
    retry_feedback_mode="policy_plus_visible_pytest",
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
    total_thoughts_tokens = 0
    last_response_id = ""
    last_stop_reason = ""
    last_tool_tested_patch = ""
    tool_budget_exhausted = False

    # 1. Build standardized task prompt (Round 13 E1 Baseline Definition)
    # Per Round 13 E1 ruling: show ALL files in repository (non-test source files + visible tests)
    # plus ticket issue and failing traceback excerpt across all cells.
    # Factor u=1 specifically means "may run tests / interactive tools", not "see the files".
    prompt_files = ticket["repo"]

    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in prompt_files.items()
    )
    envelope_header = (
        TOOL_TASK_ENVELOPE_HEADER if u_val == 1 else STANDARD_TASK_ENVELOPE_HEADER
    )
    tb_section = ""
    if "traceback_text" in ticket and ticket["traceback_text"]:
        tb_section = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n"

    task_prompt = (
        f"{envelope_header}\n\n"
        f"TICKET ISSUE:\n{ticket['issue']}\n\n"
        f"{tb_section}"
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
    resp_text, in_tok, out_tok, resp_id, stop_reason = backend_client.call(
        prompt=current_prompt, system_prompt=brief_text, history=history
    )
    th_tok = getattr(backend_client, "last_thoughts_tok", 0) or 0
    total_tokens_in += in_tok
    total_tokens_out += out_tok
    total_thoughts_tokens += th_tok
    last_response_id = resp_id
    last_stop_reason = stop_reason

    audit_turns.append(
        {
            "turn": 1,
            "type": "initial_generation",
            "prompt": current_prompt,
            "response": resp_text,
            "tokens_in": in_tok,
            "tokens_out": out_tok,
            "thoughts_tokens": th_tok,
            "response_id": resp_id,
            "stop_reason": stop_reason,
        }
    )
    history.append({"role": "user", "content": current_prompt})
    history.append({"role": "assistant", "content": resp_text})

    # Tool interaction loop for u=1
    current_turn = 1
    while u_val == 1 and current_turn <= max_tool_turns:
        tool_match = TOOL_BLOCK_REGEX.search(resp_text)
        if not tool_match:
            break

        tool_used = True
        tool_call_count += 1
        test_paths_arg = tool_match.group(1).strip()

        # Apply draft files to sandbox and save draft
        tool_sandbox.apply_draft(resp_text)
        last_tool_tested_patch = resp_text

        # Run pytest with safe argument validation
        rc, out = tool_sandbox.run_pytest_command(test_paths_arg)

        tool_feedback = (
            f"=== TOOL_OUTPUT (exit code: {rc}) ===\n"
            f"{out}\n"
            f"=== END_TOOL_OUTPUT ===\n\n"
            "If further modifications or tests are needed, output revised tool blocks or file blocks. "
            "When you are finished, output your complete final patch in === FILE === format."
        )

        current_turn += 1
        resp_text, in_tok, out_tok, resp_id, stop_reason = backend_client.call(
            prompt=tool_feedback, system_prompt=brief_text, history=history
        )
        th_tok = getattr(backend_client, "last_thoughts_tok", 0) or 0
        total_tokens_in += in_tok
        total_tokens_out += out_tok
        total_thoughts_tokens += th_tok
        last_response_id = resp_id
        last_stop_reason = stop_reason

        audit_turns.append(
            {
                "turn": current_turn,
                "type": "tool_feedback",
                "tool_cmd": f"pytest {test_paths_arg}",
                "exit_code": rc,
                "prompt": tool_feedback,
                "response": resp_text,
                "tokens_in": in_tok,
                "tokens_out": out_tok,
                "thoughts_tokens": th_tok,
                "response_id": resp_id,
                "stop_reason": stop_reason,
            }
        )
        history.append({"role": "user", "content": tool_feedback})
        history.append({"role": "assistant", "content": resp_text})

    # Tool loop exit handling (R4-D): forced final submission if tool block remains or max turns exhausted
    if u_val == 1 and (
        current_turn > max_tool_turns or TOOL_BLOCK_REGEX.search(resp_text)
    ):
        tool_budget_exhausted = True
        forced_submit_prompt = (
            "You have reached the tool execution limit. "
            "Submit your complete final patch now in the required === FILE: path === ... === END === block format. "
            "Do not output any more tool blocks."
        )
        current_turn += 1
        resp_text, in_tok, out_tok, resp_id, stop_reason = backend_client.call(
            prompt=forced_submit_prompt,
            system_prompt=brief_text,
            history=history,
        )
        th_tok = getattr(backend_client, "last_thoughts_tok", 0) or 0
        total_tokens_in += in_tok
        total_tokens_out += out_tok
        total_thoughts_tokens += th_tok
        last_response_id = resp_id
        last_stop_reason = stop_reason

        audit_turns.append(
            {
                "turn": current_turn,
                "type": "forced_final_submission",
                "prompt": forced_submit_prompt,
                "response": resp_text,
                "tokens_in": in_tok,
                "tokens_out": out_tok,
                "thoughts_tokens": th_tok,
                "response_id": resp_id,
                "stop_reason": stop_reason,
            }
        )
        history.append({"role": "user", "content": forced_submit_prompt})
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
        resp_text, in_tok, out_tok, resp_id, stop_reason = backend_client.call(
            prompt=review_prompt, system_prompt=brief_text, history=history
        )
        th_tok = getattr(backend_client, "last_thoughts_tok", 0) or 0
        total_tokens_in += in_tok
        total_tokens_out += out_tok
        total_thoughts_tokens += th_tok
        last_response_id = resp_id
        last_stop_reason = stop_reason

        audit_turns.append(
            {
                "turn": current_turn,
                "type": "review_step",
                "prompt": review_prompt,
                "response": resp_text,
                "tokens_in": in_tok,
                "tokens_out": out_tok,
                "thoughts_tokens": th_tok,
                "response_id": resp_id,
                "stop_reason": stop_reason,
            }
        )
        history.append({"role": "user", "content": review_prompt})
        history.append({"role": "assistant", "content": resp_text})
        grade_post_review = evaluate_patch(
            ticket["repo"], resp_text, ticket["key"]
        )

    # Step 3: Automated Retry (k=1) - Exactly ONE retry for k_2 (R4-F)
    retries_done = 0
    cur_patch = resp_text
    cur_grade = grade_post_review

    if k_val == 1:
        for retry_num in [1]:  # One retry for k_2 factorial level
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
            resp_text, in_tok, out_tok, resp_id, stop_reason = (
                backend_client.call(
                    prompt=feedback_msg,
                    system_prompt=brief_text,
                    history=history,
                )
            )
            th_tok = getattr(backend_client, "last_thoughts_tok", 0) or 0
            total_tokens_in += in_tok
            total_tokens_out += out_tok
            total_thoughts_tokens += th_tok
            last_response_id = resp_id
            last_stop_reason = stop_reason

            audit_turns.append(
                {
                    "turn": current_turn,
                    "type": f"retry_{retry_num}",
                    "prompt": feedback_msg,
                    "response": resp_text,
                    "tokens_in": in_tok,
                    "tokens_out": out_tok,
                    "thoughts_tokens": th_tok,
                    "response_id": resp_id,
                    "stop_reason": stop_reason,
                }
            )
            history.append({"role": "user", "content": feedback_msg})
            history.append({"role": "assistant", "content": resp_text})

            cur_patch = resp_text
            cur_grade = evaluate_patch(ticket["repo"], cur_patch, ticket["key"])

    final_patch = cur_patch
    grade_final = cur_grade

    # Determine if final patch differs from last tool-tested draft
    patch_differs_from_tool_test = (
        (final_patch.strip() != last_tool_tested_patch.strip())
        if last_tool_tested_patch
        else False
    )

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
        "stop_reason": last_stop_reason,
        "attempt1_strict": grade_att1["strict_pass"],
        "post_review_strict": grade_post_review["strict_pass"],
        "final_strict": grade_final["strict_pass"],
        "func_pass": grade_final["func_pass"],
        "tamper": grade_final["tamper"],
        "retries_done": retries_done,
        "tool_used": tool_used,
        "tool_call_count": tool_call_count,
        "tool_budget_exhausted": tool_budget_exhausted,
        "patch_differs_from_tool_test": patch_differs_from_tool_test,
        "tokens_in": total_tokens_in,
        "tokens_out": total_tokens_out,
        "thoughts_tokens": total_thoughts_tokens,
        "total_billed_tokens": total_tokens_in + total_tokens_out + total_thoughts_tokens,
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
    retry_feedback_mode="policy_plus_visible_pytest",
    output_dir="results/exp",
    frozen_commit_sha="unknown",
    seed=42,
    max_workers=1,
):
    """Executes randomized factorial experiment according to protocol."""
    os.makedirs(output_dir, exist_ok=True)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

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

    schedule = []
    for cell_tuple in cells:
        code, s, p, u, r, k = cell_tuple
        for r_idx in range(1, runs + 1):
            for t in tasks:
                schedule.append((code, s, p, u, r, k, r_idx, t))

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
    existing_keys = set()
    rows_path = os.path.join(output_dir, "rows.json")
    if os.path.exists(rows_path):
        try:
            with open(rows_path, "r", encoding="utf-8") as f:
                existing_rows = json.load(f)
                for er in existing_rows:
                    existing_keys.add((er.get("cell"), er.get("run"), er.get("ticket")))
                    rows.append(er)
            print(f"Resuming experiment: found {len(rows)} previously completed attempts.")
        except Exception:
            rows = []
            existing_keys = set()

    pending = [
        (i, item)
        for i, item in enumerate(schedule)
        if (item[0], item[6], item[7]["id"]) not in existing_keys
    ]
    print(f"Pending attempts to run: {len(pending)}/{len(schedule)} (workers={max_workers})")

    file_lock = threading.Lock()

    def process_attempt(indexed_item):
        i, item = indexed_item
        code, s, p, u, r, k, r_idx, ticket = item
        brief_file = os.path.join(brief_dir, f"{code}.md")
        brief_text = (
            open(brief_file, encoding="utf-8").read()
            if os.path.exists(brief_file)
            else ""
        )

        print(
            f"[{i+1}/{len(schedule)}] Starting cell={code}, run={r_idx}, ticket={ticket['id']}...",
            flush=True,
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

        with file_lock:
            rows.append(res)
            with open(
                os.path.join(output_dir, "rows.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(rows, f, indent=2)
            print(
                f"[{i+1}/{len(schedule)}] Finished cell={code}, run={r_idx}, ticket={ticket['id']}: "
                f"strict={res['final_strict']} (Completed {len(rows)}/{len(schedule)})",
                flush=True,
            )
        return res

    if max_workers > 1 and len(pending) > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_attempt, x) for x in pending]
            for fut in as_completed(futures):
                try:
                    fut.result()
                except Exception as e:
                    print(f"Worker exception: {e}", flush=True)
    else:
        for x in pending:
            process_attempt(x)

    return rows
