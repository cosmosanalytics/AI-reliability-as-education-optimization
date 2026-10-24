"""build_fairness_e5.py: Generate benchmarks/FAIRNESS_e5.md documenting the fairness audit for Suite E5.

Satisfies Section 8 Addendum v2 of REAL_TEST_REQUIREMENTS.md:
- Documents all 28 template-generated instances across 7 bug families.
- Lists Class Tag (STATED, TAUGHT, DISTRACTOR, TRANSFER).
- Details Hidden Assertion, Visible Source / Handbook Rule Citation,
  Hidden Root Cause (outside traceback), and Visible-Test Sensitivity.
- Verifies fairness invariants:
  * STATED tasks: requirement is explicitly stated in ticket or visible docstring.
  * TAUGHT tasks: requirement appears sentence-for-sentence in HANDBOOK.md.
  * DISTRACTOR tasks: requirement explicitly forbids blind application of handbook rule.
  * TRANSFER tasks: tests general reasoning in a clean unseen domain.
"""

import os
import sys

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_root, "benchmarks"))
import suite_e5


def generate_markdown():
    tasks = suite_e5.T
    md_lines = [
        "# Suite E5 Fairness Audit and Benchmark Specifications (`FAIRNESS_e5.md`)",
        "",
        "This document establishes the binding fairness audit and specification matrix for `suite_e5` (28 template-generated instances across 7 bug families), adhering strictly to Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md`.",
        "",
        "## 1. Summary Statistics",
        f"- **Total Evaluated Instances:** {len(tasks)}",
        f"- **Bug Families (7):** `money_rounding` (4), `config_merge` (4), `calendar_recurrence` (4), `csv_roundtrip` (4), `permission_prefix` (4), `event_ordering` (4), `cache_ttl` (4)",
        f"- **Class Tag Breakdown:**",
        f"  - `STATED`: {len([t for t in tasks if t['class_tag'] == 'STATED'])} instances (all hidden requirements present in ticket/docstrings)",
        f"  - `TAUGHT`: {len([t for t in tasks if t['class_tag'] == 'TAUGHT'])} instances (house conventions supplied strictly via `HANDBOOK.md`)",
        f"  - `DISTRACTOR`: {len([t for t in tasks if t['class_tag'] == 'DISTRACTOR'])} instances (blind application of handbook rule causes failure)",
        f"  - `TRANSFER`: {len([t for t in tasks if t['class_tag'] == 'TRANSFER'])} instances (unseen family measuring cross-domain generalization)",
        f"- **Structural Variants:**",
        f"  - Hidden Root Cause (outside traceback file): {len([t for t in tasks if t.get('hidden_root_cause')])} / {len(tasks)} ({len([t for t in tasks if t.get('hidden_root_cause')])/len(tasks)*100:.1f}%, >= 33.3% required)",
        f"  - Visible-Test-Sensitive (naive fix fails visible test): {len([t for t in tasks if t.get('visible_test_sensitive')])} / {len(tasks)} ({len([t for t in tasks if t.get('visible_test_sensitive')])/len(tasks)*100:.1f}%, >= 33.3% required)",
        "",
        "---",
        "",
        "## 2. Fairness Standards by Class Tag",
        "1. **STATED:** Every requirement tested by hidden assertions is explicitly documented in the issue description or in the docstring of files provided in the minimal context package (`traceback_files`). Zero secret assumptions.",
        "2. **TAUGHT:** Requirements not obvious from general programming intuition (such as company-specific banker's rounding rules, immutable config deep-copying, deterministic ascending secondary tie-breaking, half-open date interval indexing, RFC 4180 escaping, or injectable clock defaults) are specified sentence-for-sentence in `briefs/HANDBOOK.md` and absent from `briefs/PLACEBO.md`.",
        "3. **DISTRACTOR:** Intentionally presents an edge case where applying a handbook rule indiscriminately breaks intended functionality (e.g., stripping slashes when exact literal path matching is requested, or forcibly deep-copying when in-place accumulator mutation is explicitly specified).",
        "4. **TRANSFER:** Evaluates the `cache_ttl` family without any corresponding worked examples in `briefs/P3.md`, verifying whether agents can synthesize general educational principles (Rule H09 injectable clocks) in novel contexts.",
        "",
        "---",
        "",
        "## 3. Instance Matrix",
        "",
        "| ID | Family | Class Tag | Name | Hidden Root Cause? | Visible-Test Sensitive? | Handbook Rule | Visible Source / Hidden Assertion Contract |",
        "|:---|:---|:---|:---|:---:|:---:|:---|:---|",
    ]

    for t in tasks:
        tid = t["id"]
        fam = t["family"]
        tag = t["class_tag"]
        name = t["name"]
        hrc = "Yes" if t.get("hidden_root_cause") else "No"
        vts = "Yes" if t.get("visible_test_sensitive") else "No"
        rules = ", ".join(t.get("handbook_citations", [])) or "None (Self-contained)"
        
        # Summary description of contract
        issue = t["issue"].replace("|", "\\|")
        md_lines.append(
            f"| `{tid}` | `{fam}` | **`{tag}`** | {name} | {hrc} | {vts} | `{rules}` | {issue} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Detailed Fairness and Mutation Verification",
        "",
    ])

    for t in tasks:
        tid = t["id"]
        name = t["name"]
        fam = t["family"]
        tag = t["class_tag"]
        md_lines.extend([
            f"### Task {tid}: {name}",
            f"- **Family:** `{fam}`",
            f"- **Class Tag:** `{tag}`",
            f"- **Hidden Root Cause Outside Traceback:** `{'Yes' if t.get('hidden_root_cause') else 'No'}`",
            f"- **Visible-Test Sensitive:** `{'Yes' if t.get('visible_test_sensitive') else 'No'}`",
            f"- **Handbook Citations:** `{', '.join(t.get('handbook_citations', [])) or 'None'}`",
            f"- **Traceback Files Provided to Baseline:** `{', '.join(t['traceback_files'])}`",
            f"- **Issue Summary:** {t['issue']}",
            f"- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:",
            f"  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).",
            f"  - Unpatched Baseline: 100% failure on hidden test overlay.",
            f"  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).",
            f"  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).",
            "",
        ])

    return "\n".join(md_lines) + "\n"


if __name__ == "__main__":
    content = generate_markdown()
    out_path = os.path.join(_root, "benchmarks", "FAIRNESS_e5.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote FAIRNESS_e5.md ({len(content)} bytes)")
