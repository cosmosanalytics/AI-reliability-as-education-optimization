#!/usr/bin/env python3
"""Unit tests and preflight verification for programmatic brief builder."""

import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runner"))
import build_briefs


class TestBriefBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_briefs.generate_all_briefs()
        cls.handbook_text, cls.practice_text, cls.placebo_text = build_briefs.load_source_files()

    def test_all_16_cells_generated(self):
        self.assertEqual(len(self.manifest), 16)
        expected_cells = {
            f"C{s}{p}{u}{r}"
            for s in [0, 1]
            for p in [0, 1]
            for u in [0, 1]
            for r in [0, 1]
        }
        self.assertEqual(set(self.manifest.keys()), expected_cells)

    def test_sources_handbook_invariant(self):
        handbook_clean = self.handbook_text.strip()
        for code, m in self.manifest.items():
            brief_path = os.path.join(build_briefs.BRIEFS_DIR, f"{code}.md")
            text = open(brief_path, "r", encoding="utf-8").read()

            if m["s"] == 1:
                self.assertIn(handbook_clean, text, f"{code} must contain HANDBOOK.md verbatim")
                self.assertIn("### Rule H01: Test Directory Protection", text)
                self.assertIn("### Rule H16: Rate Limiting Token Bucket Integer Truncation", text)
                self.assertIn("ERR_RESOURCE_LOCKED", text)
            else:
                self.assertNotIn("# Engineering Standards and House Conventions (`HANDBOOK.md`)", text)
                self.assertNotIn("### Rule H01: Test Directory Protection", text)
                self.assertNotIn("### Rule H04: Structured Service Exception Hierarchy", text)
                self.assertNotIn("ERR_RESOURCE_LOCKED", text)

    def test_practice_examples_invariant(self):
        practice_clean = self.practice_text.strip()
        for code, m in self.manifest.items():
            brief_path = os.path.join(build_briefs.BRIEFS_DIR, f"{code}.md")
            text = open(brief_path, "r", encoding="utf-8").read()

            if m["p"] == 1:
                self.assertIn(practice_clean, text, f"{code} must contain P3.md verbatim")
                self.assertIn("Practice Examples (`briefs/P3.md`)", text)
                self.assertIn("Example 1: Monetary Calculation", text)
            else:
                self.assertNotIn("Practice Examples (`briefs/P3.md`)", text)
                self.assertNotIn("Example 1: Monetary Calculation", text)

    def test_placebo_contamination_prevention(self):
        for code in self.manifest:
            brief_path = os.path.join(build_briefs.BRIEFS_DIR, f"{code}.md")
            text = open(brief_path, "r", encoding="utf-8").read()
            self.assertNotIn("PLACEBO.md", text)
            self.assertNotIn("Placebo Engineering Standards", text)

    def test_unchanged_cells_byte_identity(self):
        """Verify that C0000, C0001, C0010, C0011 match previous Screening A hashes in rows.json."""
        rows_path = os.path.join(build_briefs.REPO_ROOT, "results", "screening", "rows.json")
        if os.path.exists(rows_path):
            rows = json.load(open(rows_path, "r", encoding="utf-8"))
            for code in ["C0000", "C0001", "C0010", "C0011"]:
                expected_sha = {r["brief_sha256"] for r in rows if r["cell"] == code}.pop()
                actual_sha = self.manifest[code]["sha256"]
                self.assertEqual(
                    actual_sha,
                    expected_sha,
                    f"Cell {code} hash changed! Expected {expected_sha}, got {actual_sha}",
                )

    def test_resolution_v_defining_relation(self):
        for code, m in self.manifest.items():
            s, p, u, r, k = m["s"], m["p"], m["u"], m["r"], m["k"]
            expected_k = 1 if ((s + p + u + r) % 2 == 0) else 0
            self.assertEqual(k, expected_k, f"Parity mismatch in {code}")


if __name__ == "__main__":
    unittest.main()
