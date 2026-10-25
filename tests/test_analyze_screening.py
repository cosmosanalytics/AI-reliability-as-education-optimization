import json
import math
import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))

import analyze_screening
from analyze_screening import (
    wilson_ci,
    compute_parity_k,
    build_16_cell_table,
    compute_effects_with_task_clustering,
    select_winning_condition,
    build_tune_taught_table,
    audit_execution_integrity,
    generate_markdown_report
)


class TestAnalyzeScreening(unittest.TestCase):
    def test_wilson_ci_bounds(self):
        """Verifies Wilson score confidence intervals for standard proportions and edge cases."""
        l, h = wilson_ci(0, 0)
        self.assertEqual((l, h), (0.0, 0.0))

        l, h = wilson_ci(0, 10)
        self.assertEqual(l, 0.0)
        self.assertTrue(0.0 < h < 35.0)

        l, h = wilson_ci(10, 10)
        self.assertTrue(65.0 < l < 100.0)
        self.assertAlmostEqual(h, 100.0, places=4)

        l, h = wilson_ci(5, 10)
        self.assertTrue(20.0 < l < 50.0)
        self.assertTrue(50.0 < h < 80.0)
        self.assertAlmostEqual((l + h) / 2.0, 50.0, delta=1.0)

    def test_parity_rule(self):
        """Verifies Resolution-V defining relation I = spurk."""
        # Even sum -> k = 1
        self.assertEqual(compute_parity_k(0, 0, 0, 0), 1)
        self.assertEqual(compute_parity_k(1, 1, 0, 0), 1)
        self.assertEqual(compute_parity_k(1, 1, 1, 1), 1)
        # Odd sum -> k = 0
        self.assertEqual(compute_parity_k(1, 0, 0, 0), 0)
        self.assertEqual(compute_parity_k(0, 1, 0, 0), 0)
        self.assertEqual(compute_parity_k(1, 1, 1, 0), 0)

    def test_winner_selection_criteria(self):
        """Verifies all 3 criteria of Section 8.3 theta* selection rule."""
        calibrated_tasks = [2006, 2013, 2014, 2029, 2038]

        # Mock rows where C1100 and C1001 are within 1.0 pp tie window
        # C1100: s=1, p=1, u=0, r=0, k=1 -> cognitive load = 3
        # C1001: s=1, p=0, u=0, r=1, k=1 -> cognitive load = 3
        # C0000: s=0, p=0, u=0, r=0, k=1 -> cognitive load = 1
        mock_rows = []
        for i in range(10):
            mock_rows.append({
                "cell": "C0000", "s": 0, "p": 0, "u": 0, "r": 0, "k": 1,
                "ticket": 2006, "final_strict": i < 6, "total_billed_tokens": 1000, "cost_usd": 0.002
            })
        for i in range(10):
            mock_rows.append({
                "cell": "C1100", "s": 1, "p": 1, "u": 0, "r": 0, "k": 1,
                "ticket": 2006, "final_strict": i < 9, "total_billed_tokens": 2000, "cost_usd": 0.004
            })
        for i in range(10):
            mock_rows.append({
                "cell": "C1001", "s": 1, "p": 0, "u": 0, "r": 1, "k": 1,
                "ticket": 2006, "final_strict": i < 9, "total_billed_tokens": 2000, "cost_usd": 0.004
            })

        sel = select_winning_condition(mock_rows, calibrated_tasks)
        # Between C1100 (s=1, p=1) and C1001 (s=1, p=0, r=1),
        # Hierarchy s > p > u > r > k: s are equal (1), but p=1 for C1100 vs p=0 for C1001.
        self.assertEqual(sel["winner"]["cell"], "C1100")

    def test_cognitive_load_tiebreaker(self):
        """Verifies Criterion 2: minimal cognitive load breaks ties within 1.0 pp."""
        calibrated_tasks = [2006]
        mock_rows = []
        # Cell A: C0000 (s=0, p=0, u=0, r=0, k=1) -> cog load = 1, pass rate = 100%
        for i in range(10):
            mock_rows.append({
                "cell": "C0000", "s": 0, "p": 0, "u": 0, "r": 0, "k": 1,
                "ticket": 2006, "final_strict": True, "total_billed_tokens": 1000, "cost_usd": 0.002
            })
        # Cell B: C1111 (s=1, p=1, u=1, r=1, k=1) -> cog load = 5, pass rate = 100%
        for i in range(10):
            mock_rows.append({
                "cell": "C1111", "s": 1, "p": 1, "u": 1, "r": 1, "k": 1,
                "ticket": 2006, "final_strict": True, "total_billed_tokens": 5000, "cost_usd": 0.010
            })

        sel = select_winning_condition(mock_rows, calibrated_tasks)
        self.assertEqual(sel["winner"]["cell"], "C0000")
        self.assertEqual(sel["min_cognitive_load"], 1)

    def test_audit_integrity(self):
        """Verifies audit metrics and financial spend threshold checks."""
        mock_rows = [
            {"cell": "C0000", "s": 0, "p": 0, "u": 0, "r": 0, "k": 1, "ticket": 2001,
             "call_count": 1, "tokens_in": 1000, "tokens_out": 200, "thoughts_tokens": 500,
             "total_billed_tokens": 1700, "cost_usd": 0.002, "stop_reason": "FinishReason.STOP",
             "violations": []}
        ]
        audit = audit_execution_integrity(mock_rows)
        self.assertEqual(audit["total_attempts"], 1)
        self.assertEqual(audit["truncations_count"], 0)
        self.assertEqual(audit["api_errors_count"], 0)
        self.assertEqual(audit["policy_violations_count"], 0)
        self.assertFalse(audit["cost_cap_breached"])
        self.assertFalse(audit["pause_threshold_triggered"])

    def test_screening_analysis_pipeline_live(self):
        """Verifies the pipeline on the live screening rows file."""
        rows_path = os.path.join(REPO_ROOT, "results", "screening", "rows.json")
        if not os.path.exists(rows_path):
            return

        with open(rows_path, "r", encoding="utf-8") as f:
            rows = json.load(f)

        tbl = build_16_cell_table(rows)
        self.assertEqual(len(tbl), 16)
        for c in tbl:
            self.assertGreaterEqual(c["attempts"], 0)
            self.assertTrue(0.0 <= c["rate_pct"] <= 100.0)

        eff = compute_effects_with_task_clustering(rows)
        self.assertEqual(len(eff["main_effects"]), 5)
        self.assertEqual(len(eff["interactions"]), 10)

        sel = select_winning_condition(rows, analyze_screening.FALLBACK_CALIBRATED_TUNE_TASKS)
        self.assertIsNotNone(sel["winner"])
        self.assertIn(sel["winner"]["cell"], [c["cell"] for c in tbl])


if __name__ == "__main__":
    unittest.main()
