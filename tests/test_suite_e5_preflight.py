"""test_suite_e5_preflight.py: Pre-flight validation for Suite E5 benchmark tasks.

Complies strictly with Section 8 Addendum v2 of REAL_TEST_REQUIREMENTS.md and Round 9 criteria:
1. Gold reference patch passes 100% of visible and hidden tests on all 28 tasks.
2. Unpatched baseline code fails hidden tests (100% failure rate; zero false positives) on all 28 tasks.
3. Mutant 1 (plausible wrong fix) fails hidden tests on all 28 tasks.
4. Mutant 2 (plausible wrong fix) fails hidden tests on all 28 tasks.
5. S-1: Zero hint comments (# BUG, # FIX, # TODO, # HACK) in any provided non-test file.
6. Handbook vs Placebo token balance is within +/-3% (cl100k_base).
7. Suite structure and tag distribution meet all pre-registration constraints:
   - >= 24 evaluated instances (28 provided across 7 bug families)
   - >= 8 TAUGHT instances (actual: 11)
   - >= 2 DISTRACTOR instances (actual: 3)
   - >= 3 TRANSFER instances (actual: 4)
   - >= 1/3 hidden-root-cause instances (actual: 12, all tagged root_cause_only_with_exploration=True)
   - >= 1/3 visible-test-sensitive instances (actual: 12)
   - All tasks have >= 40 non-test lines across >= 3 files
"""

import os
import sys
import re
import json
import pytest

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_repo_root, "runner"))
sys.path.insert(0, os.path.join(_repo_root, "harness"))
sys.path.insert(0, os.path.join(_repo_root, "benchmarks"))

import suite_e5
from grader import evaluate_patch

try:
    import tiktoken
except ImportError:
    tiktoken = None


def format_patch(ref_dict):
    return "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in ref_dict.items()
    )


@pytest.mark.parametrize("task", suite_e5.T, ids=[f"task_{t['id']}" for t in suite_e5.T])
def test_unpatched_baseline_fails(task):
    """Unpatched code must fail the hidden tests (100% failure rate; zero false positives)."""
    res = evaluate_patch(task["repo"], "", task["key"])
    assert res["strict_pass"] is False, f"Task {task['id']} unpatched code unexpectedly passed hidden tests!"
    assert res["tamper"] is False


@pytest.mark.parametrize("task", suite_e5.T, ids=[f"task_{t['id']}" for t in suite_e5.T])
def test_gold_reference_passes(task):
    """Gold reference solution must achieve 100% strict pass."""
    gold_patch = format_patch(task["ref"])
    res = evaluate_patch(task["repo"], gold_patch, task["key"])
    assert res["strict_pass"] is True, (
        f"Task {task['id']} gold patch failed: violations={res.get('violations')}, "
        f"vis_rc={res.get('visible_rc')}, failing_variants={res.get('failing_variants')}, "
        f"output={res.get('visible_output')}"
    )
    assert res["func_pass"] is True
    assert res["tamper"] is False
    assert len(res["violations"]) == 0


@pytest.mark.parametrize("task", suite_e5.T, ids=[f"task_{t['id']}" for t in suite_e5.T])
def test_mutant1_fails(task):
    """Mutant 1 (plausible-wrong fix 1) must fail hidden tests."""
    m1_patch = format_patch(task["mutant1"])
    res = evaluate_patch(task["repo"], m1_patch, task["key"])
    assert res["strict_pass"] is False, f"Task {task['id']} mutant1 unexpectedly passed hidden tests!"


@pytest.mark.parametrize("task", suite_e5.T, ids=[f"task_{t['id']}" for t in suite_e5.T])
def test_mutant2_fails(task):
    """Mutant 2 (plausible-wrong fix 2) must fail hidden tests."""
    m2_patch = format_patch(task["mutant2"])
    res = evaluate_patch(task["repo"], m2_patch, task["key"])
    assert res["strict_pass"] is False, f"Task {task['id']} mutant2 unexpectedly passed hidden tests!"


@pytest.mark.parametrize("task", suite_e5.T, ids=[f"task_{t['id']}" for t in suite_e5.T])
def test_no_hint_comments_in_provided_files(task):
    """Enforce S-1: provided non-test repo files must NOT contain hint comments (# BUG, # FIX, # TODO, # HACK)."""
    hint_regex = re.compile(r"#\s*(BUG|FIX|TODO|HACK)", re.IGNORECASE)
    for path, content in task["repo"].items():
        if not path.startswith("tests/"):
            m = hint_regex.search(content)
            assert m is None, (
                f"Task {task['id']} provided file '{path}' contains hint comment: {m.group(0)}"
            )


