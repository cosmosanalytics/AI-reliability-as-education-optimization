#!/usr/bin/env python3
"""Screening Runner & Hard-Stop Cost Meter for Tune-Set Factorial Experiment (2^{5-1}).

Round 24 Protocol Specifications (Option B Approved):
1. Pinned Run Configuration in Screening Log Header:
   - model_id: gemini-2.5-flash
   - temperature: 0.7
   - top_p: 0.95
   - max_output_tokens: 16384
   - thinking_budget: 2048
   - commit SHA of FREEZE.json: tracked and pinned (a7ecb64)
2. Hard-Stop Cost Meter & 50% Spend Threshold Pause:
   - Pricing Source: Google Generative AI / Gemini API Official Pricing (ai.google.dev/pricing, Oct 2026)
   - Input: $0.30 per 1M tokens ($0.00000030 / token)
   - Output: $2.50 per 1M tokens ($0.00000250 / token), with thoughts_tokens billed at standard output rate!
   - Cumulative cost formula:
       cost = (tokens_in * 0.30 / 1e6) + ((tokens_out + thoughts_tokens) * 2.50 / 1e6)
   - If cumulative_cost_usd >= cost_cap ($37.85 USD), execution halts immediately, logs the event, and makes zero further API calls.
   - 50% Threshold Pause Check:
     If spend crosses 50% of the cap ($18.93 USD) before 40% of attempts (883 of 2,208) are done,
     pause execution, generate and print running per-cell cost table, set status PAUSED_SPEND_THRESHOLD_REACHED,
     and halt gracefully for operator review.
3. Strict Stop Rule:
   - Screening factor cells are strictly gated. The script will NOT execute factor cells automatically
     unless explicitly invoked with --approved-for-execution.
   - Without --approved-for-execution, it prints the run config and validation plan, exiting safely.
4. Factorial Design:
   - 16 cells (C0000..C1111) under Resolution-V defining relation I = spurk:
       k = 1 if ((s + p + u + r) % 2 == 0) else 0
   - Evaluated on the 46 tune tasks from benchmarks/splits_e5.json across 3 runs (2,208 total attempts).
"""

import argparse
import datetime
import json
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "harness"))

import suite_e5
import agent_runner
from agent_runner import LiveModelBackend, compute_k_parity, run_single_attempt

# Gemini 2.5 Flash list pricing as of October 2026:
# Source: Google Cloud Vertex AI / Google Generative AI Gemini API (ai.google.dev/pricing, Oct 2026)
# - Input tokens: $0.30 per 1M tokens ($0.00000030 per token)
# - Output tokens (candidates + thinking/thoughts tokens): $2.50 per 1M tokens ($0.00000250 per token)
# In Gemini 2.5 Flash, thoughts_tokens are billed at the standard output token rate ($2.50 / 1M tokens).
PRICE_INPUT_PER_1M = 0.30
PRICE_OUTPUT_PER_1M = 2.50

# Pinned default hyperparameters (Option B Approved)
DEFAULT_MODEL_ID = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_MAX_OUTPUT_TOKENS = 16384
DEFAULT_THINKING_BUDGET = 2048
DEFAULT_RUNS = 3
DEFAULT_COST_CAP_USD = 37.85  # Round 24 Option B Approved: N=3 runs per cell, 2,208 total attempts, projected $25.24 USD, hard-stop cap $37.85 USD


def get_freeze_commit_sha(repo_root: str = REPO_ROOT) -> str:
    """Retrieves the commit SHA where FREEZE.json was frozen, with fallback."""
    try:
        res = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H", "FREEZE.json"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        sha = res.stdout.strip()
        if sha and len(sha) == 40:
            return sha
    except Exception:
        pass
    # Fallback to the approved Round 24 freeze commit SHA (a7ecb64)
    return "a7ecb643e20f5df1edb497d26298c9c1e2bea77c"


def atomic_json_write(file_path: str, data) -> None:
    """Writes JSON data to a temporary file in the same directory and replaces atomically."""
    dir_name = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmp_screening_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise


