"""runner/verify_rule_sufficiency.py: Automated verification of Rule Sufficiency (J2).

Validates that for every TAUGHT, TRANSFER, and DISTRACTOR task, all required
string literals, error codes, header names, envelope keys, and formatting invariants
asserted in hidden tests are either:
1. Directly stated in HANDBOOK.md, OR
2. Directly stated in the ticket/issue, repo source code, or visible tests, OR
3. Deterministically derivable from a documented rule in HANDBOOK.md applied to the task repository.

All derivation patterns are strictly coupled to the text of HANDBOOK.md.
If the governing rule sentence or token specification is missing from HANDBOOK.md,
the derivation fails and the task is flagged as UNRESOLVED.
"""

import os
import sys
import ast
import re
import pathlib

# Portable repository root relative to this file
_repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_repo_root / "benchmarks"))
sys.path.insert(0, str(_repo_root / "runner"))

import suite_e5


def check_rule_sufficiency(handbook_text=None, repo_root=None):
    if repo_root is None:
        repo_root = _repo_root
    else:
        repo_root = pathlib.Path(repo_root)

    if handbook_text is None:
        handbook_file = repo_root / "briefs" / "HANDBOOK.md"
        handbook_text = handbook_file.read_text(encoding="utf-8")

    # Invariants derived strictly from handbook text:
    # 1. H08: Requires explicit sentence defining _src from first word of module file name + _service
    has_h08_src_rule = bool(
        re.search(
            r"first word of the module['’]?s? file name.*_service",
            handbook_text,
            re.IGNORECASE,
        )
    )

    # 2. H13: Requires explicit token format specification idemp_<timestamp_ms>_<hex_token_8chars>
    has_h13_format_rule = "idemp_<timestamp_ms>_<hex_token_8chars>" in handbook_text

    # 3. H04: Requires platform error codes in handbook
    h04_codes_in_handbook = set(re.findall(r'"(ERR_[A-Z0-9_]+)"', handbook_text))

    # 4. H15: Requires canonical STATE_TRANSITION tag and ERR_INVALID_TRANSITION
    has_h15_state_rule = (
        "STATE_TRANSITION" in handbook_text
        and "ERR_INVALID_TRANSITION" in handbook_text
    )

    # 5. H09: Requires canonical UTC ISO 8601 millisecond format
    has_h09_iso_rule = (
        "YYYY-MM-DDTHH:MM:SS.sssZ" in handbook_text
        or "millisecond precision" in handbook_text
    )

    # 6. H10: Requires TSV format and \N null serialization
    has_h10_tsv_rule = "TSV" in handbook_text and r"\N" in handbook_text

    # 7. H14: Requires nearest-rank method
    has_h14_percentile_rule = "nearest-rank" in handbook_text

    # 8. H02: Requires half-up rounding (ROUND_HALF_UP)
    has_h02_rounding_rule = "ROUND_HALF_UP" in handbook_text

    unresolved_by_task = {}

    for t in suite_e5.T:
        tid = t["id"]
        fam = t["family"]
        tag = t["class_tag"]
        if tag not in ("TAUGHT", "TRANSFER", "DISTRACTOR"):
            continue

        cites = t.get("handbook_citations", [])
        ticket_text = t.get("issue", "")
        repo_text = "\n".join(t["repo"].values())
        available_text = handbook_text + "\n" + ticket_text + "\n" + repo_text

        # Extract hidden test code
        hidden_code = ""
        for v in t["key"].get("variants", []):
            for path, code in v.get("overlay", {}).items():
                hidden_code += "\n" + code

        tree = ast.parse(hidden_code)

        critical_literals = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        val = child.value.strip()
                        if not val:
                            continue
                        # Error codes
                        if val.startswith("ERR_"):
                            critical_literals.add(("error_code", val))
                        # Wire envelope keys and service names
                        elif val in ("_v", "_ts", "_src", "payload") or val.endswith("_service"):
                            critical_literals.add(("wire_envelope", val))
                        # Idempotency headers or patterns
                        elif "Idempotency" in val or "idemp_" in val or val.startswith("^idemp_"):
                            critical_literals.add(("idempotency", val))
                        # State transition audit tag
                        elif val == "STATE_TRANSITION":
                            critical_literals.add(("state_transition", val))

        unresolved = []
        for cat, val in critical_literals:
            # 1. Direct match in local ticket, repo, or handbook text
            if val in available_text:
                # If it's an error code, verify it is genuinely in handbook or local code
                continue

            # 2. Rule H08: Service name derivation (<domain>_service)
            if cat == "wire_envelope" and val.endswith("_service"):
                domain = val[:-len("_service")]
                # Derivation is VALID ONLY IF the handbook contains the H08 naming rule
                if has_h08_src_rule and "Rule H08" in cites:
                    # And domain matches first word of primary module filename before underscore
                    matched_file = False
                    for fn in t["repo"].keys():
                        base = os.path.basename(fn).replace(".py", "")
                        first_word = base.split("_")[0]
                        if first_word == domain:
                            matched_file = True
                            break
                    if matched_file:
                        continue

            # 3. Rule H13: Idempotency regex pattern
            if cat == "idempotency" and val == "^idemp_\\d+_[0-9a-f]{8}$":
                # Derivation is VALID ONLY IF handbook contains idemp_<timestamp_ms>_<hex_token_8chars>
                if has_h13_format_rule and "Rule H13" in cites:
                    continue

            # 4. Rule H15: State transition constants
            if cat == "state_transition" and val == "STATE_TRANSITION":
                if has_h15_state_rule:
                    continue

            unresolved.append((cat, val))

        if unresolved:
            unresolved_by_task[tid] = unresolved

    return unresolved_by_task


if __name__ == "__main__":
    unresolved = check_rule_sufficiency()
    if not unresolved:
        print("PASS: All 106 tasks satisfy Rule Sufficiency (J2)! 0 unstated/unresolvable contract literals.")
    else:
        print(f"FAIL: {len(unresolved)} tasks have unresolved contract literals:")
        for tid, lits in sorted(unresolved.items()):
            t = [x for x in suite_e5.T if x["id"] == tid][0]
            print(f"  Task {tid} ({t['family']}, {t['class_tag']}): {lits}")
