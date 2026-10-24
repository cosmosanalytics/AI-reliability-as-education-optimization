import os
import sys

# Ensure repo root and runner are in python path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "harness"))

import tasks
import agent_runner

if __name__ == "__main__":
    t2 = [t for t in tasks.T if t["id"] == 2]
    cells = [
        ("C0000", 0, 0, 0, 0, 1),
        ("C0001", 0, 0, 0, 1, 0),
        ("C0010", 0, 0, 1, 0, 0),
        ("C1111", 1, 1, 1, 1, 1),
    ]

    print("Starting live model dry run against Gemini API...")
    rows = agent_runner.run_experiment(
        tasks=t2,
        brief_dir=os.path.join(repo_root, "briefs"),
        cells=cells,
        runs=1,
        model_id="gemini-2.5-flash",
        backend="gemini",
        output_dir=os.path.join(repo_root, "results", "dry_run"),
        frozen_commit_sha="ca795d6",
        seed=42,
    )
    print("Dry run complete! Rows returned:", len(rows))
    for r in rows:
        print(
            f"Cell: {r['cell']}, run: {r['run']}, strict: {r['final_strict']}, "
            f"in_tok: {r['tokens_in']}, out_tok: {r['tokens_out']}, "
            f"tool_used: {r['tool_used']}, tool_calls: {r['tool_call_count']}, "
            f"retries: {r['retries_done']}, resp_id: {r['response_id']}"
        )