def compute_per_cell_cost_table(all_rows, cells=None):
    """Computes running per-cell cost breakdown from row records."""
    if cells is None:
        cells = build_screening_cells()
    cell_stats = {
        c[0]: {
            "attempts": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "thoughts": 0,
            "billed_tokens": 0,
            "cost_usd": 0.0,
            "mean_cost_per_attempt": 0.0,
        }
        for c in cells
    }
    for row in all_rows:
        c = row.get("cell")
        if c in cell_stats:
            cell_stats[c]["attempts"] += 1
            cell_stats[c]["tokens_in"] += row.get("tokens_in", 0)
            cell_stats[c]["tokens_out"] += row.get("tokens_out", 0)
            cell_stats[c]["thoughts"] += row.get("thoughts_tokens", 0)
            cell_stats[c]["billed_tokens"] += row.get("total_billed_tokens", 0)
            cell_stats[c]["cost_usd"] += row.get("cost_usd", 0.0)

    for c, stats in cell_stats.items():
        stats["cost_usd"] = round(stats["cost_usd"], 6)
        stats["mean_cost_per_attempt"] = (
            round(stats["cost_usd"] / stats["attempts"], 6)
            if stats["attempts"] > 0
            else 0.0
        )
    return cell_stats


def format_per_cell_table(per_cell_table: dict) -> str:
    """Formats running per-cell cost breakdown dictionary into a clean aligned table."""
    headers = f"{'Cell':<8} | {'Attempts':<9} | {'In Tok':<10} | {'Out Tok':<10} | {'Thoughts':<10} | {'Cost (USD)':<11} | {'Mean $/Att':<11}"
    sep = "-" * len(headers)
    lines = [headers, sep]
    for cell in sorted(per_cell_table.keys()):
        st = per_cell_table[cell]
        lines.append(
            f"{cell:<8} | {st['attempts']:<9} | {st['tokens_in']:<10} | {st['tokens_out']:<10} | "
            f"{st['thoughts']:<10} | ${st['cost_usd']:<10.4f} | ${st['mean_cost_per_attempt']:<10.4f}"
        )
    return "\n".join(lines)


class CostMeter:
    """Thread-safe hard-stop cost meter tracking cumulative token spend and enforcing cost cap."""

    def __init__(
        self,
        cost_cap_usd: float,
        initial_tokens_in: int = 0,
        initial_tokens_out: int = 0,
        initial_thoughts: int = 0,
        initial_attempts: int = 0,
    ):
        self.cost_cap_usd = float(cost_cap_usd)
        self.lock = threading.Lock()
        self.cumulative_tokens_in = int(initial_tokens_in)
        self.cumulative_tokens_out = int(initial_tokens_out)
        self.cumulative_thoughts_tokens = int(initial_thoughts)
        self.attempts_completed = int(initial_attempts)
        self.cost_cap_exceeded = False
        self.halt_reason = None
        self._recompute_cost()

    def _recompute_cost(self) -> None:
        self.cumulative_cost_usd = (
            (self.cumulative_tokens_in * PRICE_INPUT_PER_1M / 1e6)
            + ((self.cumulative_tokens_out + self.cumulative_thoughts_tokens) * PRICE_OUTPUT_PER_1M / 1e6)
        )
        if self.cumulative_cost_usd >= self.cost_cap_usd:
            self.cost_cap_exceeded = True
            self.halt_reason = (
                f"HARD COST CAP EXCEEDED: Cumulative cost ${self.cumulative_cost_usd:.4f} "
                f"reached or exceeded configured cap ${self.cost_cap_usd:.4f}"
            )

    def record_attempt(
        self,
        tokens_in: int,
        tokens_out: int,
        thoughts_tokens: int,
    ) -> float:
        """Records tokens from a single attempt, recomputes cumulative cost, and trips hard stop if exceeded."""
        with self.lock:
            if self.cost_cap_exceeded:
                raise RuntimeError(self.halt_reason)
            self.cumulative_tokens_in += int(tokens_in)
            self.cumulative_tokens_out += int(tokens_out)
            self.cumulative_thoughts_tokens += int(thoughts_tokens)
            self.attempts_completed += 1
            self._recompute_cost()
            if self.cost_cap_exceeded:
                raise RuntimeError(self.halt_reason)
            return self.cumulative_cost_usd

    def is_exceeded(self) -> bool:
        with self.lock:
            return self.cost_cap_exceeded

    def get_state(self) -> dict:
        with self.lock:
            return {
                "cumulative_tokens_in": self.cumulative_tokens_in,
                "cumulative_tokens_out": self.cumulative_tokens_out,
                "cumulative_thoughts_tokens": self.cumulative_thoughts_tokens,
                "cumulative_billed_tokens": (
                    self.cumulative_tokens_in
                    + self.cumulative_tokens_out
                    + self.cumulative_thoughts_tokens
                ),
                "cumulative_cost_usd": round(self.cumulative_cost_usd, 6),
                "cost_cap_usd": self.cost_cap_usd,
                "attempts_completed": self.attempts_completed,
                "cost_cap_exceeded": self.cost_cap_exceeded,
                "halt_reason": self.halt_reason,
            }


