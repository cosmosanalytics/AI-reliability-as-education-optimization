"""Validation test suite for Family 13 and Family 14."""
import os
import sys
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))

from grader import evaluate_patch
from family13_percentiles import register_family_13
from family14_transitions import register_family_14

TASKS = []

def add_task(
    tid, family, name, class_tag, issue, traceback_text, traceback_files,
    repo, hidden, ref, mutant1, mutant2,
    hidden_root_cause=False, visible_test_sensitive=False,
    root_cause_only_with_exploration=False,
    handbook_citations=(),
    assertions=()
):
    non_test_files = [p for p in repo if not p.startswith("tests/")]
    non_test_lines = sum(len(repo[p].splitlines()) for p in non_test_files)
    vis = [p for p in repo if p.startswith("tests/")]
    key = {
        "visible_paths": list(vis),
        "protected": list(vis),
        "forbidden": [],
        "must_touch": [],
        "variants": [
            {
                "name": "hidden tests",
                "overlay": hidden,
                "expect": "pass",
                "paths": ["tests"],
            }
        ],
    }
    task_dict = {
        "id": tid,
        "family": family,
        "name": name,
        "class_tag": class_tag,
        "hidden_root_cause": hidden_root_cause,
        "visible_test_sensitive": visible_test_sensitive,
        "root_cause_only_with_exploration": root_cause_only_with_exploration,
        "handbook_citations": list(handbook_citations),
        "issue": issue,
        "traceback_text": traceback_text,
        "traceback_files": list(traceback_files),
        "repo": repo,
        "hidden": hidden,
        "ref": ref,
        "mutant1": mutant1,
        "mutant2": mutant2,
        "assertions": list(assertions),
        "non_test_lines": non_test_lines,
        "non_test_files": non_test_files,
        "key": key,
    }
    TASKS.append(task_dict)
    return task_dict

def format_patch(ref_dict):
    return "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in ref_dict.items()
    )

def test_all():
    TASKS.clear()
    register_family_13(add_task)
    register_family_14(add_task)

    assert len(TASKS) == 16, f"Expected 16 tasks, got {len(TASKS)}"

    # 1. Check invariants
    forbidden_pattern = re.compile(r"(taught|stated|distractor|transfer|visible_sensitive|_visible|_hidden)", re.IGNORECASE)
    hint_regex = re.compile(r"#\s*(BUG|FIX|TODO|HACK)", re.IGNORECASE)

    for t in TASKS:
        tid = t["id"]
        # Hint comments
        for path, content in t["repo"].items():
            m = hint_regex.search(content)
            assert m is None, f"Task {tid} file {path} has hint comment: {m.group(0)}"
        for path, content in t["hidden"].items():
            m = hint_regex.search(content)
            assert m is None, f"Task {tid} hidden file {path} has hint comment: {m.group(0)}"

        # Line counts
        assert 40 <= t["non_test_lines"] <= 120, f"Task {tid} non-test lines {t['non_test_lines']} not in [40, 120]"
        assert 2 <= len(t["non_test_files"]) <= 3, f"Task {tid} non-test files count {len(t['non_test_files'])} not in [2, 3]"
        assert 3 <= len(t["repo"]) <= 4, f"Task {tid} total repo files {len(t['repo'])} not in [3, 4]"

        # Design words
        tb = t["traceback_text"]
        m = forbidden_pattern.search(tb)
        assert m is None, f"Task {tid} traceback contains design word: {m.group(0)}"

        for fn, content in t["hidden"].items():
            assert "hidden" not in fn.lower(), f"Task {tid} hidden test filename {fn} has 'hidden'"
            test_funcs = re.findall(r"def (test_[a-zA-Z0-9_]+)", content)
            for tf in test_funcs:
                m = forbidden_pattern.search(tf)
                assert m is None, f"Task {tid} test func {tf} has design word: {m.group(0)}"

        for fn, content in t["repo"].items():
            if fn.startswith("tests/"):
                test_funcs = re.findall(r"def (test_[a-zA-Z0-9_]+)", content)
                for tf in test_funcs:
                    m = forbidden_pattern.search(tf)
                    assert m is None, f"Task {tid} visible test func {tf} has design word: {m.group(0)}"

        # Reachability
        tb_file = t["traceback_files"][0]
        test_code = "\n".join(c for path, c in t["repo"].items() if path.startswith("tests/"))
        for p in t["non_test_files"]:
            mod_name = p[:-3]
            if p == tb_file:
                assert re.search(r"\b" + mod_name + r"\b", test_code), (
                    f"Task {tid}: Entrypoint {p} not imported by tests"
                )
            else:
                non_test_code = "\n".join(c for path, c in t["repo"].items() if not path.startswith("tests/") and path != p)
                assert re.search(r"\b" + mod_name + r"\b", non_test_code), (
                    f"Task {tid}: Helper {p} not imported by other repo code"
                )

        if t["hidden_root_cause"]:
            tb_content = t["repo"][tb_file]
            rc_files = [f for f in t["ref"] if f != tb_file and not f.startswith("tests/")]
            for rc in rc_files:
                mod_name = rc[:-3]
                assert re.search(r"\b" + mod_name + r"\b", tb_content), (
                    f"Task {tid}: HRC root-cause file {rc} not imported by traceback file {tb_file}"
                )

    print("Static integrity and reachability checks passed!")

    # 2. Dynamic execution validation with grader
    for t in TASKS:
        tid = t["id"]
        # Baseline unpatched fails hidden tests
        res = evaluate_patch(t["repo"], "", t["key"])
        assert res["strict_pass"] is False, f"Task {tid} unpatched unexpectedly passed!"

        # Gold patch passes 100%
        gold_patch = format_patch(t["ref"])
        res = evaluate_patch(t["repo"], gold_patch, t["key"])
        assert res["strict_pass"] is True, (
            f"Task {tid} gold patch failed: violations={res.get('violations')}, "
            f"vis_rc={res.get('visible_rc')}, failing_variants={res.get('failing_variants')}, "
            f"output={res.get('visible_output')}"
        )

        # Mutant 1 fails
        m1_patch = format_patch(t["mutant1"])
        res = evaluate_patch(t["repo"], m1_patch, t["key"])
        assert res["strict_pass"] is False, f"Task {tid} mutant1 unexpectedly passed!"

        # Mutant 2 fails
        m2_patch = format_patch(t["mutant2"])
        res = evaluate_patch(t["repo"], m2_patch, t["key"])
        assert res["strict_pass"] is False, f"Task {tid} mutant2 unexpectedly passed!"

        print(f"Task {tid} ({t['name']}) verified: Unpatched FAIL, Gold PASS, M1 FAIL, M2 FAIL.")

    print("\nALL 16 TASKS IN FAMILIES 13 & 14 PERFECTLY VALIDATED!")

if __name__ == "__main__":
    test_all()
