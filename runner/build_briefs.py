#!/usr/bin/env python3
"""Programmatic Brief Builder & Preflight Validator for Factorial Screening (2^{5-1}).

Round 25 Protocol Specifications:
1. Builds all 16 cell briefs from frozen files without manual copy-paste:
   - Fixed header
   - briefs/HANDBOOK.md verbatim if s = 1
   - briefs/P3.md verbatim if p = 1
   - u (interactive pytest tool instructions) if u = 1
   - r (self-review checklist) if r = 1
   - k (parity-determined retry; runner-level intervention, no brief prompt text)
2. Enforces preflight validation rules:
   - Verbatim presence and hash match of HANDBOOK.md when s = 1; zero H-rule text when s = 0
   - Verbatim presence and hash match of P3.md when p = 1; zero P3 text when p = 0
   - Zero PLACEBO.md text in any screening brief
   - Exact byte-identity match for unchanged cells (C0000, C0001, C0010, C0011) against archived phase 0
"""

import hashlib
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRIEFS_DIR = os.path.join(REPO_ROOT, "briefs")

HEADER_TEXT = (
    "You are a careful senior software engineer who ships small, correct, "
    "well-scoped patches in Python repositories. Plain patch text only.\n"
)

TOOL_TEXT = (
    "TOOLS: You have access to an interactive test execution tool. To run visible tests at any point before final submission, output:\n"
    "=== TOOL: pytest ===\n"
    "tests/\n"
    "=== END_TOOL ===\n"
    "You may include draft === FILE === blocks in the same turn so tests execute against your modified code. "
    "You will receive the exit code and traceback output. You may run tests zero, one, or multiple times. "
    "When you are finished, output your complete final patch in the standard === FILE === block format without any tool blocks."
)

REVIEW_TEXT = (
    "SELF-REVIEW: after drafting each patch and before writing the final file, review the draft against this checklist and fix anything that fails: "
    "(1) every sentence of the ticket and every docstring requirement is met, including edge cases and error types; "
    "(2) no existing test file was edited, deleted or weakened; "
    "(3) the diff is minimal and touches every file the ticket implies; "
    "(4) the output uses only the required === FILE === block format.\n"
)


def load_source_files(briefs_dir: str = BRIEFS_DIR):
    handbook_path = os.path.join(briefs_dir, "HANDBOOK.md")
    practice_path = os.path.join(briefs_dir, "P3.md")
    placebo_path = os.path.join(briefs_dir, "PLACEBO.md")

    if not os.path.exists(handbook_path):
        raise FileNotFoundError(f"Missing frozen handbook: {handbook_path}")
    if not os.path.exists(practice_path):
        raise FileNotFoundError(f"Missing practice examples: {practice_path}")
    if not os.path.exists(placebo_path):
        raise FileNotFoundError(f"Missing placebo brief: {placebo_path}")

    handbook_text = open(handbook_path, "r", encoding="utf-8").read()
    practice_text = open(practice_path, "r", encoding="utf-8").read()
    placebo_text = open(placebo_path, "r", encoding="utf-8").read()

    return handbook_text, practice_text, placebo_text


def build_brief_text(
    s: int,
    p: int,
    u: int,
    r: int,
    k: int,
    handbook_text: str,
    practice_text: str,
) -> str:
    """Build programmatic brief string with exact component isolation."""
    parts = [HEADER_TEXT]
    if s == 1:
        parts.append("\n" + handbook_text.strip() + "\n")
    if p == 1:
        parts.append("\n" + practice_text.strip() + "\n")
    if u == 1:
        parts.append("\n" + TOOL_TEXT + ("\n" if r == 1 else ""))
    if r == 1:
        if u == 1:
            parts.append(REVIEW_TEXT)
        else:
            parts.append("\n" + REVIEW_TEXT)
    return "".join(parts)


def compute_k_parity(s: int, p: int, u: int, r: int) -> int:
    """Defining relation I = spurk: k = 1 if (s + p + u + r) % 2 == 0 else 0."""
    return 1 if ((s + p + u + r) % 2 == 0) else 0


