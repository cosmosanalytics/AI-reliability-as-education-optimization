"""Pilot Calibration Runner for suite_e5 (Baseline B0 condition).

Executes the approved Round 12 Pilot Calibration:
- Model: frozen gemini-2.5-flash (thinking_budget=2048, max_output_tokens=16384, temperature=0.0)
- Condition: Baseline B0 ONLY (ticket + failing excerpt + traceback file, single call, standard envelope)
  s=0, p=0, u=0, r=0, k=0 (one call, no handbook, no placebo, no examples, no tools, no review, no retry)
- Tasks: ALL 28 tasks in suite_e5 (tune and held-out)
- Repeats: 5 runs per task (140 total attempts)
- Multi-threaded execution: 6 workers with thread-safe file locking
- Frozen commit SHA tracked and stamped on every attempt
"""

import os
import sys
import json

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))

import suite_e5
import agent_runner

if __name__ == "__main__":
    # Baseline B0 cell: single call (s=0, p=0, u=0, r=0, k=0)
    cells = [
        ("B0", 0, 0, 0, 0, 0),
    ]

    tasks = suite_e5.T
    n_runs = 5
    total_attempts = len(tasks) * len(cells) * n_runs
    print(f"=== PILOT CALIBRATION: BASELINE B0 ===")
    print(f"Tasks: {len(tasks)} (suite_e5, all 28 tasks)")
    print(f"Condition: B0 (single call, no scaffolding)")
    print(f"Repeats per task: {n_runs}")
    print(f"Total attempts: {total_attempts}")
    
    # Estimate tokens and cost
    avg_in_tok = 750
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
    print("Cost confirmation PASSED. Commencing run...\n")

    output_dir = os.path.join(repo_root, "results", "pilot_calibration")
    
    # Get current git commit SHA
    import subprocess
    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except Exception:
        git_sha = "unknown"

    rows = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=n_runs,
        model_id="gemini-2.5-flash",
        backend="gemini",
        temperature=0.0,
        output_dir=output_dir,
        frozen_commit_sha=git_sha,
        seed=42,
        max_workers=6,
    )

    print(f"\nPilot Calibration execution completed. Total rows recorded: {len(rows)}")
