"""runner/build_triage_table.py: Exhaustive literal extraction and triage across all hidden test assertions.
"""

import os
import sys
import ast
import re
import pathlib

repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "benchmarks"))
sys.path.insert(0, str(repo_root / "runner"))

import suite_e5

handbook_path = repo_root / "briefs" / "HANDBOOK.md"
handbook_text = handbook_path.read_text(encoding="utf-8")

def analyze_all_literals(handbook_str=None):
    if handbook_str is None:
        handbook_str = handbook_text

    string_literals = []
    numeric_literals = []

    for t in suite_e5.T:
        tid = t["id"]
        fam = t["family"]
        tag = t["class_tag"]
        if tag not in ("TAUGHT", "TRANSFER", "DISTRACTOR"):
            continue

        cites = t.get("handbook_citations", [])
        issue = t.get("issue", "")
        repo_code = "\n".join(t["repo"].values())
        ctx = handbook_str + "\n" + issue + "\n" + repo_code

        hidden_code = ""
        for v in t["key"].get("variants", []):
            for path, code in v.get("overlay", {}).items():
                hidden_code += "\n" + code

        tree = ast.parse(hidden_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant):
                        val = child.value
                        if val is True or val is False or val is None:
                            continue
                        if isinstance(val, (str, bytes)):
                            val_str = val if isinstance(val, str) else repr(val)
                            if not val_str.strip():
                                continue
                            in_ctx = val_str in ctx
                            string_literals.append({
                                "task_id": tid,
                                "family": fam,
                                "tag": tag,
                                "citation": cites[0] if cites else "",
                                "literal": val_str,
                                "in_context": in_ctx,
                                "type": "str" if isinstance(val, str) else "bytes"
                            })
                        elif isinstance(val, (int, float)):
                            in_ctx = str(val) in ctx
                            numeric_literals.append({
                                "task_id": tid,
                                "family": fam,
                                "tag": tag,
                                "citation": cites[0] if cites else "",
                                "literal": val,
                                "in_context": in_ctx,
                                "type": type(val).__name__
                            })

    return string_literals, numeric_literals

if __name__ == "__main__":
    strs, nums = analyze_all_literals()
    missing_strs = [s for s in strs if not s["in_context"]]
    missing_nums = [n for n in nums if not n["in_context"]]
    print(f"Total string/bytes assert literals: {len(strs)}, Missing from verbatim context: {len(missing_strs)}")
    print(f"Total numeric assert literals: {len(nums)}, Missing from verbatim context: {len(missing_nums)}")