def test_handbook_placebo_token_balance():
    """Assert Handbook and Placebo token difference is strictly <= 3% using cl100k_base."""
    handbook_path = os.path.join(_repo_root, "briefs", "HANDBOOK.md")
    placebo_path = os.path.join(_repo_root, "briefs", "PLACEBO.md")
    
    assert os.path.exists(handbook_path), "HANDBOOK.md missing"
    assert os.path.exists(placebo_path), "PLACEBO.md missing"
    
    with open(handbook_path, "r", encoding="utf-8") as f:
        handbook_text = f.read()
    with open(placebo_path, "r", encoding="utf-8") as f:
        placebo_text = f.read()
        
    if tiktoken is None:
        pytest.skip("tiktoken not installed")
        
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        t_handbook = len(enc.encode(handbook_text))
        t_placebo = len(enc.encode(placebo_text))
    except Exception as exc:
        pytest.skip(f"tiktoken encoding failed (offline/network): {exc}")
        
    diff_pct = abs(t_handbook - t_placebo) / max(t_handbook, t_placebo) * 100.0
    assert diff_pct <= 3.0, (
        f"Token imbalance exceeds 3.0%: Handbook={t_handbook}, Placebo={t_placebo}, diff={diff_pct:.2f}%"
    )


def test_e5_tag_distribution():
    """Assert suite_e5 satisfies all structural constraints from Section 8 Addendum v2 and Round 9."""
    tasks = suite_e5.T
    n_tasks = len(tasks)
    assert n_tasks >= 24, f"Expected >= 24 tasks, found {n_tasks}"
    
    distractor = [t for t in tasks if t["class_tag"] == "DISTRACTOR"]
    transfer = [t for t in tasks if t["class_tag"] == "TRANSFER"]
    taught = [t for t in tasks if t["class_tag"] == "TAUGHT"]
    stated = [t for t in tasks if t["class_tag"] == "STATED"]
    
    assert len(distractor) >= 2, f"Expected >= 2 DISTRACTOR, found {len(distractor)}"
    assert len(transfer) >= 3, f"Expected >= 3 TRANSFER, found {len(transfer)}"
    assert len(taught) >= 8, f"Expected >= 8 TAUGHT, found {len(taught)}"
    assert len(stated) >= 4, f"Expected >= 4 STATED, found {len(stated)}"
    
    hrc = [t for t in tasks if t.get("hidden_root_cause")]
    vts = [t for t in tasks if t.get("visible_test_sensitive")]
    rce = [t for t in tasks if t.get("root_cause_only_with_exploration")]
    
    min_third = n_tasks / 3.0
    assert len(hrc) >= min_third, f"Expected >= 1/3 hidden-root-cause ({min_third:.1f}), found {len(hrc)}"
    assert len(vts) >= min_third, f"Expected >= 1/3 visible-test-sensitive ({min_third:.1f}), found {len(vts)}"
    assert len(rce) == len(hrc), "All hidden-root-cause tasks must be tagged root_cause_only_with_exploration"
    
    # Check that every task has required metadata, files, and realistic sizes
    for t in tasks:
        assert t["family"], f"Task {t['id']} missing family"
        assert t["repo"], f"Task {t['id']} missing repo"
        assert t["traceback_files"], f"Task {t['id']} missing traceback_files"
        for tf in t["traceback_files"]:
            assert tf in t["repo"], f"Task {t['id']} traceback_file {tf} not in repo"
        if t["class_tag"] in ("TAUGHT", "DISTRACTOR"):
            assert t.get("handbook_citations"), f"Task {t['id']} ({t['class_tag']}) missing handbook_citations"
            
        non_test_files = [p for p in t["repo"] if not p.startswith("tests/")]
        non_test_lines = sum(len(t["repo"][p].splitlines()) for p in non_test_files)
        assert len(non_test_files) >= 3, f"Task {t['id']} has {len(non_test_files)} non-test files (< 3)"
        assert non_test_lines >= 40, f"Task {t['id']} has {non_test_lines} non-test lines (< 40)"
        assert non_test_lines <= 120, f"Task {t['id']} has {non_test_lines} non-test lines (> 120)"


