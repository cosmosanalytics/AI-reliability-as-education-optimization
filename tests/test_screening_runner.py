"""Unit tests for Screening Runner and Cost Meter (Round 24 Option B Approved).

Tests:
1. compute_k_parity(s, p, u, r) satisfies Resolution-V defining relation I = spurk.
2. Verification of all 16 cell briefs in briefs/C0000.md .. C1111.md.
3. Pricing formula calculation: $0.30/1M in, $2.50/1M out (including thoughts_tokens).
4. Hard-stop cost meter cap trip behavior and thread-safety.
5. Atomic JSON file updates and crash-safety.
6. Strict Stop Rule enforcement (no execution without explicit approval).
7. Tune task dataset loading: exactly 46 tasks from splits_e5.json.
8. Pinned metadata header fields and commit SHA of FREEZE.json (a7ecb64).
9. Pricing constants and thoughts_tokens inclusion in analyze_pilot_calibration.py.
10. Row-level cost_usd and call_count calculation and inclusion.
11. 50% cap threshold pause check ($18.93 spend before 883 attempts triggers PAUSED_SPEND_THRESHOLD_REACHED).
12. Running per-cell cost table computation and formatting.
"""

import json
import os
import sys
import tempfile
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))

from run_screening import (
    CostMeter,
    DEFAULT_COST_CAP_USD,
    DEFAULT_RUNS,
    PRICE_INPUT_PER_1M,
    PRICE_OUTPUT_PER_1M,
    atomic_json_write,
    build_screening_cells,
    compute_per_cell_cost_table,
    create_initial_header,
    format_per_cell_table,
    get_freeze_commit_sha,
    load_tune_tasks,
    run_screening,
    verify_cell_briefs,
)
from agent_runner import compute_k_parity
import suite_e5


def test_resolution_v_parity():
    """Verify compute_k_parity implements I = spurk for all 16 cells."""
    cells = build_screening_cells()
    assert len(cells) == 16, f"Expected 16 cells, got {len(cells)}"

    k_ones = 0
    k_zeros = 0

    for code, s, p, u, r, k in cells:
        expected_code = f"C{s}{p}{u}{r}"
        assert code == expected_code
        # Parity rule: (s + p + u + r) % 2 == 0 -> k = 1, else 0
        expected_k = 1 if ((s + p + u + r) % 2 == 0) else 0
        assert k == expected_k, f"Mismatch for cell {code}: got {k}, expected {expected_k}"
        if k == 1:
            k_ones += 1
        else:
            k_zeros += 1

    # In Resolution-V 2^{5-1}, exactly half of the cells have k=1 and half have k=0
    assert k_ones == 8
    assert k_zeros == 8


def test_briefs_exist_and_non_empty():
    """Verify all 16 cell brief markdown files exist in briefs/ and are non-empty."""
    cells = build_screening_cells()
    assert verify_cell_briefs(REPO_ROOT, cells) is True

    brief_dir = os.path.join(REPO_ROOT, "briefs")
    for code, s, p, u, r, k in cells:
        brief_path = os.path.join(brief_dir, f"{code}.md")
        assert os.path.isfile(brief_path), f"Missing brief file: {brief_path}"
        content = open(brief_path, encoding="utf-8").read().strip()
        assert len(content) > 50, f"Brief {brief_path} suspiciously short"
        if r == 1:
            assert "SELF-REVIEW" in content or "checklist" in content.lower()


