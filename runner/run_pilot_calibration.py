"""Pilot Calibration Runner for suite_e5 (Round 13 Re-run with Redefined B0).

Executes the approved Round 13 Pilot Calibration:
- Redefined B0 (E1): All repository files in context (non-test source + visible tests)
  plus ticket issue and failing traceback excerpt.
  Factor u means "may run tests / use interactive tools", not "see the files".
- Model: frozen gemini-2.5-flash (thinking_budget=2048, max_output_tokens=16384)
- Condition: Baseline B0 ONLY (s=0, p=0, u=0, r=0, k=0, single call, no scaffolding)
- Tasks: ALL 28 tasks in suite_e5 (tune and held-out)
- Temperature Profiles (E2):
  1. T=0.0: 1 run across all 28 tasks (28 attempts)
  2. T=0.7: 5 runs across all 28 tasks (140 attempts)
  Total attempts: 168 attempts
- Multi-threaded execution: 6 workers with thread-safe file locking
- Frozen commit SHA tracked and stamped on every attempt
"""

import os
import sys
import json
import subprocess

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))

import suite_e5
import agent_runner

if __name__ == "__main__":
    cells = [
        ("B0", 0, 0, 0, 0, 0),
    ]

    tasks = suite_e5.T
    n_t0 = 1
    n_t07 = 5
    total_attempts = len(tasks) * (n_t0 + n_t07)
    
    print(f"=== PILOT CALIBRATION: REDEFINED B0 (Expanded Suite E5) ===")
    print(f"Tasks: {len(tasks)} (suite_e5, all {len(tasks)} tasks)")
    print(f"B0 Definition: Full repo in prompt + ticket + failing excerpt (E1)")
    print(f"Temperature profiles: T=0.0 (1 run = {len(tasks)} att) + T=0.7 (5 runs = {len(tasks)*n_t07} att)")
    print(f"Total attempts: {total_attempts}")
    
    # Estimate tokens and cost
    avg_in_tok = 900
    avg_out_tok = 1000
    est_total_in = total_attempts * avg_in_tok
    est_total_out = total_attempts * avg_out_tok
    est_cost_in = est_total_in * 0.075 / 1e6
    est_cost_out = est_total_out * 0.30 / 1e6
    total_est_cost = est_cost_in + est_cost_out
    print(f"Projected input tokens: ~{est_total_in:,} (${est_cost_in:.4f})")
    print(f"Projected output tokens (incl. thinking): ~{est_total_out:,} (${est_cost_out:.4f})")
    print(f"Total Projected Cost: ~${total_est_cost:.4f} (Budget limit: $5.00)")
    assert total_est_cost < 5.0, "Projected cost exceeds budget limit!"
    print("Cost confirmation PASSED. Commencing runs...\n")

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except Exception:
        git_sha = "unknown"

    # Profile 1: T=0.0
    print(f"--- [1/2] Executing T=0.0 Baseline Run ({len(tasks)} attempts) ---")
    out_dir_t0 = os.path.join(repo_root, "results", "pilot_calibration", "t0")
    rows_t0 = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=n_t0,
        model_id="gemini-2.5-flash",
        backend="gemini",
        temperature=0.0,
        output_dir=out_dir_t0,
        frozen_commit_sha=git_sha,
        seed=42,
        max_workers=6,
    )
    print(f"T=0.0 completed: {len(rows_t0)} rows.")

    # Profile 2: T=0.7
    print(f"\n--- [2/2] Executing T=0.7 Baseline Repeated Runs ({len(tasks)*n_t07} attempts) ---")
    out_dir_t07 = os.path.join(repo_root, "results", "pilot_calibration", "t07")
    rows_t07 = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=n_t07,
        model_id="gemini-2.5-flash",
        backend="gemini",
        temperature=0.7,
        output_dir=out_dir_t07,
        frozen_commit_sha=git_sha,
        seed=1337,
        max_workers=6,
    )
    print(f"T=0.7 completed: {len(rows_t07)} rows.")
    
    print(f"\nAll Pilot Calibration runs completed: {len(rows_t0)} (T=0.0) + {len(rows_t07)} (T=0.7) = {len(rows_t0) + len(rows_t07)} total attempts.")
