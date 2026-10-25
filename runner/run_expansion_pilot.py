"""run_expansion_pilot.py: Executes fresh baseline B0 pilot for the 22 expansion tasks (2085-2106).

Complies with Round 17 K3 specifications:
- Model: frozen gemini-2.5-flash (thinking_budget=2048, max_output_tokens=16384)
- Condition: Baseline B0 ONLY (s=0, p=0, u=0, r=0, k=0)
- Tasks: 22 new expansion tasks ONLY (existing 84 task data preserved untouched)
- Temperature Profiles:
  1. T=0.0: 1 run across 22 tasks (22 attempts, seed=42)
  2. T=0.7: 5 runs across 22 tasks (110 attempts, seed=1337)
- Multi-threaded execution: 6 workers with thread-safe file locking
- Stamped with git commit SHA
- Appends results into results/pilot_calibration/t0 and results/pilot_calibration/t07
"""

import os
import sys
import json
import shutil
import subprocess
import dotenv

dotenv.load_dotenv()

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))

import suite_e5
import agent_runner

def main():
    cells = [
        ("B0", 0, 0, 0, 0, 0),
    ]

    new_tids = set(range(2085, 2107))
    tasks = [t for t in suite_e5.T if t["id"] in new_tids]
    assert len(tasks) == 22, f"Expected 22 expansion tasks, got {len(tasks)}"

    n_t0 = 1
    n_t07 = 5
    total_attempts = len(tasks) * (n_t0 + n_t07)

    print(f"=== EXPANSION PILOT CALIBRATION: BASELINE B0 (Tasks 2085-2106) ===")
    print(f"New Tasks: {len(tasks)} (Tasks 2085 to 2106)")
    print(f"Condition: B0 baseline ONLY (s=0, p=0, u=0, r=0, k=0)")
    print(f"Profiles: T=0.0 (1 run = {len(tasks)} att) + T=0.7 (5 runs = {len(tasks)*n_t07} att)")
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

    temp_t0 = os.path.join(repo_root, "results", "pilot_calibration", "temp_t0")
    temp_t07 = os.path.join(repo_root, "results", "pilot_calibration", "temp_t07")
    os.makedirs(temp_t0, exist_ok=True)
    os.makedirs(temp_t07, exist_ok=True)

    # 1. Run T=0.0
    print(f"--- [1/2] Executing T=0.0 Baseline Run ({len(tasks)} attempts) ---")
    rows_t0_new = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=n_t0,
        model_id="gemini-2.5-flash",
        backend="gemini",
        temperature=0.0,
        output_dir=temp_t0,
        frozen_commit_sha=git_sha,
        seed=42,
        max_workers=6,
    )
    print(f"T=0.0 completed: {len(rows_t0_new)} rows.")

    # 2. Run T=0.7
    print(f"\n--- [2/2] Executing T=0.7 Baseline Repeated Runs ({len(tasks)*n_t07} attempts) ---")
    rows_t07_new = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=n_t07,
        model_id="gemini-2.5-flash",
        backend="gemini",
        temperature=0.7,
        output_dir=temp_t07,
        frozen_commit_sha=git_sha,
        seed=1337,
        max_workers=6,
    )
    print(f"T=0.7 completed: {len(rows_t07_new)} rows.")

    # 3. Merge into master results/pilot_calibration/t0 and t07
    t0_master = os.path.join(repo_root, "results", "pilot_calibration", "t0", "rows.json")
    with open(t0_master, "r", encoding="utf-8") as f:
        existing_t0 = json.load(f)
    # Check no duplicate
    existing_t0_ids = set(r["ticket"] for r in existing_t0)
    for r in rows_t0_new:
        if r["ticket"] not in existing_t0_ids:
            existing_t0.append(r)
    with open(t0_master, "w", encoding="utf-8") as f:
        json.dump(existing_t0, f, indent=2)
    print(f"Merged T=0.0: Total rows in {t0_master} = {len(existing_t0)}")

    t07_master = os.path.join(repo_root, "results", "pilot_calibration", "t07", "rows.json")
    with open(t07_master, "r", encoding="utf-8") as f:
        existing_t07 = json.load(f)
    existing_t07_runs = set((r["ticket"], r["run"]) for r in existing_t07)
    for r in rows_t07_new:
        if (r["ticket"], r["run"]) not in existing_t07_runs:
            existing_t07.append(r)
    with open(t07_master, "w", encoding="utf-8") as f:
        json.dump(existing_t07, f, indent=2)
    print(f"Merged T=0.7: Total rows in {t07_master} = {len(existing_t07)}")

    # Copy raw prompt and envelope files
    raw_dest_t0 = os.path.join(repo_root, "results", "pilot_calibration", "t0", "raw")
    raw_src_t0 = os.path.join(temp_t0, "raw")
    if os.path.exists(raw_src_t0):
        for fn in os.listdir(raw_src_t0):
            shutil.copy2(os.path.join(raw_src_t0, fn), os.path.join(raw_dest_t0, fn))

    raw_dest_t07 = os.path.join(repo_root, "results", "pilot_calibration", "t07", "raw")
    raw_src_t07 = os.path.join(temp_t07, "raw")
    if os.path.exists(raw_src_t07):
        for fn in os.listdir(raw_src_t07):
            shutil.copy2(os.path.join(raw_src_t07, fn), os.path.join(raw_dest_t07, fn))

    # Clean up temp dirs
    shutil.rmtree(temp_t0, ignore_errors=True)
    shutil.rmtree(temp_t07, ignore_errors=True)

    print("\nAll 132 new attempts recorded and merged successfully!")

if __name__ == "__main__":
    main()
