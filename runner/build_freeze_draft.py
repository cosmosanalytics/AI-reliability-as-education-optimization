import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))
import suite_e5

splits = json.load(open(os.path.join(repo_root, "benchmarks", "splits_e5.json")))
tune_ids = set(splits["tune"])
held_out_ids = set(splits["held_out"])

# Count initial tags
tasks = suite_e5.T
total = len(tasks)
families = len(set(t["family"] for t in tasks))
tune_count = len(tune_ids)
held_out_count = len(held_out_ids)

stated_initial = sum(1 for t in tasks if t["class_tag"] == "STATED")
taught_initial = sum(1 for t in tasks if t["class_tag"] == "TAUGHT")
distractor_initial = sum(1 for t in tasks if t["class_tag"] == "DISTRACTOR")
transfer_initial = sum(1 for t in tasks if t["class_tag"] == "TRANSFER")

# Calculate retained TAUGHT under C2 (baseline pass rate <= 70% at T=0.7)
rows = [json.loads(line) for line in open(os.path.join(repo_root, "results", "pilot_calibration", "rows.jsonl"))]
t07_rows = [r for r in rows if r.get("temperature") == 0.7]
task_runs = defaultdict(list)
for r in t07_rows:
    task_runs[r["ticket"]].append(r)

task_map = {t["id"]: t for t in tasks}
taught_retained = 0
taught_held_out = 0

for tid, runs in task_runs.items():
    t = task_map.get(tid)
    if t and t["class_tag"] == "TAUGHT":
        passes = sum(1 for r in runs if r.get("final_strict"))
        rate = passes / len(runs)
        if rate <= 0.70:
            taught_retained += 1
            if tid in held_out_ids:
                taught_held_out += 1

files_to_hash = [
    "benchmarks/suite_e5.py",
    "benchmarks/splits_e5.json",
    "briefs/HANDBOOK.md",
    "briefs/PLACEBO.md",
    "runner/agent_runner.py",
    "runner/grader.py",
    "benchmarks/CONSISTENCY_MATRIX.md",
    "benchmarks/FAIRNESS_e5.md",
    "PILOT_CALIBRATION_REPORT.md",
    "PRE_REGISTRATION.md",
]

artifacts = {}
for rel_path in files_to_hash:
    full_path = os.path.join(repo_root, rel_path)
    with open(full_path, "rb") as f:
        artifacts[rel_path.replace("\\", "/")] = hashlib.sha256(f.read()).hexdigest().upper()

freeze_data = {
    "manifest_version": "2.0-draft",
    "phase": "pre_registration_freeze_draft",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "model": "gemini-2.5-flash",
    "backend": "gemini",
    "task_counts": {
        "total": total,
        "families": families,
        "tune": tune_count,
        "held_out": held_out_count,
        "stated_initial": stated_initial,
        "taught_initial": taught_initial,
        "distractor_initial": distractor_initial,
        "transfer_initial": transfer_initial,
        "taught_retained_after_c2": taught_retained,
        "taught_held_out_after_c2": taught_held_out,
    },
    "artifacts": artifacts,
    "review_note": "Draft freeze manifest prepared for Round 18 review. Final immutable FREEZE.json will be generated upon reviewer approval in a dedicated commit before factor execution."
}

out_path = os.path.join(repo_root, "FREEZE_DRAFT.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(freeze_data, f, indent=2)

print(f"Updated FREEZE_DRAFT.json successfully with counts: total={total}, taught_initial={taught_initial}, taught_retained={taught_retained}, taught_held_out={taught_held_out}")