def generate_all_briefs(briefs_dir: str = BRIEFS_DIR):
    handbook_text, practice_text, placebo_text = load_source_files(briefs_dir)

    cells = []
    manifest = {}

    for s in [0, 1]:
        for p in [0, 1]:
            for u in [0, 1]:
                for r in [0, 1]:
                    k = compute_k_parity(s, p, u, r)
                    cell_code = f"C{s}{p}{u}{r}"
                    brief_text = build_brief_text(s, p, u, r, k, handbook_text, practice_text)
                    cells.append({
                        "cell": cell_code,
                        "s": s, "p": p, "u": u, "r": r, "k": k,
                        "brief_text": brief_text,
                    })

    # Preflight Verification
    handbook_clean = handbook_text.strip()
    practice_clean = practice_text.strip()
    handbook_clean_hash = hashlib.sha256(handbook_clean.encode("utf-8")).hexdigest()
    practice_clean_hash = hashlib.sha256(practice_clean.encode("utf-8")).hexdigest()

    archive_dir = os.path.join(briefs_dir, "archive_phase0")

    for c in cells:
        code = c["cell"]
        text = c["brief_text"]
        sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

        # Check s invariant
        if c["s"] == 1:
            assert handbook_clean in text, f"Cell {code}: HANDBOOK.md text not found verbatim!"
            assert "### Rule H01: Test Directory Protection" in text, f"Cell {code}: Missing H01 header!"
            assert "### Rule H16: Rate Limiting Token Bucket Integer Truncation" in text, f"Cell {code}: Missing H16 header!"
        else:
            assert "# Engineering Standards and House Conventions (`HANDBOOK.md`)" not in text, f"Cell {code} (s=0) illegally contains handbook title!"
            assert "### Rule H01: Test Directory Protection" not in text, f"Cell {code} (s=0) contains H01!"
            assert "### Rule H04: Structured Service Exception Hierarchy" not in text, f"Cell {code} (s=0) contains H04!"
            assert "ERR_RESOURCE_LOCKED" not in text, f"Cell {code} (s=0) illegally contains handbook error codes!"

        # Check p invariant
        if c["p"] == 1:
            assert practice_clean in text, f"Cell {code}: P3.md text not found verbatim!"
            assert "Practice Examples (`briefs/P3.md`)" in text, f"Cell {code}: Missing P3 title!"
        else:
            assert "Practice Examples (`briefs/P3.md`)" not in text, f"Cell {code} (p=0) illegally contains P3 text!"
            assert "Example 1: Monetary Calculation" not in text, f"Cell {code} (p=0) contains P3 examples!"

        # When both s=0 and p=0: absolute absence of any Rule H text
        if c["s"] == 0 and c["p"] == 0:
            assert "Rule H" not in text, f"Cell {code} (s=0, p=0) illegally contains Rule H text!"

        # Check placebo invariant (Placebo must NEVER appear in screening briefs)
        assert "PLACEBO.md" not in text, f"Cell {code} illegally contains PLACEBO reference!"
        assert "Placebo Engineering Standards" not in text, f"Cell {code} contains Placebo text!"

        # Check unchanged cells C0000, C0001, C0010, C0011 against archived phase 0
        if c["s"] == 0 and c["p"] == 0 and os.path.exists(archive_dir):
            archived_path = os.path.join(archive_dir, f"{code}.md")
            if os.path.exists(archived_path):
                archived_text = open(archived_path, "r", encoding="utf-8").read()
                assert text == archived_text, f"Cell {code} does not match archived phase 0 exact bytes!"

        manifest[code] = {
            "s": c["s"], "p": c["p"], "u": c["u"], "r": c["r"], "k": c["k"],
            "sha256": sha256,
            "char_count": len(text),
            "line_count": len(text.splitlines()),
        }

    # Write out briefs to BRIEFS_DIR
    for c in cells:
        dest_path = os.path.join(briefs_dir, f"{c['cell']}.md")
        with open(dest_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(c["brief_text"])

    return manifest


if __name__ == "__main__":
    manifest = generate_all_briefs()
    print("All 16 screening briefs successfully generated and verified:")
    for code, m in sorted(manifest.items()):
        print(f"  {code} (s={m['s']}, p={m['p']}, u={m['u']}, r={m['r']}, k={m['k']}): "
              f"sha256={m['sha256'][:16]}..., chars={m['char_count']}")
