import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner", "swe2"))

import harness  # noqa: E402
import ontology  # noqa: E402
import quiz_items  # noqa: E402
import run_swe2  # noqa: E402


class TestSwe2Harness(unittest.TestCase):
    def test_graph_literals_grounded_in_handbook(self):
        with open(os.path.join(REPO_ROOT, "briefs", "HANDBOOK.md"), encoding="utf-8") as f:
            hb = f.read()
        self.assertEqual(ontology.verify_grounding(ontology.build(), hb), [])

    def test_triples_reference_known_nodes_and_relations(self):
        for src in ("handbook", "placebo"):
            g = ontology.build(src)
            for s, p, o in g["triples"]:
                self.assertIn(s, g["nodes"])
                self.assertIn(o, g["nodes"])
                self.assertIn(p, ontology.RELATIONS)

    def test_prompt_never_contains_handbook_prose(self):
        with open(os.path.join(REPO_ROOT, "briefs", "HANDBOOK.md"), encoding="utf-8") as f:
            hb = f.read()
        sentences = [s.strip() for s in hb.replace("\n", " ").split(". ") if len(s.strip()) > 60]
        for arm in run_swe2.ARMS:
            prompt, _ = run_swe2.build_first_prompt(arm, run_swe2.TASKS_BY_ID[2002])
            self.assertNotIn("HANDBOOK", prompt)
            for s in sentences:
                self.assertNotIn(s, prompt)

    def test_retrieval_top3_contains_family_rule(self):
        for fam, tasks in run_swe2.FAMILY_TASKS.items():
            for tid in tasks:
                ids = harness.retrieve(run_swe2.ticket_text(run_swe2.TASKS_BY_ID[tid]), 3)
                self.assertIn(run_swe2.FAMILY_TO_RULE[fam], ids, (fam, tid))

    def test_quiz_items_point_to_graph_nodes(self):
        nodes = ontology.build()["nodes"]
        self.assertEqual(set(quiz_items.ITEMS), set(run_swe2.FAMILY_TO_RULE.values()))
        for rule, items in quiz_items.ITEMS.items():
            for kg, stem, correct, distractors in items:
                self.assertTrue(kg.startswith(rule), kg)
                self.assertIn(kg, nodes)
                self.assertEqual(len(distractors), 3)
                self.assertNotIn(correct, distractors)

    def test_calibration_map_is_monotone(self):
        pairs = [(0.9, 0), (0.9, 1), (0.95, 0), (0.5, 1), (0.3, 0), (0.8, 0)]
        cmap = run_swe2.fit_calibration(pairs)
        ps = [b["p"] for b in cmap["bins"]]
        self.assertEqual(ps, sorted(ps))
        self.assertAlmostEqual(run_swe2.calibrate(1.0, cmap), ps[-1])

    def test_parse_diag(self):
        d = run_swe2.parse_diag("ROOT_CAUSE: tax_engine.py::calculate_vat\nRULE: H02\nCONFIDENCE: 85")
        self.assertEqual(d["root_cause_norm"], "tax_engine.py::calculate_vat")
        self.assertEqual(d["rule_norm"], "H02")
        self.assertAlmostEqual(d["confidence"], 0.85)
        d = run_swe2.parse_diag("ROOT_CAUSE: `sorter.py::sort_batch` where the sort key uses msg_id\nRULE: H07")
        self.assertEqual(d["root_cause_norm"], "sorter.py::sort_batch")
        d = run_swe2.parse_diag("ROOT_CONFIDENCE: discount::prorate_discount\nCONFIDENCE: 85")
        self.assertEqual(d["root_cause_norm"], "discount::prorate_discount")
        self.assertAlmostEqual(d["confidence"], 0.85)



class TestSandboxEdits(unittest.TestCase):
    def test_edit_blocks_apply_and_submit_sandbox_state(self):
        sb = run_swe2.Sandbox({"a.py": "def f():\n    return 1   \n", "tests/test_a.py": "x = 1\n"})
        changed, errs = sb.apply("=== EDIT: a.py ===\n<<<<<<< SEARCH\n    return 1\n=======\n    return 2\n"
                                 ">>>>>>> REPLACE\n=== END ===\n=== EDIT: a.py ===\n<<<<<<< SEARCH\nnope\n=======\nx\n"
                                 ">>>>>>> REPLACE\n=== END ===\n")
        self.assertEqual(changed, ["a.py"])
        self.assertEqual(len(errs), 1)
        self.assertIn("return 2", sb.draft_patch())
        self.assertNotIn("tests/test_a.py", sb.draft_patch())

if __name__ == "__main__":
    unittest.main()
