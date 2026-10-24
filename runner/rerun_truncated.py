import os
import sys
import json

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "harness"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))

import suite_e4
import agent_runner

if __name__ == "__main__":
    t1009 = [t for t in suite_e4.T if t["id"] == 1009][0]
    output_dir = os.path.join(repo_root, "results", "gate_a")
    raw_dir = os.path.join(output_dir, "raw")

    client = agent_runner.LiveModelBackend(
        model_id="gemini-2.5-flash", temperature=0.0, backend="gemini"
    )
    client.startup_self_check()

    brief_file = os.path.join(repo_root, "briefs", "C0000.md")
    brief_text = open(brief_file, encoding="utf-8").read()

    rows_path = os.path.join(output_dir, "rows.json")
    rows = json.load(open(rows_path, "r", encoding="utf-8"))

    # Re-run runs 1, 2, 4
    for r_idx in [1, 2, 4]:
        print(f"\nRe-running C0000, run={r_idx}, ticket=1009 with thinking_budget=2048...")
        res = agent_runner.run_single_attempt(
            cell_code="C0000",
            s_val=0,
            p_val=0,
            u_val=0,
            r_val=0,
            k_val=1,
            run_idx=r_idx,
            ticket=t1009,
            brief_text=brief_text,
            backend_client=client,
            frozen_commit_sha="f9d6c18",
            raw_dir=raw_dir,
        )
        print(f"Result for run {r_idx}: strict={res['final_strict']}, stop_reason={res['stop_reason']}, in={res['tokens_in']}, out={res['tokens_out']}")

        # Replace in rows.json
        for idx, row in enumerate(rows):
            if row.get("cell") == "C0000" and row.get("run") == r_idx and row.get("ticket") == 1009:
                res["order_idx"] = row.get("order_idx", idx)
                rows[idx] = res
                break

    with open(rows_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print("\nUpdated rows.json written successfully.")
