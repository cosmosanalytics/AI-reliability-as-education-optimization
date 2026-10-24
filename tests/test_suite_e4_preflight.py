"""test_suite_e4_preflight.py: Pre-flight validation for Suite E4 benchmark tasks.

Verifies:
1. Gold reference patch passes 100% of visible and hidden tests on all 12 tasks.
2. Unpatched baseline code fails hidden tests (100% failure rate; zero false positives) on all 12 tasks.
"""

import os
import sys
import pytest

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_repo_root, "runner"))
sys.path.insert(0, os.path.join(_repo_root, "harness"))
sys.path.insert(0, os.path.join(_repo_root, "benchmarks"))

import suite_e4
from grader import evaluate_patch


def format_patch(ref_dict):
    return "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in ref_dict.items()
    )


@pytest.mark.parametrize("task", suite_e4.T, ids=[f"task_{t['id']}" for t in suite_e4.T])
def test_unpatched_baseline_fails(task):
    """Unpatched code must fail the hidden tests (100% failure rate; zero false positives)."""
    res = evaluate_patch(task["repo"], "", task["key"])
    assert res["strict_pass"] is False, f"Task {task['id']} unpatched code unexpectedly passed hidden tests!"
    assert res["tamper"] is False


@pytest.mark.parametrize("task", suite_e4.T, ids=[f"task_{t['id']}" for t in suite_e4.T])
def test_gold_reference_passes(task):
    """Gold reference solution must achieve 100% strict pass."""
    gold_patch = format_patch(task["ref"])
    res = evaluate_patch(task["repo"], gold_patch, task["key"])
    assert res["strict_pass"] is True, f"Task {task['id']} gold patch failed: {res.get('violations')}, vis_rc={res.get('visible_rc')}"
    assert res["func_pass"] is True
    assert res["tamper"] is False
    assert len(res["violations"]) == 0