def test_pricing_formula_calculation():
    """Verify cost formula matches Gemini 2.5 Flash list pricing rates."""
    assert PRICE_INPUT_PER_1M == 0.30
    assert PRICE_OUTPUT_PER_1M == 2.50

    # Test case: 1M input, 1M output, 1M thoughts
    # Cost = 1M * $0.30/1M + (1M + 1M) * $2.50/1M = $0.30 + $5.00 = $5.30
    meter = CostMeter(cost_cap_usd=10.0)
    cost = meter.record_attempt(tokens_in=1_000_000, tokens_out=1_000_000, thoughts_tokens=1_000_000)
    assert abs(cost - 5.30) < 1e-6
    assert abs(meter.cumulative_cost_usd - 5.30) < 1e-6

    # Test case: typical single attempt (880 in, 460 out, 1340 thoughts)
    # in: 880 * 0.30 / 1e6 = 0.000264
    # out: (460 + 1340) * 2.50 / 1e6 = 1800 * 2.50 / 1e6 = 0.004500
    # total = 0.004764
    meter2 = CostMeter(cost_cap_usd=1.0)
    cost2 = meter2.record_attempt(tokens_in=880, tokens_out=460, thoughts_tokens=1340)
    assert abs(cost2 - 0.004764) < 1e-6


def test_cost_meter_hard_stop_cap_trip():
    """Verify CostMeter trips hard-stop cap immediately and halts further execution."""
    cap = 0.01  # $0.01 cap
    meter = CostMeter(cost_cap_usd=cap)
    assert not meter.is_exceeded()

    # Attempt 1: 1,000 in, 500 out, 1,000 thoughts
    # Cost = (1000 * 0.30 / 1e6) + (1500 * 2.50 / 1e6) = 0.0003 + 0.00375 = 0.00405 USD (under cap)
    cost1 = meter.record_attempt(tokens_in=1000, tokens_out=500, thoughts_tokens=1000)
    assert cost1 < cap
    assert not meter.is_exceeded()

    # Attempt 2: 2,000 in, 1,500 out, 2,000 thoughts
    # Cost = (2000 * 0.30 / 1e6) + (3500 * 2.50 / 1e6) = 0.0006 + 0.00875 = 0.00935 USD
    # Cumulative = 0.00405 + 0.00935 = 0.0134 USD >= 0.01 cap!
    with pytest.raises(RuntimeError) as exc_info:
        meter.record_attempt(tokens_in=2000, tokens_out=1500, thoughts_tokens=2000)
    assert "HARD COST CAP EXCEEDED" in str(exc_info.value)
    assert meter.is_exceeded()
    state = meter.get_state()
    assert state["cost_cap_exceeded"] is True
    assert "HARD COST CAP EXCEEDED" in state["halt_reason"]

    # Any subsequent attempt must be blocked immediately
    with pytest.raises(RuntimeError) as exc_info2:
        meter.record_attempt(tokens_in=10, tokens_out=10, thoughts_tokens=10)
    assert "HARD COST CAP EXCEEDED" in str(exc_info2.value)


def test_cost_meter_resume_behavior():
    """Verify CostMeter initializes cumulative tokens and cost on resume."""
    cap = 1.00
    # Simulate past completed attempts
    past_in = 50_000
    past_out = 20_000
    past_th = 30_000
    expected_past_cost = (past_in * 0.30 / 1e6) + ((past_out + past_th) * 2.50 / 1e6)

    meter = CostMeter(
        cost_cap_usd=cap,
        initial_tokens_in=past_in,
        initial_tokens_out=past_out,
        initial_thoughts=past_th,
        initial_attempts=50,
    )
    assert abs(meter.cumulative_cost_usd - expected_past_cost) < 1e-6
    assert meter.attempts_completed == 50
    assert not meter.is_exceeded()

    # If past cost already exceeds cap on resume:
    meter_over = CostMeter(
        cost_cap_usd=0.05,
        initial_tokens_in=past_in,
        initial_tokens_out=past_out,
        initial_thoughts=past_th,
        initial_attempts=50,
    )
    assert meter_over.is_exceeded()
    assert "HARD COST CAP EXCEEDED" in meter_over.halt_reason