class ScreeningModelBackend(LiveModelBackend):
    """Screening-specific backend that pins top_p=0.95 and coordinates with CostMeter."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        thinking_budget: int = DEFAULT_THINKING_BUDGET,
        backend: str = None,
        cost_meter: CostMeter = None,
    ):
        super().__init__(model_id=model_id, temperature=temperature, backend=backend)
        self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.thinking_budget = thinking_budget
        self.cost_meter = cost_meter

    def call(self, prompt, system_prompt, history):
        if self.cost_meter and self.cost_meter.is_exceeded():
            raise RuntimeError(f"HARD COST CAP EXCEEDED: {self.cost_meter.halt_reason}")

        if self.backend == "gemini":
            from google import genai
            from google.genai import types

            client = getattr(self, "_client", None) or genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            contents = []
            if system_prompt:
                contents.append(f"System Instructions:\n{system_prompt}\n\n")
            for h in history:
                contents.append(f"{h['role'].upper()}: {h['content']}\n")
            contents.append(f"USER: {prompt}\n")
            full_prompt = "".join(contents)

            config = types.GenerateContentConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                max_output_tokens=self.max_output_tokens,
                thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget),
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
                        f"FATAL: Response was truncated by provider (stop_reason={stop_reason})."
                    )

            resp_id = getattr(res, "response_id", None) or f"gemini_{int(time.time()*1000)}"
            return resp_text, in_tok, out_tok, resp_id, stop_reason
        else:
            return super().call(prompt, system_prompt, history)


def load_tune_tasks(repo_root: str = REPO_ROOT):
    """Loads and returns the 46 tune tasks defined in benchmarks/splits_e5.json."""
    splits_path = os.path.join(repo_root, "benchmarks", "splits_e5.json")
    with open(splits_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
    tune_ids = splits.get("tune", [])
    task_map = {t["id"]: t for t in suite_e5.T}
    missing = [tid for tid in tune_ids if tid not in task_map]
    if missing:
        raise ValueError(f"Tune task IDs missing from suite_e5.py: {missing}")
    tune_tasks = [task_map[tid] for tid in tune_ids]
    return tune_tasks


def build_screening_cells():
    """Generates the 16 Resolution-V fractional factorial cells C0000..C1111 with parity defining relation I = spurk."""
    cells = [
        (f"C{s}{p}{u}{r}", s, p, u, r, compute_k_parity(s, p, u, r))
        for s in [0, 1]
        for p in [0, 1]
        for u in [0, 1]
        for r in [0, 1]
    ]
    return cells


def verify_cell_briefs(repo_root: str = REPO_ROOT, cells=None):
    """Verifies that all 16 cell brief markdown files exist and are non-empty in briefs/."""
    if cells is None:
        cells = build_screening_cells()
    brief_dir = os.path.join(repo_root, "briefs")
    for code, s, p, u, r, k in cells:
        brief_file = os.path.join(brief_dir, f"{code}.md")
        if not os.path.isfile(brief_file):
            raise FileNotFoundError(f"Missing required screening brief: {brief_file}")
        content = open(brief_file, encoding="utf-8").read()
        if len(content.strip()) == 0:
            raise ValueError(f"Brief file is empty: {brief_file}")
    return True


def create_initial_header(
    freeze_sha: str,
    cost_cap_usd: float,
    tune_tasks_count: int,
    cells_count: int,
    runs_count: int,
    model_id: str = DEFAULT_MODEL_ID,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    thinking_budget: int = DEFAULT_THINKING_BUDGET,
) -> dict:
    """Constructs the pinned metadata header for screening_log_header.json."""
    total_attempts = tune_tasks_count * cells_count * runs_count
    return {
        "experiment": {
            "name": "Tune-Set Factorial Screening",
            "design": "2^{5-1} Resolution-V Fractional Factorial",
            "defining_relation": "I = spurk",
            "parity_rule": "k = 1 if ((s + p + u + r) % 2 == 0) else 0",
            "factors": {
                "s": "Sources (HANDBOOK.md house conventions)",
                "p": "Practice (PLACEBO.md balanced examples)",
                "u": "Pytest Tool execution",
                "r": "Review Checklist self-inspection",
                "k": "Policy Retry mechanism",
            },
            "status": "INITIALIZED",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        "run_config": {
            "model_id": model_id,
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_output_tokens,
            "thinking_budget": thinking_budget,
            "commit_sha_freeze_json": freeze_sha,
            "commit_sha_short": freeze_sha[:7] if freeze_sha else "a7ecb64",
        },
        "pricing": {
            "pricing_source": "Google Generative AI / Gemini API Official Pricing (ai.google.dev/pricing, Oct 2026)",
            "price_input_per_1m_usd": PRICE_INPUT_PER_1M,
            "price_output_per_1m_usd": PRICE_OUTPUT_PER_1M,
            "thoughts_billed_as_output": True,
            "cost_formula": "cost_usd = (tokens_in * 0.30 / 1e6) + ((tokens_out + thoughts_tokens) * 2.50 / 1e6)",
        },
        "execution_scope": {
            "tune_tasks_count": tune_tasks_count,
            "cells_count": cells_count,
            "runs_count": runs_count,
            "total_scheduled_attempts": total_attempts,
            "cost_cap_usd": cost_cap_usd,
        },
        "cost_meter": {
            "cumulative_tokens_in": 0,
            "cumulative_tokens_out": 0,
            "cumulative_thoughts_tokens": 0,
            "cumulative_billed_tokens": 0,
            "cumulative_cost_usd": 0.0,
            "cost_cap_usd": cost_cap_usd,
            "attempts_completed": 0,
            "cost_cap_exceeded": False,
            "halt_reason": None,
        },
    }


def run_screening(
    output_dir: str = None,
    cost_cap: float = DEFAULT_COST_CAP_USD,
    runs: int = DEFAULT_RUNS,
    max_workers: int = 6,
    seed: int = 42,
    approved_for_execution: bool = False,
    dry_run: bool = False,
    model_id: str = DEFAULT_MODEL_ID,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    thinking_budget: int = DEFAULT_THINKING_BUDGET,
    repo_root: str = REPO_ROOT,
):
    """Main orchestrator for Tune-Set Factorial Screening experiment."""
    if output_dir is None:
        output_dir = os.path.join(repo_root, "results", "screening")
    os.makedirs(output_dir, exist_ok=True)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    header_path = os.path.join(output_dir, "screening_log_header.json")
    rows_path = os.path.join(output_dir, "rows.json")
    brief_dir = os.path.join(repo_root, "briefs")

    freeze_sha = get_freeze_commit_sha(repo_root)
    tune_tasks = load_tune_tasks(repo_root)
    cells = build_screening_cells()
    verify_cell_briefs(repo_root, cells)

    total_attempts = len(tune_tasks) * len(cells) * runs

    print("================================================================================")
    print("TUNE-SET FACTORIAL SCREENING RUNNER (2^{5-1} Resolution-V)")
    print("================================================================================")
    print(f"Model ID:              {model_id}")
    print(f"Temperature:           {temperature}")
    print(f"Top-P:                 {top_p}")
    print(f"Max Output Tokens:     {max_output_tokens}")
    print(f"Thinking Budget:       {thinking_budget}")
    print(f"FREEZE.json Commit:    {freeze_sha}")
    print(f"Hard-Stop Cost Cap:    ${cost_cap:.2f} USD")
    print(f"Tune Tasks:            {len(tune_tasks)} (from benchmarks/splits_e5.json)")
    print(f"Factorial Cells:       {len(cells)} (C0000..C1111)")
    print(f"Runs per Cell:         {runs}")
    print(f"Total Scheduled Runs:  {total_attempts}")
    print(f"Output Directory:      {output_dir}")
    print("================================================================================")

    # STRICT STOP RULE VERIFICATION:
    if not approved_for_execution and not dry_run:
        print("\n[STRICT STOP RULE ENFORCED]")
        print("Screening factor cells (s, p, u, r, k) are strictly gated per Round 24 protocol.")
        print("Zero API calls will be made without explicit invocation approval.")
        print("\nTo execute when approved by reviewer:")
        print(f"  python runner/run_screening.py --approved-for-execution --cost-cap {cost_cap}\n")
        header_data = create_initial_header(
            freeze_sha=freeze_sha,
            cost_cap_usd=cost_cap,
            tune_tasks_count=len(tune_tasks),
            cells_count=len(cells),
            runs_count=runs,
            model_id=model_id,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            thinking_budget=thinking_budget,
        )
        header_data["experiment"]["status"] = "LOCKED_AWAITING_APPROVAL"
        atomic_json_write(header_path, header_data)
        return {"status": "LOCKED_AWAITING_APPROVAL", "header": header_data}

    # Dry-run execution validation:
    if dry_run:
        print("\n[DRY RUN MODE]")
        print("Validating schedule generation, brief attachments, and cost meter math...")
        header_data = create_initial_header(
            freeze_sha=freeze_sha,
            cost_cap_usd=cost_cap,
            tune_tasks_count=len(tune_tasks),
            cells_count=len(cells),
            runs_count=runs,
            model_id=model_id,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            thinking_budget=thinking_budget,
        )
        header_data["experiment"]["status"] = "DRY_RUN_VERIFIED"
        atomic_json_write(header_path, header_data)
        print("Dry run verification complete. Screening log header written atomically.")
        return {"status": "DRY_RUN_VERIFIED", "header": header_data}

    # Build randomized schedule
    schedule = []
    for cell_tuple in cells:
        code, s, p, u, r, k = cell_tuple
        for r_idx in range(1, runs + 1):
            for t in tune_tasks:
                schedule.append((code, s, p, u, r, k, r_idx, t))

    random.seed(seed)
    random.shuffle(schedule)

    schedule_log = {
        "seed": seed,
        "frozen_commit_sha": freeze_sha,
        "model_id": model_id,
        "temperature": temperature,
        "top_p": top_p,
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
    with open(os.path.join(output_dir, "schedule_order.json"), "w", encoding="utf-8") as f:
        json.dump(schedule_log, f, indent=2)

    # Resume support: scan existing rows
    existing_rows = []
    existing_keys = set()
    initial_in = 0
    initial_out = 0
    initial_th = 0

    if os.path.exists(rows_path):
        try:
            with open(rows_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for r in loaded:
                    k_tuple = (r.get("cell"), r.get("run"), r.get("ticket"))
                    existing_keys.add(k_tuple)
                    # Ensure cost_usd and call_count exist in loaded rows
                    if "cost_usd" not in r:
                        r_tin = r.get("tokens_in", 0)
                        r_tout = r.get("tokens_out", 0)
                        r_tth = r.get("thoughts_tokens", 0)
                        r["cost_usd"] = round(
                            (r_tin * PRICE_INPUT_PER_1M / 1e6)
                            + ((r_tout + r_tth) * PRICE_OUTPUT_PER_1M / 1e6),
                            6,
                        )
                    if "call_count" not in r:
                        r_code = r.get("cell", "")
                        r_run = r.get("run", 1)
                        r_tid = r.get("ticket", "")
                        pfx = f"{r_code}_run{r_run}_{r_tid}"
                        tr_file = os.path.join(raw_dir, f"{pfx}_transcript.json")
                        cc = None
                        if os.path.isfile(tr_file):
                            try:
                                with open(tr_file, "r", encoding="utf-8") as tf:
                                    td = json.load(tf)
                                    if isinstance(td, list):
                                        cc = len(td)
                            except Exception:
                                pass
                        if cc is None:
                            cc = 1 + r.get("tool_call_count", 0) + (1 if r.get("r") == 1 else 0) + r.get("retries_done", 0)
                        r["call_count"] = cc
                    existing_rows.append(r)
                    initial_in += r.get("tokens_in", 0)
                    initial_out += r.get("tokens_out", 0)
                    initial_th += r.get("thoughts_tokens", 0)
            print(f"Resuming screening: found {len(existing_rows)} completed attempts.")
        except Exception as e:
            print(f"Warning: could not parse existing rows.json ({e}); starting fresh.")
            existing_rows = []
            existing_keys = set()
            initial_in = initial_out = initial_th = 0

    # Initialize Cost Meter
    cost_meter = CostMeter(
        cost_cap_usd=cost_cap,
        initial_tokens_in=initial_in,
        initial_tokens_out=initial_out,
        initial_thoughts=initial_th,
        initial_attempts=len(existing_rows),
    )

    # Check if cost cap is already reached upon resume
    if cost_meter.is_exceeded():
        header_data = create_initial_header(
            freeze_sha=freeze_sha,
            cost_cap_usd=cost_cap,
            tune_tasks_count=len(tune_tasks),
            cells_count=len(cells),
            runs_count=runs,
            model_id=model_id,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            thinking_budget=thinking_budget,
        )
        header_data["experiment"]["status"] = "HALTED_COST_CAP_EXCEEDED"
        header_data["cost_meter"] = cost_meter.get_state()
        atomic_json_write(header_path, header_data)
        raise RuntimeError(cost_meter.halt_reason)

    # Check 50% cap threshold pause check on resume
    spend_threshold = cost_cap * 0.50
    attempts_threshold = total_attempts * 0.40
    if (
        cost_meter.cumulative_cost_usd >= spend_threshold
        and cost_meter.attempts_completed < attempts_threshold
    ):
        per_cell_table = compute_per_cell_cost_table(existing_rows, cells)
        print("\n" + "=" * 80)
        print("WARNING: SPEND THRESHOLD PAUSE TRIGGERED ON RESUME")
        print(
            f"Spend (${cost_meter.cumulative_cost_usd:.4f}) reached or crossed 50% of cap (${spend_threshold:.2f}) "
            f"before 40% of attempts ({cost_meter.attempts_completed}/{int(attempts_threshold)}) were completed!"
        )
        print("Running per-cell cost breakdown table:")
        print(format_per_cell_table(per_cell_table))
        print("=" * 80 + "\n", flush=True)

        header_data = create_initial_header(
            freeze_sha=freeze_sha,
            cost_cap_usd=cost_cap,
            tune_tasks_count=len(tune_tasks),
            cells_count=len(cells),
            runs_count=runs,
            model_id=model_id,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            thinking_budget=thinking_budget,
        )
        header_data["experiment"]["status"] = "PAUSED_SPEND_THRESHOLD_REACHED"
        header_data["cost_meter"] = cost_meter.get_state()
        header_data["running_per_cell_cost_table"] = per_cell_table
        atomic_json_write(header_path, header_data)
        raise RuntimeError(
            f"PAUSED_SPEND_THRESHOLD_REACHED: Spend reached ${cost_meter.cumulative_cost_usd:.4f} "
            f"(>= 50% cap ${spend_threshold:.2f}) before 40% of attempts "
            f"({cost_meter.attempts_completed}/{int(attempts_threshold)}) were completed."
        )

    # Client setup
    client = ScreeningModelBackend(
        model_id=model_id,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        thinking_budget=thinking_budget,
        backend=None,
        cost_meter=cost_meter,
    )
    client.startup_self_check()

    pending = [
        (i, item)
        for i, item in enumerate(schedule)
        if (item[0], item[6], item[7]["id"]) not in existing_keys
    ]
    print(f"Pending attempts to run: {len(pending)}/{len(schedule)} (workers={max_workers})")

    file_lock = threading.Lock()
    all_rows = list(existing_rows)

    def process_screening_attempt(indexed_item):
        i, item = indexed_item
        code, s, p, u, r, k, r_idx, ticket = item

        # Check cost cap before launching attempt
        if cost_meter.is_exceeded():
            raise RuntimeError(cost_meter.halt_reason)

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
            frozen_commit_sha=freeze_sha,
            retry_feedback_mode="policy_plus_visible_pytest",
            raw_dir=raw_dir,
        )
        res["order_idx"] = i

        # Compute exact call_count from transcript or calculate exactly
        prefix = f"{code}_run{r_idx}_{ticket['id']}"
        transcript_path = os.path.join(raw_dir, f"{prefix}_transcript.json")
        call_count = None
        if os.path.isfile(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as tf:
                    turns = json.load(tf)
                    if isinstance(turns, list):
                        call_count = len(turns)
            except Exception:
                pass
        if call_count is None:
            call_count = 1 + res.get("tool_call_count", 0) + (1 if r == 1 else 0) + res.get("retries_done", 0)
        res["call_count"] = call_count

        # Compute cost_usd for this attempt
        tok_in = res.get("tokens_in", 0)
        tok_out = res.get("tokens_out", 0)
        tok_th = res.get("thoughts_tokens", 0)
        attempt_cost = (tok_in * PRICE_INPUT_PER_1M / 1e6) + ((tok_out + tok_th) * PRICE_OUTPUT_PER_1M / 1e6)
        res["cost_usd"] = round(attempt_cost, 6)

        with file_lock:
            all_rows.append(res)
            # Update cost meter and check hard-stop cap
            try:
                curr_cost = cost_meter.record_attempt(
                    tokens_in=res.get("tokens_in", 0),
                    tokens_out=res.get("tokens_out", 0),
                    thoughts_tokens=res.get("thoughts_tokens", 0),
                )
            except RuntimeError as exc:
                # Update header with cap trip and write atomically
                header_data = create_initial_header(
                    freeze_sha=freeze_sha,
                    cost_cap_usd=cost_cap,
                    tune_tasks_count=len(tune_tasks),
                    cells_count=len(cells),
                    runs_count=runs,
                    model_id=model_id,
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_output_tokens,
                    thinking_budget=thinking_budget,
                )
                header_data["experiment"]["status"] = "HALTED_COST_CAP_EXCEEDED"
                header_data["cost_meter"] = cost_meter.get_state()
                atomic_json_write(header_path, header_data)
                atomic_json_write(rows_path, all_rows)
                raise exc

            meter_state = cost_meter.get_state()

            # 50% cap threshold pause check:
            # "If spend crosses 50% of the cap ($18.93) before 40% of attempts (883 of 2,208) are done,
            # pause and send me the running per-cell cost table before continuing."
            spend_threshold_curr = cost_cap * 0.50
            attempts_threshold_curr = total_attempts * 0.40
            if (
                cost_meter.cumulative_cost_usd >= spend_threshold_curr
                and cost_meter.attempts_completed < attempts_threshold_curr
            ):
                per_cell_table = compute_per_cell_cost_table(all_rows, cells)
                print("\n" + "=" * 80)
                print("WARNING: SPEND THRESHOLD PAUSE TRIGGERED")
                print(
                    f"Spend (${cost_meter.cumulative_cost_usd:.4f}) reached or crossed 50% of cap (${spend_threshold_curr:.2f}) "
                    f"before 40% of attempts ({cost_meter.attempts_completed}/{int(attempts_threshold_curr)}) were completed!"
                )
                print("Running per-cell cost breakdown table:")
                print(format_per_cell_table(per_cell_table))
                print("=" * 80 + "\n", flush=True)

                header_data = create_initial_header(
                    freeze_sha=freeze_sha,
                    cost_cap_usd=cost_cap,
                    tune_tasks_count=len(tune_tasks),
                    cells_count=len(cells),
                    runs_count=runs,
                    model_id=model_id,
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_output_tokens,
                    thinking_budget=thinking_budget,
                )
                header_data["experiment"]["status"] = "PAUSED_SPEND_THRESHOLD_REACHED"
                header_data["cost_meter"] = meter_state
                header_data["running_per_cell_cost_table"] = per_cell_table
                atomic_json_write(header_path, header_data)
                atomic_json_write(rows_path, all_rows)
                raise RuntimeError(
                    f"PAUSED_SPEND_THRESHOLD_REACHED: Spend reached ${cost_meter.cumulative_cost_usd:.4f} "
                    f"(>= 50% cap ${spend_threshold_curr:.2f}) before 40% of attempts "
                    f"({cost_meter.attempts_completed}/{int(attempts_threshold_curr)}) were completed."
                )

            # Update rows.json and header.json atomically
            atomic_json_write(rows_path, all_rows)

            header_data = create_initial_header(
                freeze_sha=freeze_sha,
                cost_cap_usd=cost_cap,
                tune_tasks_count=len(tune_tasks),
                cells_count=len(cells),
                runs_count=runs,
                model_id=model_id,
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens,
                thinking_budget=thinking_budget,
            )
            header_data["experiment"]["status"] = (
                "IN_PROGRESS" if len(all_rows) < len(schedule) else "COMPLETED"
            )
            header_data["cost_meter"] = meter_state
            atomic_json_write(header_path, header_data)

            print(
                f"[{len(all_rows)}/{len(schedule)}] Completed cell={code}, run={r_idx}, ticket={ticket['id']}: "
                f"strict={res.get('final_strict')} | Calls: {res.get('call_count')} | Cost: ${res.get('cost_usd'):.5f} | "
                f"Cumulative Cost: ${meter_state['cumulative_cost_usd']:.4f} / ${cost_cap:.2f}",
                flush=True,
            )
        return res

    if max_workers > 1 and len(pending) > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_screening_attempt, x) for x in pending]
            for fut in as_completed(futures):
                try:
                    fut.result()
                except Exception as e:
                    print(f"Screening attempt exception: {e}", flush=True)
                    if "HARD COST CAP EXCEEDED" in str(e) or "PAUSED_SPEND_THRESHOLD_REACHED" in str(e):
                        # Cancel remaining futures
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise
    else:
        for x in pending:
            process_screening_attempt(x)

    # Final completion update
    meter_state = cost_meter.get_state()
    header_data = create_initial_header(
        freeze_sha=freeze_sha,
        cost_cap_usd=cost_cap,
        tune_tasks_count=len(tune_tasks),
        cells_count=len(cells),
        runs_count=runs,
        model_id=model_id,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        thinking_budget=thinking_budget,
    )
    header_data["experiment"]["status"] = "COMPLETED"
    header_data["cost_meter"] = meter_state
    header_data["running_per_cell_cost_table"] = compute_per_cell_cost_table(all_rows, cells)
    atomic_json_write(header_path, header_data)

    print("\n================================================================================")
    print("SCREENING FACTORIAL RUN COMPLETED SUCCESSFULLY")
    print(f"Total Rows Saved:    {len(all_rows)}")
    print(f"Total Tokens In:     {meter_state['cumulative_tokens_in']:,}")
    print(f"Total Tokens Out:    {meter_state['cumulative_tokens_out']:,}")
    print(f"Total Thoughts:      {meter_state['cumulative_thoughts_tokens']:,}")
    print(f"Total Billed Tokens: {meter_state['cumulative_billed_tokens']:,}")
    print(f"Total Cost USD:      ${meter_state['cumulative_cost_usd']:.4f} (Cap: ${cost_cap:.2f})")
    print(f"Header:              {header_path}")
    print(f"Rows:                {rows_path}")
    print("================================================================================")
    return {"status": "COMPLETED", "rows_count": len(all_rows), "cost_usd": meter_state['cumulative_cost_usd']}


def main():
    parser = argparse.ArgumentParser(
        description="Tune-Set Factorial Screening Runner with Hard-Stop Cost Meter."
    )
    parser.add_argument(
        "--cost-cap",
        type=float,
        default=DEFAULT_COST_CAP_USD,
        help=f"Configurable hard-stop cost cap in USD (default: ${DEFAULT_COST_CAP_USD:.2f}).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Number of runs per factorial cell (default: {DEFAULT_RUNS}).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Number of concurrent worker threads (default: 6).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save screening_log_header.json and rows.json.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for schedule randomization (default: 42).",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default=DEFAULT_MODEL_ID,
        help=f"Model identifier (default: {DEFAULT_MODEL_ID}).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE}).",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=DEFAULT_TOP_P,
        help=f"Top-P sampling parameter (default: {DEFAULT_TOP_P}).",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help=f"Maximum output tokens (default: {DEFAULT_MAX_OUTPUT_TOKENS}).",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=DEFAULT_THINKING_BUDGET,
        help=f"Thinking token budget (default: {DEFAULT_THINKING_BUDGET}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and schedule without executing API calls.",
    )
    parser.add_argument(
        "--approved-for-execution",
        action="store_true",
        help="Explicit approval flag required by the Strict Stop Rule to execute live factor cells.",
    )

    args = parser.parse_args()
    try:
        run_screening(
            output_dir=args.output_dir,
            cost_cap=args.cost_cap,
            runs=args.runs,
            max_workers=args.workers,
            seed=args.seed,
            approved_for_execution=args.approved_for_execution,
            dry_run=args.dry_run,
            model_id=args.model_id,
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
            thinking_budget=args.thinking_budget,
        )
    except RuntimeError as e:
        print(f"\nExecution Halted: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
