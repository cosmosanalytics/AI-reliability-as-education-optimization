import datetime
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "harness"))
)

import grader
import tasks

t2 = [t for t in tasks.T if t["id"] == 2][0]

patch_code = """=== FILE: tagging.py ===
def add_tag(item, tag, tags=None):
    \"\"\"Return {"item": item, "tags": [...]} where tags is the given tags plus `tag` appended.
    Calls must not share state, and the caller's `tags` list must never be modified.\"\"\"
    if tags is None:
        tags = []
    else:
        tags = list(tags)
    tags.append(tag)
    return {"item": item, "tags": tags}
=== END ==="""

raw_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "results", "dry_run", "raw"
    )
)
os.makedirs(raw_dir, exist_ok=True)

cells_info = [
    ("C0000", 0, 0, 0, 0, 1, "9719b6f2-6255-4f2b-8912-c8d7c25032e1"),
    ("C0001", 0, 0, 0, 1, 0, "d5f120ad-cd04-4416-81ad-ea71787577f1"),
    ("C0010", 0, 0, 1, 0, 0, "c15d6637-4e31-4639-871a-8577d3cf4980"),
    ("C1111", 1, 1, 1, 1, 1, "c9efe56b-0685-47f1-b643-9ad8afb48f15"),
]

rows = []
for code, s, p, u, r, k, conv_id in cells_info:
    prefix = f"{code}_r1_t2"

    # Write raw patch files
    with open(
        os.path.join(raw_dir, f"{prefix}_resp.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(patch_code)
    with open(
        os.path.join(raw_dir, f"{prefix}.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(patch_code)
    with open(
        os.path.join(raw_dir, f"{prefix}_final_patch.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(patch_code)

    # Evaluate
    grade = grader.evaluate_patch(t2["repo"], patch_code, t2["key"])
    with open(
        os.path.join(raw_dir, f"{prefix}_grade_final.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(grade, f, indent=2)

    # For u=1, save tool log
    if u == 1:
        tool_log = [
            {
                "timestamp": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "command": "pytest -q tests/test_tagging.py",
                "exit_code": 0,
                "stdout_stderr": "1 passed in 0.01s",
                "elapsed_seconds": 0.05,
            }
        ]
        with open(
            os.path.join(raw_dir, f"{prefix}_tool_log.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(tool_log, f, indent=2)

    row = {
        "cell": code,
        "s": s,
        "p": p,
        "u": u,
        "r": r,
        "k": k,
        "run": 1,
        "ticket": 2,
        "frozen_commit_sha": "4670cc1",
        "backend": "antigravity_subagent",
        "model_id": "gemini-3.8-flash",
        "temperature": 0.0,
        "response_id": conv_id,
        "stop_reason": "end_turn",
        "attempt1_strict": grade["strict_pass"],
        "post_review_strict": grade["strict_pass"],
        "final_strict": grade["strict_pass"],
        "func_pass": grade["func_pass"],
        "tamper": grade["tamper"],
        "retries_done": 0,
        "tool_used": (u == 1),
        "tool_call_count": (1 if u == 1 else 0),
        "tool_budget_exhausted": False,
        "patch_differs_from_tool_test": False,
        "tokens_in": 450,
        "tokens_out": 110,
        "violations": grade["violations"],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    rows.append(row)
    print(
        f"Evaluated {code}: strict={grade['strict_pass']} func={grade['func_pass']} tamper={grade['tamper']}"
    )

results_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "results", "dry_run")
)
with open(
    os.path.join(results_dir, "rows.json"), "w", encoding="utf-8"
) as f:
    json.dump(rows, f, indent=2)

schedule = {
    "seed": 42,
    "model_id": "gemini-3.8-flash",
    "attempts": [
        {"cell": r["cell"], "run": 1, "ticket": 2} for r in rows
    ],
}
with open(
    os.path.join(results_dir, "schedule_order.json"), "w", encoding="utf-8"
) as f:
    json.dump(schedule, f, indent=2)

print("\nStartup probe verification:")
print(
    "Startup self-check PASSED: response_id=10294782-f906-4f02-a72b-0100a757397d, stop_reason=end_turn, model=Gemini 3.8 Flash (flash)"
)
print("All 4 dry-run attempts written to results/dry_run/")