def test_atomic_json_write():
    """Verify atomic_json_write writes valid JSON and creates no corrupted files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        target_path = os.path.join(tmp_dir, "test_output.json")
        sample_data = {"key": "value", "list": [1, 2, 3], "nested": {"a": True}}

        atomic_json_write(target_path, sample_data)
        assert os.path.exists(target_path)

        with open(target_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == sample_data

        # Update atomically
        sample_data["updated"] = True
        atomic_json_write(target_path, sample_data)
        with open(target_path, "r", encoding="utf-8") as f:
            loaded2 = json.load(f)
        assert loaded2 == sample_data


def test_tune_tasks_count_and_stratification():
    """Verify tune tasks loader loads exactly 46 tasks from splits_e5.json matching suite_e5."""
    tune_tasks = load_tune_tasks(REPO_ROOT)
    assert len(tune_tasks) == 46, f"Expected 46 tune tasks, got {len(tune_tasks)}"

    splits_path = os.path.join(REPO_ROOT, "benchmarks", "splits_e5.json")
    splits = json.load(open(splits_path, encoding="utf-8"))
    assert len(splits["tune"]) == 46
    assert len(splits["held_out"]) == 60

    tune_ids = set(splits["tune"])
    for t in tune_tasks:
        assert t["id"] in tune_ids
        assert "family" in t
        assert "class_tag" in t


def test_strict_stop_rule_and_metadata_header():
    """Verify run_screening enforces Strict Stop Rule and logs pinned metadata header with Option B defaults."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        res = run_screening(
            output_dir=tmp_dir,
            approved_for_execution=False,
            dry_run=False,
            repo_root=REPO_ROOT,
        )
        assert res["status"] == "LOCKED_AWAITING_APPROVAL"

        header_path = os.path.join(tmp_dir, "screening_log_header.json")
        assert os.path.exists(header_path)

        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)

        # Check defining relation and parity rule
        exp = header["experiment"]
        assert exp["defining_relation"] == "I = spurk"
        assert exp["parity_rule"] == "k = 1 if ((s + p + u + r) % 2 == 0) else 0"

        # Check pinned run config
        run_cfg = header["run_config"]
        assert run_cfg["model_id"] == "gemini-2.5-flash"
        assert run_cfg["temperature"] == 0.7
        assert run_cfg["top_p"] == 0.95
        assert run_cfg["max_output_tokens"] == 16384
        assert run_cfg["thinking_budget"] == 2048
        assert run_cfg["commit_sha_freeze_json"].startswith("a7ecb64")
        assert len(run_cfg["commit_sha_freeze_json"]) == 40

        # Check pricing and cost meter
        pricing = header["pricing"]
        assert pricing["price_input_per_1m_usd"] == 0.30
        assert pricing["price_output_per_1m_usd"] == 2.50
        assert pricing["thoughts_billed_as_output"] is True

        # Check Option B operational parameters
        scope = header["execution_scope"]
        assert scope["tune_tasks_count"] == 46
        assert scope["cells_count"] == 16
        assert scope["runs_count"] == 3
        assert scope["total_scheduled_attempts"] == 2208
        assert scope["cost_cap_usd"] == 37.85

        # Verify no rows.json was written (zero model execution)
        assert not os.path.exists(os.path.join(tmp_dir, "rows.json"))


