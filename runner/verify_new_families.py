import os
import sys
import re
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from grader import evaluate_patch

def verify_family(register_fn, family_name, expected_ids):
    tasks = []
    def add_task(**kwargs):
        if "tid" in kwargs and "id" not in kwargs:
            kwargs["id"] = kwargs["tid"]
        tasks.append(kwargs)

    register_fn(add_task)
    print(f"\n==========================================")
    print(f"Verifying {family_name}: {len(tasks)} tasks")
    print(f"==========================================")
    assert len(tasks) == len(expected_ids), f"Expected {len(expected_ids)} tasks, got {len(tasks)}"

    forbidden_pattern = re.compile(r"(taught|stated|distractor|transfer|visible_sensitive|_visible|_hidden)", re.IGNORECASE)
    hint_regex = re.compile(r"#\s*(BUG|FIX|TODO|HACK)", re.IGNORECASE)

    def format_patch(ref_dict):
        return "".join(f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n" for p, c in ref_dict.items())

    for t in tasks:
        tid = t["id"]
        assert tid in expected_ids, f"Unexpected tid {tid}"
        tag = t["class_tag"]
        tb = t["traceback_text"]
        print(f"--- Task {tid} ({tag}) ---")

        # 1. No hint comments
        for p, c in t["repo"].items():
            m = hint_regex.search(c)
            assert m is None, f"Task {tid} file {p} has hint comment: {m.group(0)}"

        # 2. Neutral test names & tracebacks
        assert forbidden_pattern.search(tb) is None, f"Task {tid} traceback contains forbidden word: {tb}"
        for fn, c in t["hidden"].items():
            assert "hidden" not in fn.lower(), f"Task {tid} hidden file contains 'hidden': {fn}"
            for tf in re.findall(r"def (test_[a-zA-Z0-9_]+)", c):
                assert forbidden_pattern.search(tf) is None, f"Task {tid} hidden test {tf} has forbidden word"
        for fn, c in t["repo"].items():
            if fn.startswith("tests/"):
                for tf in re.findall(r"def (test_[a-zA-Z0-9_]+)", c):
                    assert forbidden_pattern.search(tf) is None, f"Task {tid} visible test {tf} has forbidden word"

        # 3. 40-120 non-test lines across 3-4 files
        non_test_files = [p for p in t["repo"] if not p.startswith("tests/")]
        non_test_lines = sum(len(t["repo"][p].splitlines()) for p in non_test_files)
        assert 3 <= len(non_test_files) <= 4, f"Task {tid} has {len(non_test_files)} non-test files"
        assert 40 <= non_test_lines <= 120, f"Task {tid} has {non_test_lines} non-test lines"
        print(f"  Files: {len(non_test_files)}, Lines: {non_test_lines}")

        # 4. Reachability: 100% on reachability path, zero decoys
        tb_file = t["traceback_files"][0]
        test_code = "\n".join(c for path, c in t["repo"].items() if path.startswith("tests/"))
        assert re.search(r"\b" + tb_file[:-3] + r"\b", test_code), f"Task {tid}: {tb_file} not imported by tests"
        for p in non_test_files:
            mod_name = p[:-3]
            if p != tb_file:
                other_code = "\n".join(c for path, c in t["repo"].items() if not path.startswith("tests/") and path != p)
                assert re.search(r"\b" + mod_name + r"\b", other_code), f"Task {tid}: {p} not imported by non-test code"

        # 5. Build key for evaluation
        vis = [p for p in t["repo"] if p.startswith("tests/")]
        key = {
            "visible_paths": list(vis),
            "protected": list(vis),
            "forbidden": [],
            "must_touch": [],
            "variants": [
                {
                    "name": "hidden tests",
                    "overlay": t["hidden"],
                    "expect": "pass",
                    "paths": ["tests"],
                }
            ],
        }

        # 6. Unpatched baseline fails hidden tests
        res_un = evaluate_patch(t["repo"], "", key)
        assert res_un["strict_pass"] is False, f"Task {tid} unpatched unexpectedly passed!"
        print("  Unpatched fails: OK")

        # 7. Gold reference passes 100%
        res_gold = evaluate_patch(t["repo"], format_patch(t["ref"]), key)
        assert res_gold["strict_pass"] is True, f"Task {tid} gold failed: {res_gold}"
        assert res_gold["func_pass"] is True
        assert len(res_gold["violations"]) == 0
        print("  Gold passes 100%: OK")

        # 8. Mutant 1 fails
        res_m1 = evaluate_patch(t["repo"], format_patch(t["mutant1"]), key)
        assert res_m1["strict_pass"] is False, f"Task {tid} mutant1 unexpectedly passed!"
        print("  Mutant 1 fails: OK")

        # 9. Mutant 2 fails
        res_m2 = evaluate_patch(t["repo"], format_patch(t["mutant2"]), key)
        assert res_m2["strict_pass"] is False, f"Task {tid} mutant2 unexpectedly passed!"
        print("  Mutant 2 fails: OK")

    print(f"\nALL {len(tasks)} TASKS IN {family_name} VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    from family8_errors import register_family_8
    from family9_wire import register_family_9
    from family10_timestamp import register_family_10
    from family11_lists import register_family_11
    from family12_idempotency import register_family_12
    from family13_percentiles import register_family_13
    from family14_transitions import register_family_14

    verify_family(register_family_8, "family8_errors", list(range(2029, 2037)))
    verify_family(register_family_9, "family9_wire", list(range(2037, 2045)))
    verify_family(register_family_10, "family10_timestamp", list(range(2045, 2053)))
    verify_family(register_family_11, "family11_lists", list(range(2053, 2061)))
    verify_family(register_family_12, "family12_idempotency", list(range(2061, 2069)))
    verify_family(register_family_13, "family13_percentiles", list(range(2069, 2077)))
    verify_family(register_family_14, "family14_transitions", list(range(2077, 2085)))
