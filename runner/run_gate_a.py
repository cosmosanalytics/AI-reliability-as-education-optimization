import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "harness"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))

import suite_e4
import agent_runner

if __name__ == "__main__":
    cells = [
        ("C0000", 0, 0, 0, 0, 1),
        ("C1111", 1, 1, 1, 1, 1),
    ]

    tasks = suite_e4.T
    print(f"Starting Gate A evaluation on {len(tasks)} tasks across 2 cells x 5 runs = {len(tasks)*2*5} attempts...")
    rows = agent_runner.run_experiment(
        tasks=tasks,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=5,
        model_id="gemini-2.5-flash",
        backend="gemini",
        output_dir=os.path.join(repo_root, "results", "gate_a"),
        frozen_commit_sha="f9d6c18",
        seed=42,
        max_workers=6,
    )

    print("Gate A execution completed. Total rows:", len(rows))