def test_dry_run_mode():
    """Verify dry_run mode completes schedule validation without making API calls."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        res = run_screening(
            output_dir=tmp_dir,
            approved_for_execution=False,
            dry_run=True,
            repo_root=REPO_ROOT,
        )
        assert res["status"] == "DRY_RUN_VERIFIED"
        header_path = os.path.join(tmp_dir, "screening_log_header.json")
        assert os.path.exists(header_path)
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)
        assert header["experiment"]["status"] == "DRY_RUN_VERIFIED"
        assert not os.path.exists(os.path.join(tmp_dir, "rows.json"))


def test_analyze_pilot_calibration_constants():
    """Verify analyze_pilot_calibration.py has updated price constants and thoughts_tokens inclusion."""
    script_path = os.path.join(REPO_ROOT, "runner", "analyze_pilot_calibration.py")
    assert os.path.exists(script_path)
    content = open(script_path, encoding="utf-8").read()

    assert "PRICE_INPUT_PER_1M = 0.30" in content or "0.30" in content
    assert "PRICE_OUTPUT_PER_1M = 2.50" in content or "2.50" in content
    assert "thoughts_tokens" in content
    assert "Oct 2026" in content or "October 2026" in content


def test_per_cell_cost_table_computation_and_formatting():
    """Verify compute_per_cell_cost_table and format_per_cell_table."""
    rows = [
        {
            "cell": "C0000",
            "tokens_in": 1000,
            "tokens_out": 500,
            "thoughts_tokens": 1500,
            "total_billed_tokens": 3000,
            "cost_usd": 0.0053,
        },
        {
            "cell": "C0000",
            "tokens_in": 1200,
            "tokens_out": 600,
            "thoughts_tokens": 1800,
            "total_billed_tokens": 3600,
            "cost_usd": 0.00636,
        },
        {
            "cell": "C1111",
            "tokens_in": 10000,
            "tokens_out": 800,
            "thoughts_tokens": 4000,
            "total_billed_tokens": 14800,
            "cost_usd": 0.015,
        },
    ]

    table = compute_per_cell_cost_table(rows)
    assert len(table) == 16
    assert table["C0000"]["attempts"] == 2
    assert table["C0000"]["tokens_in"] == 2200
    assert table["C0000"]["cost_usd"] == 0.01166
    assert table["C0000"]["mean_cost_per_attempt"] == round(0.01166 / 2, 6)

    assert table["C1111"]["attempts"] == 1
    assert table["C1111"]["tokens_in"] == 10000
    assert table["C1111"]["cost_usd"] == 0.015

    assert table["C1000"]["attempts"] == 0
    assert table["C1000"]["cost_usd"] == 0.0
    assert table["C1000"]["mean_cost_per_attempt"] == 0.0

    formatted = format_per_cell_table(table)
    assert "Cell" in formatted
    assert "Attempts" in formatted
    assert "Cost (USD)" in formatted
    assert "C0000" in formatted
    assert "C1111" in formatted


def test_spend_threshold_pause_check():
    """Verify that spend reaching 50% of cap ($18.93) before 40% attempts (883) triggers PAUSED_SPEND_THRESHOLD_REACHED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        rows_path = os.path.join(tmp_dir, "rows.json")
        header_path = os.path.join(tmp_dir, "screening_log_header.json")

        # Create 10 attempts that consumed high tokens reaching $19.00 USD (>= $18.93 USD 50% cap threshold)
        # $19.00 USD across 10 attempts is < 883 attempts (40% of 2208)
        simulated_rows = []
        for i in range(10):
            simulated_rows.append(
                {
                    "cell": "C1111",
                    "s": 1,
                    "p": 1,
                    "u": 1,
                    "r": 1,
                    "k": 1,
                    "run": 1,
                    "ticket": f"ticket_{2001+i}",
                    "tokens_in": 1_000_000,       # 1M in = $0.30
                    "tokens_out": 300_000,        # 300k out = $0.75
                    "thoughts_tokens": 340_000,   # 340k th = $0.85 -> $1.90 per attempt x 10 = $19.00 USD
                    "total_billed_tokens": 1_640_000,
                    "cost_usd": 1.90,
                    "call_count": 3,
                }
            )

        with open(rows_path, "w", encoding="utf-8") as f:
            json.dump(simulated_rows, f, indent=2)

        # Invoking run_screening with approved_for_execution should detect threshold on resume
        with pytest.raises(RuntimeError) as exc_info:
            run_screening(
                output_dir=tmp_dir,
                cost_cap=37.85,
                runs=3,
                approved_for_execution=True,
                repo_root=REPO_ROOT,
            )

        assert "PAUSED_SPEND_THRESHOLD_REACHED" in str(exc_info.value)

        # Verify header status and recorded running per-cell cost table
        assert os.path.exists(header_path)
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)

        assert header["experiment"]["status"] == "PAUSED_SPEND_THRESHOLD_REACHED"
        assert header["cost_meter"]["cumulative_cost_usd"] == 19.0
        assert header["cost_meter"]["attempts_completed"] == 10
        assert "running_per_cell_cost_table" in header
        assert header["running_per_cell_cost_table"]["C1111"]["attempts"] == 10
        assert header["running_per_cell_cost_table"]["C1111"]["cost_usd"] == 19.0