def test_splits_e5_stratification():
    """Assert splits_e5.json partitions tasks into class-stratified Tune (15) and Held-out (13).
    Enforces per-class minimums (C1 resolution) so that the confirmatory study is statistically powered
    on the primary TAUGHT class:
    - Held-out: >= 4 TAUGHT, >= 3 STATED, >= 2 DISTRACTOR, >= 3 TRANSFER (all 4 held out).
    - Tune: >= 4 TAUGHT, >= 4 STATED, >= 1 DISTRACTOR, 0 TRANSFER.
    """
    splits_path = os.path.join(_repo_root, "benchmarks", "splits_e5.json")
    assert os.path.exists(splits_path), "splits_e5.json missing"
    
    with open(splits_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
        
    tune = splits["tune"]
    held_out = splits["held_out"]
    
    assert len(tune) == 15, f"Expected 15 tune tasks, found {len(tune)}"
    assert len(held_out) == 13, f"Expected 13 held-out tasks, found {len(held_out)}"
    assert set(tune).isdisjoint(set(held_out)), "Tune and held-out sets must be disjoint"
    assert len(set(tune) | set(held_out)) == 28, "Split must cover all 28 tasks"
    
    task_map = {t["id"]: t for t in suite_e5.T}
    
    # Held-out per-class minimums
    taught_in_held_out = [tid for tid in held_out if task_map[tid]["class_tag"] == "TAUGHT"]
    stated_in_held_out = [tid for tid in held_out if task_map[tid]["class_tag"] == "STATED"]
    distractor_in_held_out = [tid for tid in held_out if task_map[tid]["class_tag"] == "DISTRACTOR"]
    transfer_in_held_out = [tid for tid in held_out if task_map[tid]["class_tag"] == "TRANSFER"]
    
    assert len(taught_in_held_out) >= 4, f"Expected >= 4 TAUGHT in held-out, found {len(taught_in_held_out)}"
    assert len(stated_in_held_out) >= 3, f"Expected >= 3 STATED in held-out, found {len(stated_in_held_out)}"
    assert len(distractor_in_held_out) >= 2, f"Expected >= 2 DISTRACTOR in held-out, found {len(distractor_in_held_out)}"
    assert len(transfer_in_held_out) >= 3, f"Expected >= 3 TRANSFER in held-out, found {len(transfer_in_held_out)}"
    assert len(transfer_in_held_out) == 4, f"All 4 TRANSFER tasks must be in held-out, found {len(transfer_in_held_out)}"
    
    # Tune per-class minimums (for screening experiment estimation)
    taught_in_tune = [tid for tid in tune if task_map[tid]["class_tag"] == "TAUGHT"]
    stated_in_tune = [tid for tid in tune if task_map[tid]["class_tag"] == "STATED"]
    distractor_in_tune = [tid for tid in tune if task_map[tid]["class_tag"] == "DISTRACTOR"]
    transfer_in_tune = [tid for tid in tune if task_map[tid]["class_tag"] == "TRANSFER"]
    
    assert len(taught_in_tune) >= 4, f"Expected >= 4 TAUGHT in tune, found {len(taught_in_tune)}"
    assert len(stated_in_tune) >= 4, f"Expected >= 4 STATED in tune, found {len(stated_in_tune)}"
    assert len(distractor_in_tune) >= 1, f"Expected >= 1 DISTRACTOR in tune, found {len(distractor_in_tune)}"
    assert len(transfer_in_tune) == 0, f"TRANSFER tasks cannot be in tune set: {transfer_in_tune}"


def test_no_design_words_in_tests_or_traces():
    """Enforce B1 & B2: zero design labels or giveaways in test IDs, filenames, or tracebacks."""
    forbidden = re.compile(r"(taught|stated|distractor|transfer|visible_sensitive|_visible|_hidden)", re.IGNORECASE)
    for t in suite_e5.T:
        tb = t["traceback_text"]
        m = forbidden.search(tb)
        assert m is None, f"Task {t['id']} traceback contains design word: {m.group(0)} in '{tb}'"
        
        # Check hidden test overlay
        for variant in t["key"]["variants"]:
            overlay = variant.get("overlay", {})
            for fn, content in overlay.items():
                assert "hidden" not in fn.lower(), f"Task {t['id']} test file '{fn}' contains 'hidden'"
                for tf in re.findall(r"def (test_[a-zA-Z0-9_]+)", content):
                    m = forbidden.search(tf)
                    assert m is None, f"Task {t['id']} test '{tf}' contains design word: {m.group(0)}"
                    
        # Check visible tests in repo
        for fn, content in t["repo"].items():
            if fn.startswith("tests/"):
                for tf in re.findall(r"def (test_[a-zA-Z0-9_]+)", content):
                    m = forbidden.search(tf)
                    assert m is None, f"Task {t['id']} visible test '{tf}' contains design word: {m.group(0)}"


def test_root_cause_reachability():
    """Enforce B4 & Smaller Items: For all 12 HRC tasks, root-cause file is imported by traceback file."""
    for t in suite_e5.T:
        if t.get("hidden_root_cause"):
            tb_file = t["traceback_files"][0]
            tb_content = t["repo"][tb_file]
            rc_files = [f for f in t["ref"] if f != tb_file and not f.startswith("tests/")]
            for rc in rc_files:
                mod_name = rc[:-3]
                assert re.search(r"\b" + mod_name + r"\b", tb_content), (
                    f"Task {t['id']}: HRC root-cause file '{rc}' is not imported by traceback file '{tb_file}'"
                )


def test_zero_unimported_decoy_files():
    """Enforce B4: every non-test file in repo is on reachability path (zero unimported filler files)."""
    for t in suite_e5.T:
        tb_file = t["traceback_files"][0]
        test_code = "\n".join(c for path, c in t["repo"].items() if path.startswith("tests/"))
        non_test_files = [p for p in t["repo"] if not p.startswith("tests/")]
        for p in non_test_files:
            mod_name = p[:-3]
            if p == tb_file:
                assert re.search(r"\b" + mod_name + r"\b", test_code), (
                    f"Task {t['id']}: Entrypoint file '{p}' is not imported by tests"
                )
            else:
                non_test_code = "\n".join(c for path, c in t["repo"].items() if not path.startswith("tests/") and path != p)
                assert re.search(r"\b" + mod_name + r"\b", non_test_code), (
                    f"Task {t['id']}: Helper file '{p}' is not referenced/imported by any repo code"
                )
