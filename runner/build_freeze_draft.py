import os
import json
import hashlib
from datetime import datetime, timezone

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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
        "total": 106,
        "families": 14,
        "tune": 46,
        "held_out": 60,
        "stated_initial": 21,
        "taught_initial": 57,
        "distractor_initial": 16,
        "transfer_initial": 12,
        "taught_retained_after_c2": 23,
        "taught_held_out_after_c2": 11,
    },
    "artifacts": artifacts,
    "review_note": "Draft freeze manifest prepared for Round 18 review. Final immutable FREEZE.json will be generated upon reviewer approval in a dedicated commit before factor execution."
}

out_path = os.path.join(repo_root, "FREEZE_DRAFT.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(freeze_data, f, indent=2)

print("Updated FREEZE_DRAFT.json successfully!")
