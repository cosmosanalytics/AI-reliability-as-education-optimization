"""suite_e5.py: Modular benchmark suite for E5 evaluation (28 instances across 7 families).

Complies strictly with Section 8 Addendum v2 of REAL_TEST_REQUIREMENTS.md and Round 10 criteria:
- 7 bug families, 4 distinct instances per family (28 total instances).
- Class tags: STATED (10), TAUGHT (11), DISTRACTOR (3), TRANSFER (4).
- Hidden Root Cause (12 tasks, 42.9%): tagged root_cause_only_with_exploration=True.
- Visible Test Sensitive (12 tasks, 42.9%): naive fixes fail visible tests.
- Neutral test names: zero design words in test IDs, filenames, or tracebacks.
- Tracebacks and assertions show symptoms only (never the rule or cause).
- Repositories contain 40-120 non-test lines across 2-4 files (zero decoys; 100% on reachability path).
- Minimal context package (traceback_files) provided to Baseline B0.
"""

import os
import sys

T = []

def register_task(tid, family, name, class_tag, issue, traceback_text, traceback_files,
                  repo, hidden, ref, mutant1, mutant2, hidden_root_cause=False,
                  visible_test_sensitive=False, root_cause_only_with_exploration=False,
                  handbook_citations=(), visible=None, protected=(), forbidden=(), must_touch=()):
    vis = visible or [p for p in repo if p.startswith("tests/")]
    key = {
        "visible_paths": list(vis),
        "protected": list(protected) or list(vis),
        "forbidden": list(forbidden),
        "must_touch": list(must_touch),
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
        "group": "E5",
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
        "key": key,
        "ref": ref,
        "mutant1": mutant1,
        "mutant2": mutant2,
    }
    T.append(task_dict)
    return task_dict

# Task 2001: Order Tax Calculation (STATED)
t2001_repo = {'models.py': '"""Data models for commerce order line items."""\nfrom dataclasses import dataclass, field\nfrom typing import List, Dict, Any\n\n@dataclass\nclass LineItem:\n    sku: str\n    price_cents: int\n    quantity: int = 1\n\n    def subtotal(self) -> int:\n        return self.price_cents * self.quantity\n\n@dataclass\nclass OrderSummary:\n    order_id: str\n    items: List[LineItem]\n    net_cents: int\n    tax_cents: int\n    gross_cents: int\n\n    def to_dict(self) -> Dict[str, Any]:\n        return {\n            "order_id": self.order_id,\n            "net_cents": self.net_cents,\n            "tax_cents": self.tax_cents,\n            "gross_cents": self.gross_cents,\n        }\n', 'tax_engine.py': '"""Low-level tax rate computation engine."""\nfrom typing import Dict, Any\n\nDEFAULT_TAX_JURISDICTIONS = {\n    "standard": 0.20,\n    "reduced": 0.10,\n    "exempt": 0.0,\n}\n\ndef get_rate_for_jurisdiction(code: str) -> float:\n    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)\n\ndef calculate_vat(net_cents: int, vat_rate: float) -> int:\n    """Compute VAT in integer cents for given net amount."""\n    return int(net_cents * vat_rate)\n', 'pricing.py': '"""Order pricing calculation with itemized taxes."""\nfrom typing import List, Tuple, Optional\nfrom models import LineItem, OrderSummary\nfrom tax_engine import calculate_vat, get_rate_for_jurisdiction\n\ndef calculate_order_total(items: List[Tuple[int, int]], vat_rate: float = 0.20, order_id: str = "ORD-001") -> OrderSummary:\n    """Calculate order total including tax.\n    items: list of (price_cents, quantity).\n    Returns OrderSummary.\n    Tax calculation must use banker\'s rounding (round half to even) on exact half-cents.\n    """\n    line_objs = [LineItem(sku=f"SKU-{i+1}", price_cents=p, quantity=q) for i, (p, q) in enumerate(items)]\n    net = sum(item.subtotal() for item in line_objs)\n    tax = calculate_vat(net, vat_rate)\n    return OrderSummary(order_id=order_id, items=line_objs, net_cents=net, tax_cents=tax, gross_cents=net + tax)\n', 'tests/test_pricing.py': 'from pricing import calculate_order_total\n\ndef test_single_item():\n    summary = calculate_order_total([(100, 1)], vat_rate=0.20)\n    assert summary.net_cents == 100\n    assert summary.tax_cents == 20\n    assert summary.gross_cents == 120\n\ndef test_multi_item():\n    summary = calculate_order_total([(100, 2), (200, 1)], vat_rate=0.10)\n    assert summary.net_cents == 400\n    assert summary.tax_cents == 40\n    assert summary.gross_cents == 440\n'}
t2001_hidden = {'tests/test_pricing_cases.py': 'import pytest\nfrom pricing import calculate_order_total\nfrom tax_engine import calculate_vat\n\ndef test_vat_rate_calculation():\n    assert calculate_order_total([(135, 1)], vat_rate=0.10).tax_cents == 14\n    assert calculate_order_total([(145, 1)], vat_rate=0.10).tax_cents == 14\n    assert calculate_order_total([(155, 1)], vat_rate=0.10).tax_cents == 16\n    assert calculate_order_total([(165, 1)], vat_rate=0.10).tax_cents == 16\n\ndef test_tax_engine_contract():\n    assert calculate_vat(135, 0.10) == 14\n    assert calculate_vat(145, 0.10) == 14\n'}
t2001_ref = {'tax_engine.py': '"""Low-level tax rate computation engine."""\nfrom decimal import Decimal, ROUND_HALF_EVEN\nfrom typing import Dict, Any\n\nDEFAULT_TAX_JURISDICTIONS = {\n    "standard": 0.20,\n    "reduced": 0.10,\n    "exempt": 0.0,\n}\n\ndef get_rate_for_jurisdiction(code: str) -> float:\n    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)\n\ndef calculate_vat(net_cents: int, vat_rate: float) -> int:\n    """Compute VAT in integer cents for given net amount using banker\'s rounding."""\n    d_net = Decimal(str(net_cents))\n    d_rate = Decimal(str(vat_rate))\n    return int((d_net * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))\n'}
t2001_m1 = {'pricing.py': '"""Order pricing calculation with itemized taxes."""\nfrom typing import List, Tuple, Optional\nfrom models import LineItem, OrderSummary\nfrom tax_engine import calculate_vat, get_rate_for_jurisdiction\nfrom decimal import Decimal, ROUND_HALF_EVEN\n\ndef calculate_order_total(items: List[Tuple[int, int]], vat_rate: float = 0.20, order_id: str = "ORD-001") -> OrderSummary:\n    line_objs = [LineItem(sku=f"SKU-{i+1}", price_cents=p, quantity=q) for i, (p, q) in enumerate(items)]\n    net = sum(item.subtotal() for item in line_objs)\n    tax = int((Decimal(str(net)) * Decimal(str(vat_rate))).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))\n    return OrderSummary(order_id=order_id, items=line_objs, net_cents=net, tax_cents=tax, gross_cents=net + tax)\n'}
t2001_m2 = {'tax_engine.py': '"""Low-level tax rate computation engine."""\nimport math\nfrom typing import Dict, Any\n\nDEFAULT_TAX_JURISDICTIONS = {\n    "standard": 0.20,\n    "reduced": 0.10,\n    "exempt": 0.0,\n}\n\ndef get_rate_for_jurisdiction(code: str) -> float:\n    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)\n\ndef calculate_vat(net_cents: int, vat_rate: float) -> int:\n    return int(math.ceil(net_cents * vat_rate))\n'}
register_task(
    tid=2001,
    family='money_rounding',
    name='Order Tax Calculation',
    class_tag='STATED',
    issue='Incident INC-8401: Itemized billing batch reconciliation failed for customer order line items under variable VAT rates.',
    traceback_text='FAILED tests/test_pricing_cases.py::test_vat_rate_calculation - AssertionError: assert 13 == 14',
    traceback_files=['pricing.py'],
    repo=t2001_repo,
    hidden=t2001_hidden,
    ref=t2001_ref,
    mutant1=t2001_m1,
    mutant2=t2001_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H02'],
)

# Task 2002: Invoice Discount Allocation (TAUGHT)
t2002_repo = {'models.py': '"""Discount rule models and line items."""\nfrom dataclasses import dataclass\nfrom typing import List, Dict, Any\n\n@dataclass\nclass LineDiscount:\n    line_id: int\n    allocated_cents: int\n\n@dataclass\nclass AllocationResult:\n    discounts: List[int]\n    total_allocated: int\n    is_fully_allocated: bool\n\n    def as_dict(self) -> Dict[str, Any]:\n        return {\n            "discounts": self.discounts,\n            "total_allocated": self.total_allocated,\n            "is_fully_allocated": self.is_fully_allocated,\n        }\n', 'utils.py': '"""Invoice discount validation helpers."""\nfrom typing import List\n\ndef validate_line_totals(lines: List[int]) -> bool:\n    return all(isinstance(x, int) and x >= 0 for x in lines)\n\ndef compute_total_cents(lines: List[int]) -> int:\n    return sum(lines)\n', 'discount.py': '"""Invoice discount allocation module."""\nfrom typing import List\nfrom models import AllocationResult\nfrom utils import validate_line_totals\n\ndef prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:\n    """Prorate discount across lines proportionally to their value.\n    line_totals: list of integer cents.\n    Returns list of discount cents per line.\n    """\n    if not validate_line_totals(line_totals):\n        raise ValueError("Line totals must be non-negative integers")\n    total = sum(line_totals)\n    if total == 0:\n        return [0] * len(line_totals)\n    return [int(cents * total_discount_cents // total) for cents in line_totals]\n\ndef allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:\n    """Wrapper returning structured allocation result."""\n    allocs = prorate_discount(line_totals, total_discount_cents)\n    tot = sum(allocs)\n    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))\n', 'tests/test_discount.py': 'from discount import prorate_discount, allocate_discounts\n\ndef test_even_split():\n    assert prorate_discount([100, 100], 20) == [10, 10]\n    res = allocate_discounts([200, 100], 30)\n    assert res.discounts == [20, 10]\n    assert res.total_allocated == 30\n\ndef test_zero_total():\n    assert prorate_discount([0, 0], 50) == [0, 0]\n\ndef test_proportional_distribution():\n    res = prorate_discount([100, 300], 100)\n    assert res == [25, 75]\n'}
t2002_hidden = {'tests/test_discount_cases.py': 'import pytest\nfrom discount import prorate_discount\n\ndef test_fractional_split():\n    assert prorate_discount([100, 100], 25) == [12, 12]\n    assert prorate_discount([100, 100], 35) == [18, 18]\n    assert prorate_discount([100, 100], 45) == [22, 22]\n\ndef test_multi_line_allocation():\n    assert sum(prorate_discount([100, 100, 100], 30)) == 30\n'}
t2002_ref = {'discount.py': '"""Invoice discount allocation module."""\nfrom typing import List\nfrom decimal import Decimal, ROUND_HALF_EVEN\nfrom models import AllocationResult\nfrom utils import validate_line_totals\n\ndef prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:\n    """Prorate discount across lines proportionally to their value.\n    line_totals: list of integer cents.\n    Returns list of discount cents per line.\n    """\n    if not validate_line_totals(line_totals):\n        raise ValueError("Line totals must be non-negative integers")\n    total = sum(line_totals)\n    if total == 0:\n        return [0] * len(line_totals)\n    d_total = Decimal(str(total))\n    d_disc = Decimal(str(total_discount_cents))\n    res = []\n    for cents in line_totals:\n        share = (Decimal(str(cents)) * d_disc / d_total).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)\n        res.append(int(share))\n    return res\n\ndef allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:\n    """Wrapper returning structured allocation result."""\n    allocs = prorate_discount(line_totals, total_discount_cents)\n    tot = sum(allocs)\n    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))\n'}
t2002_m1 = {'discount.py': '"""Invoice discount allocation module."""\nfrom typing import List\nfrom decimal import Decimal, ROUND_HALF_UP\nfrom models import AllocationResult\nfrom utils import validate_line_totals\n\ndef prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:\n    if not validate_line_totals(line_totals):\n        raise ValueError("Line totals must be non-negative integers")\n    total = sum(line_totals)\n    if total == 0:\n        return [0] * len(line_totals)\n    d_total = Decimal(str(total))\n    d_disc = Decimal(str(total_discount_cents))\n    return [int((Decimal(str(c)) * d_disc / d_total).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) for c in line_totals]\n\ndef allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:\n    allocs = prorate_discount(line_totals, total_discount_cents)\n    tot = sum(allocs)\n    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))\n'}
t2002_m2 = {'discount.py': '"""Invoice discount allocation module."""\nfrom typing import List\nfrom models import AllocationResult\nfrom utils import validate_line_totals\n\ndef prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:\n    if not validate_line_totals(line_totals):\n        raise ValueError("Line totals must be non-negative integers")\n    total = sum(line_totals)\n    if total == 0:\n        return [0] * len(line_totals)\n    return [int(c * total_discount_cents // total) for c in line_totals]\n\ndef allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:\n    allocs = prorate_discount(line_totals, total_discount_cents)\n    tot = sum(allocs)\n    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))\n'}
register_task(
    tid=2002,
    family='money_rounding',
    name='Invoice Discount Allocation',
    class_tag='TAUGHT',
    issue='Incident INC-3902: Promotional discount allocation across invoice line items results in an unallocated penny mismatch during checkout settlement.',
    traceback_text='FAILED tests/test_discount_cases.py::test_fractional_split - AssertionError: assert [17, 17] == [18, 18]',
    traceback_files=['discount.py'],
    repo=t2002_repo,
    hidden=t2002_hidden,
    ref=t2002_ref,
    mutant1=t2002_m1,
    mutant2=t2002_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H02'],
)

# Task 2003: Multi-Currency Fee Conversion (TAUGHT)
t2003_repo = {'rates.py': '"""Foreign exchange conversion models."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Optional\n\n@dataclass\nclass FxQuote:\n    base_currency: str\n    quote_currency: str\n    rate: float\n    provider: str = "ECB"\n\n    def is_inverted(self) -> bool:\n        return self.rate < 1.0\n\n@dataclass\nclass ConversionSummary:\n    source_cents: int\n    converted_cents: int\n    applied_rate: float\n', 'fx_engine.py': '"""Low-level exchange rate computation."""\nfrom typing import Tuple\n\ndef apply_fx_rate(cents: int, rate: float) -> int:\n    """Compute converted currency amount in cents."""\n    return int(cents * rate)\n\ndef compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:\n    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)\n    return apply_fx_rate(cents, effective_rate), effective_rate\n', 'converter.py': '"""Currency amount converter interface."""\nfrom rates import FxQuote, ConversionSummary\nfrom fx_engine import apply_fx_rate\n\ndef convert_currency_amount(amount_cents: int, quote: FxQuote) -> int:\n    """Convert amount in base currency cents to quote currency cents.\n    amount_cents: source currency amount in cents.\n    quote: exchange rate quote.\n    """\n    return apply_fx_rate(amount_cents, quote.rate)\n\ndef build_conversion_summary(amount_cents: int, quote: FxQuote) -> ConversionSummary:\n    converted = convert_currency_amount(amount_cents, quote)\n    return ConversionSummary(source_cents=amount_cents, converted_cents=converted, applied_rate=quote.rate)\n', 'tests/test_fx.py': 'from converter import convert_currency_amount, build_conversion_summary\nfrom rates import FxQuote\n\ndef test_integer_rate():\n    quote = FxQuote("USD", "EUR", 2.0)\n    assert convert_currency_amount(100, quote) == 200\n\ndef test_summary_builder():\n    quote = FxQuote("USD", "GBP", 0.5)\n    s = build_conversion_summary(200, quote)\n    assert s.converted_cents == 100\n'}
t2003_hidden = {'tests/test_fx_cases.py': 'from converter import convert_currency_amount\nfrom rates import FxQuote\nfrom fx_engine import apply_fx_rate\n\ndef test_fx_conversion():\n    quote = FxQuote("USD", "JPY", 1.5)\n    assert convert_currency_amount(135, quote) == 202\n    assert convert_currency_amount(145, quote) == 218\n\ndef test_fx_engine_contract():\n    assert apply_fx_rate(135, 1.5) == 202\n    assert apply_fx_rate(145, 1.5) == 218\n'}
t2003_ref = {'fx_engine.py': '"""Low-level exchange rate computation."""\nfrom decimal import Decimal, ROUND_HALF_EVEN\nfrom typing import Tuple\n\ndef apply_fx_rate(cents: int, rate: float) -> int:\n    """Compute converted currency amount in cents using banker\'s rounding."""\n    d_cents = Decimal(str(cents))\n    d_rate = Decimal(str(rate))\n    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))\n\ndef compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:\n    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)\n    return apply_fx_rate(cents, effective_rate), effective_rate\n'}
t2003_m1 = {'converter.py': '"""Currency amount converter interface."""\nfrom rates import FxQuote, ConversionSummary\nfrom fx_engine import apply_fx_rate\nfrom decimal import Decimal, ROUND_HALF_EVEN\n\ndef convert_currency_amount(amount_cents: int, quote: FxQuote) -> int:\n    d_cents = Decimal(str(amount_cents))\n    d_rate = Decimal(str(quote.rate))\n    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))\n\ndef build_conversion_summary(amount_cents: int, quote: FxQuote) -> ConversionSummary:\n    converted = convert_currency_amount(amount_cents, quote)\n    return ConversionSummary(source_cents=amount_cents, converted_cents=converted, applied_rate=quote.rate)\n'}
t2003_m2 = {'fx_engine.py': '"""Low-level exchange rate computation."""\nfrom decimal import Decimal, ROUND_HALF_UP\nfrom typing import Tuple\n\ndef apply_fx_rate(cents: int, rate: float) -> int:\n    d_cents = Decimal(str(cents))\n    d_rate = Decimal(str(rate))\n    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))\n\ndef compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:\n    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)\n    return apply_fx_rate(cents, effective_rate), effective_rate\n'}
register_task(
    tid=2003,
    family='money_rounding',
    name='Multi-Currency Fee Conversion',
    class_tag='TAUGHT',
    issue='Payment gateway ticket PAY-501: Cross-border clearing failed settlement reconciliation on fractional cent conversion batches.',
    traceback_text='FAILED tests/test_fx_cases.py::test_fx_conversion - AssertionError: assert 201 == 202',
    traceback_files=['converter.py'],
    repo=t2003_repo,
    hidden=t2003_hidden,
    ref=t2003_ref,
    mutant1=t2003_m1,
    mutant2=t2003_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H02'],
)

# Task 2004: Legacy Payroll Tax Ceiling (DISTRACTOR)
t2004_repo = {'models.py': '"""Payroll record data models."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass WithholdingRecord:\n    employee_id: int\n    gross_cents: int\n    tax_cents: int\n    exempt: bool = False\n    state_code: str = "CA"\n\n    def net_pay(self) -> int:\n        return self.gross_cents - self.tax_cents\n\n    def to_payload(self) -> Dict[str, Any]:\n        return {\n            "employee_id": self.employee_id,\n            "gross_cents": self.gross_cents,\n            "tax_cents": self.tax_cents,\n            "exempt": self.exempt,\n            "state_code": self.state_code,\n        }\n', 'validator.py': '"""Payroll audit validators."""\nfrom models import WithholdingRecord\n\ndef verify_withholding(record: WithholdingRecord, minimum_cents: int = 0) -> bool:\n    return record.tax_cents >= minimum_cents\n', 'payroll.py': '"""Payroll statutory tax calculation."""\nimport math\nfrom models import WithholdingRecord\nfrom validator import verify_withholding\n\ndef compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:\n    """Compute statutory payroll tax withholding.\n    Statutory requirement: payroll withholding MUST round fractional cents UP (ceiling)\n    to guarantee tax obligations are never under-withheld. Do NOT use banker\'s rounding.\n    """\n    return int(gross_cents * tax_rate)\n\ndef build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:\n    if exempt:\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)\n    else:\n        tax = compute_payroll_withholding(gross_cents, tax_rate)\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)\n    if not verify_withholding(rec, 0):\n        raise ValueError("Negative withholding calculated")\n    return rec\n', 'tests/test_payroll.py': 'from payroll import compute_payroll_withholding, build_withholding_record\n\ndef test_integer_withholding():\n    assert compute_payroll_withholding(1000, 0.10) == 100\n    rec = build_withholding_record(101, 2000, 0.05)\n    assert rec.tax_cents == 100\n\ndef test_fractional_withholding():\n    assert compute_payroll_withholding(105, 0.10) == 11\n'}
t2004_hidden = {'tests/test_payroll_cases.py': 'import pytest\nfrom payroll import compute_payroll_withholding\n\ndef test_payroll_deduction_rate():\n    assert compute_payroll_withholding(125, 0.10) == 13\n    assert compute_payroll_withholding(145, 0.10) == 15\n    assert compute_payroll_withholding(101, 0.10) == 11\n'}
t2004_ref = {'payroll.py': '"""Payroll statutory tax calculation."""\nimport math\nfrom models import WithholdingRecord\nfrom validator import verify_withholding\n\ndef compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:\n    """Compute statutory payroll tax withholding.\n    Statutory requirement: payroll withholding MUST round fractional cents UP (ceiling)\n    to guarantee tax obligations are never under-withheld. Do NOT use banker\'s rounding.\n    """\n    return int(math.ceil(gross_cents * tax_rate))\n\ndef build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:\n    if exempt:\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)\n    else:\n        tax = compute_payroll_withholding(gross_cents, tax_rate)\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)\n    if not verify_withholding(rec, 0):\n        raise ValueError("Negative withholding calculated")\n    return rec\n'}
t2004_m1 = {'payroll.py': '"""Payroll statutory tax calculation."""\nfrom decimal import Decimal, ROUND_HALF_EVEN\nfrom models import WithholdingRecord\nfrom validator import verify_withholding\n\ndef compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:\n    # Mutant 1: Blindly applies Banker\'s rounding\n    d_gross = Decimal(str(gross_cents))\n    d_rate = Decimal(str(tax_rate))\n    return int((d_gross * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))\n\ndef build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:\n    if exempt:\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)\n    else:\n        tax = compute_payroll_withholding(gross_cents, tax_rate)\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)\n    if not verify_withholding(rec, 0):\n        raise ValueError("Negative withholding calculated")\n    return rec\n'}
t2004_m2 = {'payroll.py': '"""Payroll statutory tax calculation."""\nfrom models import WithholdingRecord\nfrom validator import verify_withholding\n\ndef compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:\n    # Mutant 2: Truncation\n    return int(gross_cents * tax_rate)\n\ndef build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:\n    if exempt:\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)\n    else:\n        tax = compute_payroll_withholding(gross_cents, tax_rate)\n        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)\n    if not verify_withholding(rec, 0):\n        raise ValueError("Negative withholding calculated")\n    return rec\n'}
register_task(
    tid=2004,
    family='money_rounding',
    name='Legacy Payroll Tax Ceiling',
    class_tag='DISTRACTOR',
    issue='Compliance alert PAY-89: Statutory state tax withholding calculation is under-withholding on payroll processing batches.',
    traceback_text='FAILED tests/test_payroll_cases.py::test_payroll_deduction_rate - AssertionError: assert 12 == 13',
    traceback_files=['payroll.py'],
    repo=t2004_repo,
    hidden=t2004_hidden,
    ref=t2004_ref,
    mutant1=t2004_m1,
    mutant2=t2004_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H02'],
)

# Task 2005: Tenant Routing Configuration (STATED)
t2005_repo = {'models.py': '"""Configuration models for network routing."""\nfrom dataclasses import dataclass, field\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass RouteProfile:\n    tenant_id: str\n    settings: Dict[str, Any]\n    active: bool = True\n\n    def get_setting(self, path: str, default: Any = None) -> Any:\n        keys = path.split(".")\n        val = self.settings\n        for k in keys:\n            if isinstance(val, dict) and k in val:\n                val = val[k]\n            else:\n                return default\n        return val\n', 'schema.py': '"""Routing validation schemas."""\nfrom typing import Dict, Any\n\ndef validate_route_keys(config: Dict[str, Any]) -> bool:\n    required = ["retries", "timeout"]\n    return any(k in config for k in required)\n\ndef get_default_network_settings() -> Dict[str, Any]:\n    return {"network": {"retries": 3, "timeout": 30}}\n', 'routing.py': '"""Tenant routing configuration aggregator."""\nimport copy\nfrom typing import Dict, Any\nfrom models import RouteProfile\nfrom schema import validate_route_keys\n\ndef merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    """Merge tenant overrides into base configuration.\n    Inputs must remain strictly immutable; the function must return a newly allocated deep copy.\n    """\n    merged = dict(base_config)\n    merged.update(tenant_overrides)\n    return merged\n\ndef build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:\n    cfg = merge_tenant_routing(base_config, tenant_overrides)\n    validate_route_keys(cfg)\n    return RouteProfile(tenant_id=tenant_id, settings=cfg)\n', 'tests/test_routing.py': 'from routing import merge_tenant_routing, build_route_profile\n\ndef test_flat_merge():\n    base = {"retries": 3, "timeout": 30}\n    over = {"timeout": 10}\n    res = merge_tenant_routing(base, over)\n    assert res == {"retries": 3, "timeout": 10}\n    assert base == {"retries": 3, "timeout": 30}\n\ndef test_profile_builder():\n    p = build_route_profile("tenant-1", {"host": "internal"}, {"port": 8080})\n    assert p.settings["port"] == 8080\n\ndef test_nested_configuration_isolation():\n    base = {"network": {"retries": 3}}\n    over = {"network": {"timeout": 5}}\n    merged = merge_tenant_routing(base, over)\n    merged["network"]["retries"] = 99\n    assert base["network"]["retries"] == 3\n'}
t2005_hidden = {'tests/test_routing_cases.py': 'import pytest\nfrom routing import merge_tenant_routing\n\ndef test_config_isolation():\n    base = {"db": {"host": "localhost", "pool": {"size": 10, "max": 20}}}\n    over = {"db": {"pool": {"size": 5}}}\n    merged = merge_tenant_routing(base, over)\n    \n    assert merged["db"]["pool"]["size"] == 5\n    assert merged["db"]["pool"]["max"] == 20\n    assert merged["db"]["host"] == "localhost"\n    \n    merged["db"]["pool"]["max"] = 999\n    assert base["db"]["pool"]["max"] == 20\n'}
t2005_ref = {'routing.py': '"""Tenant routing configuration aggregator."""\nimport copy\nfrom typing import Dict, Any\nfrom models import RouteProfile\nfrom schema import validate_route_keys\n\ndef _deep_merge_dict(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:\n    result = copy.deepcopy(base)\n    for k, v in overrides.items():\n        if k in result and isinstance(result[k], dict) and isinstance(v, dict):\n            result[k] = _deep_merge_dict(result[k], v)\n        else:\n            result[k] = copy.deepcopy(v)\n    return result\n\ndef merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    """Merge tenant overrides into base configuration.\n    Inputs must remain strictly immutable; the function must return a newly allocated deep copy.\n    """\n    return _deep_merge_dict(base_config, tenant_overrides)\n\ndef build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:\n    cfg = merge_tenant_routing(base_config, tenant_overrides)\n    validate_route_keys(cfg)\n    return RouteProfile(tenant_id=tenant_id, settings=cfg)\n'}
t2005_m1 = {'routing.py': '"""Tenant routing configuration aggregator."""\nfrom typing import Dict, Any\nfrom models import RouteProfile\nfrom schema import validate_route_keys\n\ndef merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    merged = dict(base_config)\n    for k, v in tenant_overrides.items():\n        merged[k] = v\n    return merged\n\ndef build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:\n    cfg = merge_tenant_routing(base_config, tenant_overrides)\n    validate_route_keys(cfg)\n    return RouteProfile(tenant_id=tenant_id, settings=cfg)\n'}
t2005_m2 = {'routing.py': '"""Tenant routing configuration aggregator."""\nfrom typing import Dict, Any\nfrom models import RouteProfile\nfrom schema import validate_route_keys\n\ndef merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    base_config.update(tenant_overrides)\n    return base_config\n\ndef build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:\n    cfg = merge_tenant_routing(base_config, tenant_overrides)\n    validate_route_keys(cfg)\n    return RouteProfile(tenant_id=tenant_id, settings=cfg)\n'}
register_task(
    tid=2005,
    family='config_merge',
    name='Tenant Routing Configuration',
    class_tag='STATED',
    issue='Production outage OUT-104: Dynamic tenant routing update altered default network retry policies across multi-tenant worker nodes.',
    traceback_text='FAILED tests/test_routing_cases.py::test_config_isolation - AssertionError: assert 999 == 20',
    traceback_files=['routing.py'],
    repo=t2005_repo,
    hidden=t2005_hidden,
    ref=t2005_ref,
    mutant1=t2005_m1,
    mutant2=t2005_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H03'],
)

# Task 2006: Database Pool Settings (TAUGHT)
t2006_repo = {'options.py': '"""Database connection options schemas."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass ConnectionOptions:\n    dsn: str\n    pool_params: Dict[str, Any]\n    max_overflow: int = 10\n    timeout_seconds: float = 30.0\n\n    def is_ssl(self) -> bool:\n        return "sslmode" in self.pool_params\n\n    def get_param(self, key: str, fallback: Any = None) -> Any:\n        return self.pool_params.get(key, fallback)\n\n    def summary(self) -> str:\n        return f"Pool(dsn={self.dsn}, params={len(self.pool_params)})"\n', 'pool.py': '"""Database pool manager."""\nfrom typing import Dict, Any\nfrom env_loader import merge_env_settings\nfrom options import ConnectionOptions\n\ndef configure_pool(base_template: Dict[str, Any], overrides: Dict[str, Any]) -> ConnectionOptions:\n    """Configure connection pool options from template and overrides.\n    Returns ConnectionOptions instance.\n    """\n    settings = merge_env_settings(base_template, overrides)\n    dsn = settings.get("dsn", "sqlite:///:memory:")\n    opts = ConnectionOptions(dsn=dsn, pool_params=settings.get("pool", {}))\n    _ = opts.summary()\n    return opts\n', 'env_loader.py': '"""Environment settings loader and merger."""\nfrom typing import Dict, Any\n\nDEFAULT_CONN_TIMEOUT = 30\n\ndef load_system_env() -> Dict[str, Any]:\n    return {"timeout": DEFAULT_CONN_TIMEOUT}\n\ndef merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:\n    merged = dict(base_settings)\n    merged.update(override_settings)\n    return merged\n', 'tests/test_pool.py': 'from pool import configure_pool\n\ndef test_basic_pool_config():\n    opts = configure_pool({"dsn": "pg://prod", "pool": {"min": 5}}, {"pool": {"max": 20}})\n    assert opts.dsn == "pg://prod"\n'}
t2006_hidden = {'tests/test_pool_cases.py': 'import pytest\nfrom pool import configure_pool\nfrom env_loader import merge_env_settings\n\ndef test_pool_defaults_isolation():\n    base = {"dsn": "pg://master", "pool": {"min": 2, "max": 10, "timeout": 30}}\n    over = {"pool": {"max": 50}}\n    opts = configure_pool(base, over)\n    \n    assert opts.pool_params["max"] == 50\n    assert opts.pool_params["min"] == 2\n    \n    opts.pool_params["min"] = 99\n    assert base["pool"]["min"] == 2\n\ndef test_env_loader_contract():\n    b = {"sub": {"k": 1}}\n    o = {"sub": {"k2": 2}}\n    m = merge_env_settings(b, o)\n    m["sub"]["k"] = 99\n    assert b["sub"]["k"] == 1\n'}
t2006_ref = {'env_loader.py': '"""Environment settings loader and merger."""\nimport copy\nfrom typing import Dict, Any\n\nDEFAULT_CONN_TIMEOUT = 30\n\ndef load_system_env() -> Dict[str, Any]:\n    return {"timeout": DEFAULT_CONN_TIMEOUT}\n\ndef merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:\n    merged = copy.deepcopy(base_settings)\n    for key, value in override_settings.items():\n        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):\n            merged[key] = copy.deepcopy(merged[key])\n            merged[key].update(copy.deepcopy(value))\n        else:\n            merged[key] = copy.deepcopy(value)\n    return merged\n'}
t2006_m1 = {'pool.py': '"""Database pool manager."""\nimport copy\nfrom typing import Dict, Any\nfrom env_loader import merge_env_settings\nfrom options import ConnectionOptions\n\ndef configure_pool(base_template: Dict[str, Any], overrides: Dict[str, Any]) -> ConnectionOptions:\n    safe_base = copy.deepcopy(base_template)\n    safe_over = copy.deepcopy(overrides)\n    settings = merge_env_settings(safe_base, safe_over)\n    dsn = settings.get("dsn", "sqlite:///:memory:")\n    return ConnectionOptions(dsn=dsn, pool_params=copy.deepcopy(settings.get("pool", {})))\n'}
t2006_m2 = {'env_loader.py': '"""Environment settings loader and merger."""\nfrom typing import Dict, Any\n\nDEFAULT_CONN_TIMEOUT = 30\n\ndef load_system_env() -> Dict[str, Any]:\n    return {"timeout": DEFAULT_CONN_TIMEOUT}\n\ndef merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:\n    merged = base_settings.copy()\n    merged.update(override_settings)\n    return merged\n'}
register_task(
    tid=2006,
    family='config_merge',
    name='Database Pool Settings',
    class_tag='TAUGHT',
    issue='Security ticket SEC-402: Shared database connection pool defaults corrupted across worker threads following tenant override.',
    traceback_text='FAILED tests/test_pool_cases.py::test_pool_defaults_isolation - AssertionError: assert 99 == 2',
    traceback_files=['pool.py'],
    repo=t2006_repo,
    hidden=t2006_hidden,
    ref=t2006_ref,
    mutant1=t2006_m1,
    mutant2=t2006_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H03'],
)

# Task 2007: Pipeline Step Definition (STATED)
t2007_repo = {'defaults.py': '"""Default step parameters."""\nfrom typing import Dict, Any\n\nDEFAULT_PIPELINE_OPTS = {\n    "engine": "v2",\n    "retries": {"max": 3, "backoff": 1.5},\n    "monitoring": {"enabled": True, "sample_rate": 0.1},\n    "concurrency": {"max_workers": 4, "queue_depth": 100}\n}\n\ndef get_base_options() -> Dict[str, Any]:\n    return DEFAULT_PIPELINE_OPTS\n\ndef is_feature_enabled(feature_name: str) -> bool:\n    return DEFAULT_PIPELINE_OPTS.get(feature_name, {}).get("enabled", False)\n', 'step_builder.py': '"""Low-level step configuration compiler."""\nfrom typing import Dict, Any\n\ndef compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:\n    res = dict(base_opts)\n    res["name"] = name\n    res.update(overrides)\n    return res\n\ndef format_step_manifest(spec: Dict[str, Any]) -> str:\n    name = spec.get("name", "unnamed")\n    engine = spec.get("engine", "default")\n    return f"StageManifest(name={name}, engine={engine})"\n', 'pipeline.py': '"""Pipeline stage configurator."""\nfrom typing import Dict, Any, List\nfrom step_builder import compile_step_config, format_step_manifest\nfrom defaults import DEFAULT_PIPELINE_OPTS\n\ndef build_stage_spec(stage_name: str, step_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    """Compile pipeline stage specification.\n    Inputs must remain immutable and nested options must be defensively copied.\n    """\n    spec = compile_step_config(stage_name, DEFAULT_PIPELINE_OPTS, step_overrides)\n    _ = format_step_manifest(spec)\n    return spec\n\ndef build_multi_stage_pipeline(stage_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:\n    return [build_stage_spec(f"stage-{i}", cfg) for i, cfg in enumerate(stage_configs)]\n', 'tests/test_pipeline.py': 'from pipeline import build_stage_spec\n\ndef test_stage_naming():\n    spec = build_stage_spec("ingest", {"engine": "v3"})\n    assert spec["name"] == "ingest"\n    assert spec["engine"] == "v3"\n'}
t2007_hidden = {'tests/test_pipeline_cases.py': 'import pytest\nfrom pipeline import build_stage_spec\nfrom step_builder import compile_step_config\nfrom defaults import DEFAULT_PIPELINE_OPTS\n\ndef test_pipeline_defaults_isolation():\n    spec = build_stage_spec("transform", {"retries": {"max": 10}})\n    assert spec["retries"]["max"] == 10\n    assert spec["retries"]["backoff"] == 1.5\n    \n    spec["retries"]["backoff"] = 99.0\n    assert DEFAULT_PIPELINE_OPTS["retries"]["backoff"] == 1.5\n\ndef test_step_builder_contract():\n    b = {"r": {"m": 1}}\n    o = {"r": {"m": 2}}\n    s = compile_step_config("test", b, o)\n    s["r"]["m"] = 99\n    assert b["r"]["m"] == 1\n'}
t2007_ref = {'step_builder.py': '"""Low-level step configuration compiler."""\nimport copy\nfrom typing import Dict, Any\n\ndef compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:\n    res = copy.deepcopy(base_opts)\n    res["name"] = name\n    for k, v in overrides.items():\n        if k in res and isinstance(res[k], dict) and isinstance(v, dict):\n            res[k] = copy.deepcopy(res[k])\n            res[k].update(copy.deepcopy(v))\n        else:\n            res[k] = copy.deepcopy(v)\n    return res\n\ndef format_step_manifest(spec: Dict[str, Any]) -> str:\n    name = spec.get("name", "unnamed")\n    engine = spec.get("engine", "default")\n    return f"StageManifest(name={name}, engine={engine})"\n'}
t2007_m1 = {'pipeline.py': '"""Pipeline stage configurator."""\nimport copy\nfrom typing import Dict, Any\nfrom step_builder import compile_step_config, format_step_manifest\nfrom defaults import DEFAULT_PIPELINE_OPTS\n\ndef build_stage_spec(stage_name: str, step_overrides: Dict[str, Any]) -> Dict[str, Any]:\n    clean_base = copy.deepcopy(DEFAULT_PIPELINE_OPTS)\n    clean_over = copy.deepcopy(step_overrides)\n    res = compile_step_config(stage_name, clean_base, clean_over)\n    _ = format_step_manifest(res)\n    return copy.deepcopy(res)\n'}
t2007_m2 = {'step_builder.py': '"""Low-level step configuration compiler."""\nfrom typing import Dict, Any\n\ndef compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:\n    res = base_opts.copy()\n    res["name"] = name\n    res.update(overrides)\n    return res\n\ndef format_step_manifest(spec: Dict[str, Any]) -> str:\n    name = spec.get("name", "unnamed")\n    engine = spec.get("engine", "default")\n    return f"StageManifest(name={name}, engine={engine})"\n'}
register_task(
    tid=2007,
    family='config_merge',
    name='Pipeline Step Definition',
    class_tag='STATED',
    issue='Workflow engine bug WFL-301: Stage retry policy overrides mutated global default execution parameters across sequential pipeline steps.',
    traceback_text='FAILED tests/test_pipeline_cases.py::test_pipeline_defaults_isolation - AssertionError: assert 99.0 == 1.5',
    traceback_files=['pipeline.py'],
    repo=t2007_repo,
    hidden=t2007_hidden,
    ref=t2007_ref,
    mutant1=t2007_m1,
    mutant2=t2007_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H03'],
)

# Task 2008: Live Session State Accumulator (DISTRACTOR)
t2008_repo = {'state.py': '"""Session state accumulator model."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, List\n\n@dataclass\nclass SessionEnvelope:\n    session_id: str\n    data: Dict[str, Any]\n    version: int = 1\n    tags: List[str] = None\n\n    def __post_init__(self):\n        if self.tags is None:\n            self.tags = ["active"]\n\n    def get_metric(self, key: str) -> Any:\n        return self.data.get(key)\n\n    def is_valid(self) -> bool:\n        return bool(self.session_id and isinstance(self.data, dict))\n', 'metrics.py': '"""Session metric calculations."""\nfrom typing import Dict, Any\n\ndef count_active_keys(data: Dict[str, Any]) -> int:\n    return len(data)\n\ndef calculate_checksum(data: Dict[str, Any]) -> int:\n    return sum(len(str(k)) + len(str(v)) for k, v in data.items())\n', 'session.py': '"""Real-time live session accumulator."""\nfrom typing import Dict, Any\nfrom state import SessionEnvelope\nfrom metrics import count_active_keys\n\ndef update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:\n    """Update high-throughput live session accumulator.\n    Performance critical: high-frequency live session state MUST mutate accumulator in-place\n    to avoid GC thrashing (do NOT create deep copies), and nested dictionary entries MUST be\n    recursively updated in-place rather than overwritten.\n    """\n    return {**accumulator, **deltas}\n\ndef wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:\n    _ = count_active_keys(accumulator)\n    return SessionEnvelope(session_id=session_id, data=accumulator)\n', 'tests/test_session.py': 'from session import update_live_session, wrap_session\n\ndef test_session_values():\n    acc = {"count": 1}\n    res = update_live_session(acc, {"status": "active"})\n    assert res["count"] == 1\n    assert res["status"] == "active"\n\ndef test_accumulator_object_identity():\n    acc = {"session_hits": 10}\n    res = update_live_session(acc, {"session_hits": 11})\n    assert res is acc\n    assert acc["session_hits"] == 11\n'}
t2008_hidden = {'tests/test_session_cases.py': 'import pytest\nfrom session import update_live_session\n\ndef test_nested_accumulator_identity():\n    acc = {"counters": {"page_views": 100, "errors": 0}}\n    res = update_live_session(acc, {"counters": {"errors": 1}})\n    assert res is acc\n    assert acc["counters"]["page_views"] == 100\n    assert acc["counters"]["errors"] == 1\n'}
t2008_ref = {'session.py': '"""Real-time live session accumulator."""\nfrom typing import Dict, Any\nfrom state import SessionEnvelope\nfrom metrics import count_active_keys\n\ndef update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:\n    """Update high-throughput live session accumulator.\n    Performance critical: high-frequency live session state MUST mutate accumulator in-place\n    to avoid GC thrashing (do NOT create deep copies), and nested dictionary entries MUST be\n    recursively updated in-place rather than overwritten.\n    """\n    for k, v in deltas.items():\n        if k in accumulator and isinstance(accumulator[k], dict) and isinstance(v, dict):\n            accumulator[k].update(v)\n        else:\n            accumulator[k] = v\n    return accumulator\n\ndef wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:\n    _ = count_active_keys(accumulator)\n    return SessionEnvelope(session_id=session_id, data=accumulator)\n'}
t2008_m1 = {'session.py': '"""Real-time live session accumulator."""\nimport copy\nfrom typing import Dict, Any\nfrom state import SessionEnvelope\nfrom metrics import count_active_keys\n\ndef update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:\n    new_acc = copy.deepcopy(accumulator)\n    new_acc.update(copy.deepcopy(deltas))\n    return new_acc\n\ndef wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:\n    _ = count_active_keys(accumulator)\n    return SessionEnvelope(session_id=session_id, data=accumulator)\n'}
t2008_m2 = {'session.py': '"""Real-time live session accumulator."""\nfrom typing import Dict, Any\nfrom state import SessionEnvelope\nfrom metrics import count_active_keys\n\ndef update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:\n    accumulator.update(deltas)\n    return accumulator\n\ndef wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:\n    _ = count_active_keys(accumulator)\n    return SessionEnvelope(session_id=session_id, data=accumulator)\n'}
register_task(
    tid=2008,
    family='config_merge',
    name='Live Session State Accumulator',
    class_tag='DISTRACTOR',
    issue='Performance regression PERF-102: Memory telemetry detected excessive allocations and cache misses during live session state streaming, and nested metrics were overwritten instead of updated in-place.',
    traceback_text='FAILED tests/test_session_cases.py::test_nested_accumulator_identity - AssertionError: assert False is True',
    traceback_files=['session.py'],
    repo=t2008_repo,
    hidden=t2008_hidden,
    ref=t2008_ref,
    mutant1=t2008_m1,
    mutant2=t2008_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H03'],
)

# Task 2009: Billing Period Interval Calculator (STATED)
t2009_repo = {'calendar_models.py': '"""Models for billing period dates."""\nfrom dataclasses import dataclass\nfrom datetime import datetime, timedelta\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass BillingWindow:\n    start_dt: datetime\n    end_dt: datetime\n    account_id: str = "ACC-DEFAULT"\n    cycle_name: str = "monthly"\n\n    def duration(self) -> timedelta:\n        return self.end_dt - self.start_dt\n\n    def total_seconds(self) -> float:\n        return self.duration().total_seconds()\n\n    def to_iso(self) -> Dict[str, str]:\n        return {\n            "start": self.start_dt.isoformat(),\n            "end": self.end_dt.isoformat(),\n            "cycle": self.cycle_name,\n        }\n', 'formatters.py': '"""Date interval formatters."""\nfrom datetime import datetime\n\ndef format_window_label(start_dt: datetime, end_dt: datetime) -> str:\n    return f"{start_dt.strftime(\'%Y-%m-%d\')} to {end_dt.strftime(\'%Y-%m-%d\')}"\n\ndef format_short_month(dt: datetime) -> str:\n    return dt.strftime("%b %Y")\n', 'intervals.py': '"""Billing period interval membership checker."""\nfrom datetime import datetime\nfrom calendar_models import BillingWindow\nfrom formatters import format_window_label\n\ndef is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:\n    """Check if target timestamp falls within the billing window.\n    Interval convention: half-open interval [start, end), where start is inclusive and end is exclusive.\n    """\n    return window.start_dt <= target_dt <= window.end_dt\n\ndef filter_billing_events(window: BillingWindow, timestamps: list) -> list:\n    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]\n\ndef get_window_summary(window: BillingWindow) -> str:\n    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"\n', 'tests/test_intervals.py': 'from datetime import datetime\nfrom calendar_models import BillingWindow\nfrom intervals import is_timestamp_in_billing_period\n\ndef test_strictly_inside():\n    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))\n    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 15)) is True\n    assert is_timestamp_in_billing_period(w, datetime(2026, 2, 15)) is False\n\ndef test_start_inclusive():\n    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))\n    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1)) is True\n'}
t2009_hidden = {'tests/test_intervals_cases.py': 'from datetime import datetime\nfrom calendar_models import BillingWindow\nfrom intervals import is_timestamp_in_billing_period\n\ndef test_interval_end_boundary():\n    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))\n    assert is_timestamp_in_billing_period(w, datetime(2026, 2, 1)) is False\n\ndef test_interval_subsecond_boundary():\n    w = BillingWindow(datetime(2026, 1, 1, 0, 0, 0), datetime(2026, 1, 1, 1, 0, 0))\n    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1, 0, 59, 59, 999999)) is True\n    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1, 1, 0, 0)) is False\n'}
t2009_ref = {'intervals.py': '"""Billing period interval membership checker."""\nfrom datetime import datetime\nfrom calendar_models import BillingWindow\nfrom formatters import format_window_label\n\ndef is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:\n    """Check if target timestamp falls within the billing window.\n    Interval convention: half-open interval [start, end), where start is inclusive and end is exclusive.\n    """\n    return window.start_dt <= target_dt < window.end_dt\n\ndef filter_billing_events(window: BillingWindow, timestamps: list) -> list:\n    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]\n\ndef get_window_summary(window: BillingWindow) -> str:\n    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"\n'}
t2009_m1 = {'intervals.py': '"""Billing period interval membership checker."""\nfrom datetime import datetime\nfrom calendar_models import BillingWindow\nfrom formatters import format_window_label\n\ndef is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:\n    return window.start_dt < target_dt <= window.end_dt\n\ndef filter_billing_events(window: BillingWindow, timestamps: list) -> list:\n    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]\n\ndef get_window_summary(window: BillingWindow) -> str:\n    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"\n'}
t2009_m2 = {'intervals.py': '"""Billing period interval membership checker."""\nfrom datetime import datetime\nfrom calendar_models import BillingWindow\nfrom formatters import format_window_label\n\ndef is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:\n    return window.start_dt < target_dt < window.end_dt\n\ndef filter_billing_events(window: BillingWindow, timestamps: list) -> list:\n    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]\n\ndef get_window_summary(window: BillingWindow) -> str:\n    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"\n'}
register_task(
    tid=2009,
    family='calendar_recurrence',
    name='Billing Period Interval Calculator',
    class_tag='STATED',
    issue='Subscription billing incident SUB-801: Customers double-billed on the exact boundary timestamp between consecutive monthly subscription cycles.',
    traceback_text='FAILED tests/test_intervals_cases.py::test_interval_end_boundary - AssertionError: assert True is False',
    traceback_files=['intervals.py'],
    repo=t2009_repo,
    hidden=t2009_hidden,
    ref=t2009_ref,
    mutant1=t2009_m1,
    mutant2=t2009_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H05'],
)

# Task 2010: Subscription Active Window Evaluator (TAUGHT)
t2010_repo = {'rules.py': '"""Subscription entitlement schemas."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, List\n\n@dataclass\nclass Entitlement:\n    user_id: int\n    plan: str\n    tier: int = 1\n    features: List[str] = None\n\n    def __post_init__(self):\n        if self.features is None:\n            self.features = ["basic_access"]\n\n    def is_premium(self) -> bool:\n        return self.tier > 1\n\n    def has_feature(self, feat: str) -> bool:\n        return feat in self.features\n', 'subscription.py': '"""Subscription authorization service."""\nfrom rules import Entitlement\nfrom period_calc import check_in_window\n\ndef is_entitled_at(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> bool:\n    """Evaluate whether user plan entitlement is active at current_epoch timestamp."""\n    return check_in_window(start_epoch, end_epoch, current_epoch)\n\ndef get_entitlement_status(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> dict:\n    active = is_entitled_at(user_id, plan, start_epoch, end_epoch, current_epoch)\n    return {"user_id": user_id, "plan": plan, "active": active}\n\ndef describe_window(start_epoch: int, end_epoch: int) -> str:\n    return f"Window(from={start_epoch}, to={end_epoch})"\n', 'period_calc.py': '"""Low-level timestamp window evaluator."""\ndef check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:\n    return start_ts <= probe_ts <= end_ts\n\ndef get_window_duration(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n\ndef is_valid_epoch_range(start_ts: int, end_ts: int) -> bool:\n    return end_ts >= start_ts >= 0\n', 'tests/test_subscription.py': 'from subscription import is_entitled_at, get_entitlement_status\n\ndef test_nominal_active():\n    assert is_entitled_at(101, "pro", 1000, 2000, 1500) is True\n    assert is_entitled_at(101, "pro", 1000, 2000, 500) is False\n    assert is_entitled_at(101, "pro", 1000, 2000, 1000) is True\n'}
t2010_hidden = {'tests/test_subscription_cases.py': 'from subscription import is_entitled_at\nfrom period_calc import check_in_window\n\ndef test_window_expiration():\n    assert is_entitled_at(101, "pro", 1000, 2000, 2000) is False\n    assert is_entitled_at(101, "pro", 1000, 2000, 1999) is True\n\ndef test_period_calc_contract():\n    assert check_in_window(100, 200, 200) is False\n    assert check_in_window(100, 200, 100) is True\n'}
t2010_ref = {'period_calc.py': '"""Low-level timestamp window evaluator."""\ndef check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:\n    return start_ts <= probe_ts < end_ts\n\ndef get_window_duration(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n'}
t2010_m1 = {'subscription.py': '"""Subscription authorization service."""\nfrom rules import Entitlement\nfrom period_calc import check_in_window\n\ndef is_entitled_at(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> bool:\n    if current_epoch >= end_epoch:\n        return False\n    return check_in_window(start_epoch, end_epoch, current_epoch)\n\ndef get_entitlement_status(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> dict:\n    active = is_entitled_at(user_id, plan, start_epoch, end_epoch, current_epoch)\n    return {"user_id": user_id, "plan": plan, "active": active}\n'}
t2010_m2 = {'period_calc.py': '"""Low-level timestamp window evaluator."""\ndef check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:\n    return start_ts <= probe_ts <= end_ts\n\ndef get_window_duration(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n'}
register_task(
    tid=2010,
    family='calendar_recurrence',
    name='Subscription Active Window Evaluator',
    class_tag='TAUGHT',
    issue='Access control report ACC-404: Expired user account retained active entitlement access for one second after subscription window lapsed.',
    traceback_text='FAILED tests/test_subscription_cases.py::test_window_expiration - AssertionError: assert True is False',
    traceback_files=['subscription.py'],
    repo=t2010_repo,
    hidden=t2010_hidden,
    ref=t2010_ref,
    mutant1=t2010_m1,
    mutant2=t2010_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H05'],
)

# Task 2011: Maintenance Window Scheduler (STATED)
t2011_repo = {'slots.py': '"""Maintenance slot reservation schemas."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass MaintenanceSlot:\n    slot_id: str\n    start_hour: int\n    end_hour: int\n    approved: bool = True\n    cluster_id: str = "cluster-01"\n\n    def duration(self) -> int:\n        return self.end_hour - self.start_hour\n\n    def to_record(self) -> Dict[str, Any]:\n        return {\n            "slot_id": self.slot_id,\n            "span": f"[{self.start_hour}, {self.end_hour})",\n            "cluster": self.cluster_id,\n        }\n', 'audit.py': '"""Maintenance schedule auditor."""\nfrom typing import List\nfrom slots import MaintenanceSlot\n\ndef total_scheduled_hours(slots: List[MaintenanceSlot]) -> int:\n    return sum(s.duration() for s in slots)\n\ndef validate_all_approved(slots: List[MaintenanceSlot]) -> bool:\n    return all(s.approved for s in slots)\n', 'maintenance.py': '"""Cluster maintenance scheduler."""\nfrom typing import List\nfrom slots import MaintenanceSlot\nfrom audit import validate_all_approved\n\ndef has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:\n    """Detect if two maintenance slots overlap.\n    Interval contract: slots are half-open intervals [start, end). Adjacent slots sharing\n    a boundary (e.g. [2, 4) and [4, 6)) do NOT overlap.\n    """\n    return not (slot_a.end_hour < slot_b.start_hour or slot_b.end_hour < slot_a.start_hour)\n\ndef can_schedule_slot(existing_slots: List[MaintenanceSlot], candidate: MaintenanceSlot) -> bool:\n    if not validate_all_approved(existing_slots):\n        raise ValueError("Existing slots contain unapproved reservations")\n    return not any(has_window_overlap(s, candidate) for s in existing_slots)\n\ndef get_slot_bounds(slots: List[MaintenanceSlot]) -> tuple:\n    if not slots:\n        return (0, 0)\n    return (min(s.start_hour for s in slots), max(s.end_hour for s in slots))\n', 'tests/test_maintenance.py': 'from slots import MaintenanceSlot\nfrom maintenance import has_window_overlap\n\ndef test_disjoint_slots():\n    a = MaintenanceSlot("s1", 1, 3)\n    b = MaintenanceSlot("s2", 5, 7)\n    assert has_window_overlap(a, b) is False\n\ndef test_adjacent_slots():\n    a = MaintenanceSlot("s1", 2, 4)\n    b = MaintenanceSlot("s2", 4, 6)\n    assert has_window_overlap(a, b) is False\n'}
t2011_hidden = {'tests/test_maintenance_cases.py': 'from slots import MaintenanceSlot\nfrom maintenance import has_window_overlap\n\ndef test_touching_slot_boundaries():\n    a = MaintenanceSlot("s1", 2, 4)\n    b = MaintenanceSlot("s2", 4, 6)\n    assert has_window_overlap(a, b) is False\n\ndef test_nested_slot():\n    a = MaintenanceSlot("s1", 1, 10)\n    b = MaintenanceSlot("s2", 3, 5)\n    assert has_window_overlap(a, b) is True\n'}
t2011_ref = {'maintenance.py': '"""Cluster maintenance scheduler."""\nfrom typing import List\nfrom slots import MaintenanceSlot\nfrom audit import validate_all_approved\n\ndef has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:\n    """Detect if two maintenance slots overlap.\n    Interval contract: slots are half-open intervals [start, end). Adjacent slots sharing\n    a boundary (e.g. [2, 4) and [4, 6)) do NOT overlap.\n    """\n    return not (slot_a.end_hour <= slot_b.start_hour or slot_b.end_hour <= slot_a.start_hour)\n\ndef can_schedule_slot(existing_slots: List[MaintenanceSlot], candidate: MaintenanceSlot) -> bool:\n    if not validate_all_approved(existing_slots):\n        raise ValueError("Existing slots contain unapproved reservations")\n    return not any(has_window_overlap(s, candidate) for s in existing_slots)\n\ndef get_slot_bounds(slots: List[MaintenanceSlot]) -> tuple:\n    if not slots:\n        return (0, 0)\n    return (min(s.start_hour for s in slots), max(s.end_hour for s in slots))\n'}
t2011_m1 = {'maintenance.py': '"""Cluster maintenance scheduler."""\nfrom slots import MaintenanceSlot\nfrom audit import validate_all_approved\n\ndef has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:\n    return max(slot_a.start_hour, slot_b.start_hour) <= min(slot_a.end_hour, slot_b.end_hour)\n\ndef can_schedule_slot(existing_slots: list, candidate: MaintenanceSlot) -> bool:\n    return not any(has_window_overlap(s, candidate) for s in existing_slots)\n'}
t2011_m2 = {'maintenance.py': '"""Cluster maintenance scheduler."""\nfrom slots import MaintenanceSlot\nfrom audit import validate_all_approved\n\ndef has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:\n    return False\n\ndef can_schedule_slot(existing_slots: list, candidate: MaintenanceSlot) -> bool:\n    return True\n'}
register_task(
    tid=2011,
    family='calendar_recurrence',
    name='Maintenance Window Scheduler',
    class_tag='STATED',
    issue='Operations incident OPS-202: Maintenance scheduling system rejected valid contiguous deployment windows as conflicting collisions.',
    traceback_text='FAILED tests/test_maintenance.py::test_adjacent_slots - AssertionError: assert True is False',
    traceback_files=['maintenance.py'],
    repo=t2011_repo,
    hidden=t2011_hidden,
    ref=t2011_ref,
    mutant1=t2011_m1,
    mutant2=t2011_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H05'],
)

# Task 2012: Audit Log Retention Window (TAUGHT)
t2012_repo = {'log_store.py': '"""Log storage models."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass LogEntry:\n    entry_id: str\n    timestamp: int\n    source: str = "app"\n    severity: str = "INFO"\n\n    def is_system(self) -> bool:\n        return self.source == "system"\n\n    def is_error(self) -> bool:\n        return self.severity in ("ERROR", "FATAL")\n\n    def to_record(self) -> Dict[str, Any]:\n        return {"id": self.entry_id, "ts": self.timestamp, "sev": self.severity}\n', 'window_evaluator.py': '"""Retention window evaluator."""\ndef is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:\n    return start_ts <= ts <= end_ts\n\ndef get_window_span(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n\ndef is_valid_cutoff(start_ts: int, end_ts: int) -> bool:\n    return start_ts <= end_ts\n', 'retention.py': '"""Audit log retention manager."""\nfrom typing import List\nfrom window_evaluator import is_within_retention\nfrom log_store import LogEntry\n\ndef filter_retained_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> List[LogEntry]:\n    """Filter logs that fall into the active retention period."""\n    return [l for l in logs if is_within_retention(l.timestamp, cutoff_start, cutoff_end)]\n\ndef count_purged_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> int:\n    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)\n    return len(logs) - len(retained)\n\ndef group_retained_by_source(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> dict:\n    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)\n    res = {}\n    for l in retained:\n        res.setdefault(l.source, []).append(l)\n    return res\n', 'tests/test_retention.py': 'from log_store import LogEntry\nfrom retention import filter_retained_logs\n\ndef test_nominal_filtering():\n    logs = [LogEntry("l1", 100), LogEntry("l2", 500)]\n    retained = filter_retained_logs(logs, 50, 200)\n    assert len(retained) == 1\n    assert retained[0].entry_id == "l1"\n'}
t2012_hidden = {'tests/test_retention_cases.py': 'from log_store import LogEntry\nfrom retention import filter_retained_logs\nfrom window_evaluator import is_within_retention\n\ndef test_retention_window_cutoff():\n    logs = [LogEntry("start", 100), LogEntry("end", 200)]\n    retained = filter_retained_logs(logs, 100, 200)\n    assert len(retained) == 1\n    assert retained[0].entry_id == "start"\n\ndef test_window_evaluator_contract():\n    assert is_within_retention(100, 100, 200) is True\n    assert is_within_retention(200, 100, 200) is False\n'}
t2012_ref = {'window_evaluator.py': '"""Retention window evaluator."""\ndef is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:\n    return start_ts <= ts < end_ts\n\ndef get_window_span(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n'}
t2012_m1 = {'retention.py': '"""Audit log retention manager."""\nfrom typing import List\nfrom window_evaluator import is_within_retention\nfrom log_store import LogEntry\n\ndef filter_retained_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> List[LogEntry]:\n    return [l for l in logs if l.timestamp < cutoff_end and is_within_retention(l.timestamp, cutoff_start, cutoff_end)]\n\ndef count_purged_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> int:\n    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)\n    return len(logs) - len(retained)\n'}
t2012_m2 = {'window_evaluator.py': '"""Retention window evaluator."""\ndef is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:\n    return start_ts < ts < end_ts\n\ndef get_window_span(start_ts: int, end_ts: int) -> int:\n    return max(0, end_ts - start_ts)\n'}
register_task(
    tid=2012,
    family='calendar_recurrence',
    name='Audit Log Retention Window',
    class_tag='TAUGHT',
    issue='Compliance audit AUD-601: Expired audit log records on the exact daily archive cutoff timestamp were retained past required purge window.',
    traceback_text='FAILED tests/test_retention_cases.py::test_retention_window_cutoff - AssertionError: assert 2 == 1',
    traceback_files=['retention.py'],
    repo=t2012_repo,
    hidden=t2012_hidden,
    ref=t2012_ref,
    mutant1=t2012_m1,
    mutant2=t2012_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H05'],
)

# Task 2013: Customer Profile CSV Exporter (STATED)
t2013_repo = {'schema.py': '"""Customer profile models."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, List\n\n@dataclass\nclass CustomerProfile:\n    cust_id: int\n    name: str\n    notes: str\n    active: bool = True\n    tags: List[str] = None\n\n    def __post_init__(self):\n        if self.tags is None:\n            self.tags = ["standard"]\n\n    def to_row(self) -> list:\n        return [str(self.cust_id), self.name, self.notes]\n\n    def has_embedded_delimiters(self) -> bool:\n        return any(c in self.notes for c in (",", "\\n", \'"\'))\n', 'io_helpers.py': '"""CSV stream and buffer helpers."""\nfrom typing import List\n\ndef join_csv_lines(header: str, rows: List[str]) -> str:\n    return "\\n".join([header] + rows)\n\ndef validate_csv_header(header: str, expected_cols: List[str]) -> bool:\n    cols = [c.strip() for c in header.split(",")]\n    return cols == expected_cols\n', 'csv_writer.py': '"""CSV serialization utilities."""\nfrom typing import List\nfrom schema import CustomerProfile\nfrom io_helpers import validate_csv_header\n\ndef escape_csv_field(val: str) -> str:\n    """Escape CSV field per RFC 4180:\n    If field contains comma, newline, or double quote, wrap in double quotes and escape internal quotes by doubling ("").\n    """\n    if any(c in val for c in [",", "\\n", \'"\']):\n        escaped = val.replace(\'"\', \'\\"\')\n        return f\'"{escaped}"\'\n    return val\n\ndef export_profiles_csv(profiles: List[CustomerProfile]) -> str:\n    header = "cust_id,name,notes"\n    if not validate_csv_header(header, ["cust_id", "name", "notes"]):\n        raise ValueError("Invalid header")\n    lines = [header]\n    for p in profiles:\n        f_name = escape_csv_field(p.name)\n        f_notes = escape_csv_field(p.notes)\n        lines.append(f"{p.cust_id},{f_name},{f_notes}")\n    return "\\n".join(lines)\n\ndef count_records(csv_payload: str) -> int:\n    lines = [l for l in csv_payload.splitlines() if l.strip()]\n    return max(0, len(lines) - 1)\n', 'tests/test_profile.py': 'from schema import CustomerProfile\nfrom csv_writer import export_profiles_csv, escape_csv_field\n\ndef test_simple_csv():\n    p = [CustomerProfile(1, "Alice", "Normal")]\n    assert export_profiles_csv(p) == "cust_id,name,notes\\n1,Alice,Normal"\n\ndef test_comma_escaping():\n    assert escape_csv_field("Hello, World") == \'"Hello, World"\'\n'}
t2013_hidden = {'tests/test_profile_cases.py': 'from csv_writer import escape_csv_field, export_profiles_csv\nfrom schema import CustomerProfile\n\ndef test_quote_escaping():\n    assert escape_csv_field(\'Alice "Ace" Smith\') == \'"Alice ""Ace"" Smith"\'\n    assert escape_csv_field(\'"Quotes"\') == \'"""Quotes"""\'\n\ndef test_multiline_csv():\n    p = [CustomerProfile(2, "Bob", "Line 1\\nLine 2")]\n    out = export_profiles_csv(p)\n    assert out == \'cust_id,name,notes\\n2,Bob,"Line 1\\nLine 2"\'\n'}
t2013_ref = {'csv_writer.py': '"""CSV serialization utilities."""\nfrom typing import List\nfrom schema import CustomerProfile\nfrom io_helpers import validate_csv_header\n\ndef escape_csv_field(val: str) -> str:\n    """Escape CSV field per RFC 4180:\n    If field contains comma, newline, or double quote, wrap in double quotes and escape internal quotes by doubling ("").\n    """\n    if any(c in val for c in [",", "\\n", \'"\']):\n        doubled = val.replace(\'"\', \'""\')\n        return f\'"{doubled}"\'\n    return val\n\ndef export_profiles_csv(profiles: List[CustomerProfile]) -> str:\n    header = "cust_id,name,notes"\n    if not validate_csv_header(header, ["cust_id", "name", "notes"]):\n        raise ValueError("Invalid header")\n    lines = [header]\n    for p in profiles:\n        f_name = escape_csv_field(p.name)\n        f_notes = escape_csv_field(p.notes)\n        lines.append(f"{p.cust_id},{f_name},{f_notes}")\n    return "\\n".join(lines)\n\ndef count_records(csv_payload: str) -> int:\n    lines = [l for l in csv_payload.splitlines() if l.strip()]\n    return max(0, len(lines) - 1)\n'}
t2013_m1 = {'csv_writer.py': '"""CSV serialization utilities."""\nfrom typing import List\nfrom schema import CustomerProfile\nfrom io_helpers import validate_csv_header\n\ndef escape_csv_field(val: str) -> str:\n    # Mutant 1: Double backslash\n    if any(c in val for c in [",", "\\n", \'"\']):\n        escaped = val.replace(\'"\', \'\\\\\\"\')\n        return f\'"{escaped}"\'\n    return val\n\ndef export_profiles_csv(profiles: List[CustomerProfile]) -> str:\n    header = "cust_id,name,notes"\n    lines = [header]\n    for p in profiles:\n        lines.append(f"{p.cust_id},{escape_csv_field(p.name)},{escape_csv_field(p.notes)}")\n    return "\\n".join(lines)\n'}
t2013_m2 = {'csv_writer.py': '"""CSV serialization utilities."""\nfrom typing import List\nfrom schema import CustomerProfile\nfrom io_helpers import validate_csv_header\n\ndef escape_csv_field(val: str) -> str:\n    # Mutant 2: Simple wrap without escaping\n    if any(c in val for c in [",", "\\n", \'"\']):\n        return f\'"{val}"\'\n    return val\n\ndef export_profiles_csv(profiles: List[CustomerProfile]) -> str:\n    header = "cust_id,name,notes"\n    lines = [header]\n    for p in profiles:\n        lines.append(f"{p.cust_id},{escape_csv_field(p.name)},{escape_csv_field(p.notes)}")\n    return "\\n".join(lines)\n'}
register_task(
    tid=2013,
    family='csv_roundtrip',
    name='Customer Profile CSV Exporter',
    class_tag='STATED',
    issue='Customer support ticket SUP-303: Data export file failed to import into standard spreadsheet software when customer company name contained quotes.',
    traceback_text='FAILED tests/test_profile_cases.py::test_quote_escaping - AssertionError: assert \'"Alice \\\\"Ace\\\\" Smith"\' == \'"Alice ""Ace"" Smith"\'',
    traceback_files=['csv_writer.py'],
    repo=t2013_repo,
    hidden=t2013_hidden,
    ref=t2013_ref,
    mutant1=t2013_m1,
    mutant2=t2013_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H10'],
)

# Task 2014: Order Item CSV Serializer (TAUGHT)
t2014_repo = {'item.py': '"""Item definition for order exports."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass OrderItem:\n    item_id: str\n    description: str\n    sku: str = "GENERIC"\n    category: str = "general"\n\n    def is_valid(self) -> bool:\n        return bool(self.item_id and self.description)\n\n    def summary(self) -> str:\n        return f"{self.item_id} ({self.sku})"\n\n    def formatted_label(self) -> str:\n        return f"[{self.category.upper()}] {self.description}"\n', 'catalog_validator.py': '"""Catalog export validator."""\nfrom typing import List\nfrom item import OrderItem\n\ndef validate_catalog(items: List[OrderItem]) -> bool:\n    return all(i.is_valid() for i in items)\n\ndef filter_by_category(items: List[OrderItem], category: str) -> List[OrderItem]:\n    return [i for i in items if i.category == category]\n', 'serializer.py': '"""Order item CSV row serializer."""\nfrom typing import List\nfrom item import OrderItem\nfrom catalog_validator import validate_catalog\n\ndef serialize_item_row(item: OrderItem) -> str:\n    """Serialize OrderItem into a CSV formatted line."""\n    return f"{item.item_id},{item.description}"\n\ndef serialize_catalog(items: List[OrderItem]) -> str:\n    if not validate_catalog(items):\n        raise ValueError("Invalid catalog items")\n    return "\\n".join(serialize_item_row(i) for i in items)\n\ndef count_serialized_items(catalog_str: str) -> int:\n    return len([line for line in catalog_str.splitlines() if line.strip()])\n', 'tests/test_item.py': 'from item import OrderItem\nfrom serializer import serialize_item_row\n\ndef test_simple_item():\n    item = OrderItem("ITM-1", "Standard Widget")\n    assert serialize_item_row(item) == "ITM-1,Standard Widget"\n'}
t2014_hidden = {'tests/test_item_cases.py': 'from item import OrderItem\nfrom serializer import serialize_item_row\n\ndef test_item_quote_escaping():\n    item = OrderItem("ITM-2", \'Widget "Pro" Edition\')\n    assert serialize_item_row(item) == \'ITM-2,"Widget ""Pro"" Edition"\'\n\ndef test_comma_enclosure():\n    item = OrderItem("ITM-3", "Gadget, Type A")\n    assert serialize_item_row(item) == \'ITM-3,"Gadget, Type A"\'\n'}
t2014_ref = {'serializer.py': '"""Order item CSV row serializer."""\nfrom typing import List\nfrom item import OrderItem\nfrom catalog_validator import validate_catalog\n\ndef _escape(val: str) -> str:\n    if any(c in val for c in [",", "\\n", \'"\']):\n        return f\'"{val.replace(chr(34), chr(34) + chr(34))}"\'\n    return val\n\ndef serialize_item_row(item: OrderItem) -> str:\n    """Serialize OrderItem into a CSV formatted line."""\n    return f"{_escape(item.item_id)},{_escape(item.description)}"\n\ndef serialize_catalog(items: List[OrderItem]) -> str:\n    if not validate_catalog(items):\n        raise ValueError("Invalid catalog items")\n    return "\\n".join(serialize_item_row(i) for i in items)\n'}
t2014_m1 = {'serializer.py': '"""Order item CSV row serializer."""\nfrom typing import List\nfrom item import OrderItem\nfrom catalog_validator import validate_catalog\n\ndef _escape(val: str) -> str:\n    if any(c in val for c in [",", "\\n", \'"\']):\n        return f\'"{val.replace(chr(34), chr(92) + chr(34))}"\'\n    return val\n\ndef serialize_item_row(item: OrderItem) -> str:\n    return f"{_escape(item.item_id)},{_escape(item.description)}"\n\ndef serialize_catalog(items: List[OrderItem]) -> str:\n    if not validate_catalog(items):\n        raise ValueError("Invalid catalog items")\n    return "\\n".join(serialize_item_row(i) for i in items)\n'}
t2014_m2 = {'serializer.py': '"""Order item CSV row serializer."""\nfrom typing import List\nfrom item import OrderItem\nfrom catalog_validator import validate_catalog\n\ndef serialize_item_row(item: OrderItem) -> str:\n    clean_desc = item.description.replace(\'"\', \'\')\n    return f"{item.item_id},{clean_desc}"\n\ndef serialize_catalog(items: List[OrderItem]) -> str:\n    if not validate_catalog(items):\n        raise ValueError("Invalid catalog items")\n    return "\\n".join(serialize_item_row(i) for i in items)\n'}
register_task(
    tid=2014,
    family='csv_roundtrip',
    name='Order Item CSV Serializer',
    class_tag='TAUGHT',
    issue='E-commerce export ticket EXP-119: CSV inventory export generated unquoted fields on catalog descriptions containing commas and inch measurement quotes.',
    traceback_text='FAILED tests/test_item_cases.py::test_item_quote_escaping - AssertionError: assert \'ITM-2,Widget "Pro" Edition\' == \'ITM-2,"Widget ""Pro"" Edition"\'',
    traceback_files=['serializer.py'],
    repo=t2014_repo,
    hidden=t2014_hidden,
    ref=t2014_ref,
    mutant1=t2014_m1,
    mutant2=t2014_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H10'],
)

# Task 2015: Batch Metric CSV Downloader (TAUGHT)
t2015_repo = {'metric.py': '"""Telemetry metric entry."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass MetricEntry:\n    key: str\n    value_label: str\n    sample_rate: float = 1.0\n    unit: str = "count"\n\n    def is_high_volume(self) -> bool:\n        return self.sample_rate > 0.5\n\n    def to_metric_dict(self) -> Dict[str, Any]:\n        return {\n            "key": self.key,\n            "label": self.value_label,\n            "rate": self.sample_rate,\n            "unit": self.unit,\n        }\n', 'sanitizer.py': '"""CSV cell sanitizer."""\ndef sanitize_cell(text: str) -> str:\n    return text.replace(\'"\', \'\\"\')\n\ndef requires_sanitization(text: str) -> bool:\n    return any(c in text for c in (\',\', \'\\n\', \'"\'))\n', 'exporter.py': '"""Metric telemetry exporter."""\nfrom typing import List\nfrom sanitizer import sanitize_cell\nfrom metric import MetricEntry\n\ndef format_metric_row(entry: MetricEntry) -> str:\n    """Format single metric row into CSV line."""\n    return f"{sanitize_cell(entry.key)},{sanitize_cell(entry.value_label)}"\n\ndef export_metric_batch(metrics: List[MetricEntry]) -> str:\n    return "\\n".join(format_metric_row(m) for m in metrics)\n\ndef export_with_header(metrics: List[MetricEntry]) -> str:\n    header = "metric_key,value_label"\n    rows = export_metric_batch(metrics)\n    return f"{header}\\n{rows}" if rows else header\n', 'tests/test_exporter.py': 'from metric import MetricEntry\nfrom exporter import format_metric_row\n\ndef test_simple_metric():\n    m = MetricEntry("cpu_usage", "nominal")\n    assert format_metric_row(m) == "cpu_usage,nominal"\n'}
t2015_hidden = {'tests/test_exporter_cases.py': 'from metric import MetricEntry\nfrom exporter import format_metric_row\nfrom sanitizer import sanitize_cell\n\ndef test_metric_quote_escaping():\n    m = MetricEntry("query", \'SELECT * FROM "users"\')\n    assert format_metric_row(m) == \'query,"SELECT * FROM ""users"""\'\n\ndef test_sanitizer_contract():\n    assert sanitize_cell(\'foo "bar"\') == \'"foo ""bar"""\'\n    assert sanitize_cell(\'a,b\') == \'"a,b"\'\n'}
t2015_ref = {'sanitizer.py': '"""CSV cell sanitizer."""\ndef sanitize_cell(text: str) -> str:\n    if any(c in text for c in [",", "\\n", \'"\']):\n        return f\'"{text.replace(chr(34), chr(34) + chr(34))}"\'\n    return text\n'}
t2015_m1 = {'exporter.py': '"""Metric telemetry exporter."""\nfrom typing import List\nfrom sanitizer import sanitize_cell\nfrom metric import MetricEntry\n\ndef format_metric_row(entry: MetricEntry) -> str:\n    k = f\'"{entry.key.replace(chr(34), chr(34) + chr(34))}"\' if any(c in entry.key for c in [\',\', \'\\n\', \'"\']) else entry.key\n    v = f\'"{entry.value_label.replace(chr(34), chr(34) + chr(34))}"\' if any(c in entry.value_label for c in [\',\', \'\\n\', \'"\']) else entry.value_label\n    return f"{k},{v}"\n\ndef export_metric_batch(metrics: List[MetricEntry]) -> str:\n    return "\\n".join(format_metric_row(m) for m in metrics)\n'}
t2015_m2 = {'sanitizer.py': '"""CSV cell sanitizer."""\ndef sanitize_cell(text: str) -> str:\n    if any(c in text for c in [",", "\\n", \'"\']):\n        return f\'"{text.replace(chr(34), chr(92) + chr(34))}"\'\n    return text\n'}
register_task(
    tid=2015,
    family='csv_roundtrip',
    name='Batch Metric CSV Downloader',
    class_tag='TAUGHT',
    issue='Monitoring report MON-409: SQL query telemetry export crashed BI import parser due to unescaped double quotes inside query metric labels.',
    traceback_text='FAILED tests/test_exporter_cases.py::test_metric_quote_escaping - AssertionError: assert \'query,SELECT * FROM \\\\"users\\\\"\' == \'query,"SELECT * FROM ""users"""\'',
    traceback_files=['exporter.py'],
    repo=t2015_repo,
    hidden=t2015_hidden,
    ref=t2015_ref,
    mutant1=t2015_m1,
    mutant2=t2015_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H10'],
)

# Task 2016: Shell TSV Command Log (DISTRACTOR)
t2016_repo = {'cmd_models.py': '"""Shell command log data structures."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass CommandAuditRecord:\n    cmd_id: int\n    command_str: str\n    exit_code: int = 0\n    host: str = "worker-01"\n\n    def is_success(self) -> bool:\n        return self.exit_code == 0\n\n    def to_record(self) -> Dict[str, Any]:\n        return {\n            "id": self.cmd_id,\n            "cmd": self.command_str,\n            "rc": self.exit_code,\n            "host": self.host,\n        }\n', 'cmd_log.py': '"""Shell command log generator."""\nfrom cmd_models import CommandAuditRecord\n\ndef audit_format_event(cmd_id: int) -> bool:\n    return cmd_id > 0\n\ndef format_audit_record(rec: CommandAuditRecord) -> str:\n    return f"{rec.cmd_id}\\t{rec.command_str}"\n', 'tsv_formatter.py': '"""TSV command formatter."""\nfrom cmd_models import CommandAuditRecord\nfrom cmd_log import audit_format_event\n\ndef format_tsv_command(cmd_id: int, command_str: str) -> str:\n    """Format shell command record.\n    Unix pipe format: fields must be tab-delimited and internal quotes must be backslash-escaped (\\")\n    for Bash compatibility. Do NOT use RFC 4180 double-quoting.\n    """\n    _ = audit_format_event(cmd_id)\n    return f"{cmd_id},{command_str}"\n\ndef get_tsv_delimiter() -> str:\n    return "\\t"\n', 'tests/test_cmd_log.py': 'from tsv_formatter import format_tsv_command\n\ndef test_simple_command():\n    assert format_tsv_command(1, "ls -la") == "1\\tls -la"\n\ndef test_tab_delimiters():\n    res = format_tsv_command(2, "echo hello")\n    assert "\\t" in res\n    assert "," not in res\n'}
t2016_hidden = {'tests/test_cmd_log_cases.py': 'from tsv_formatter import format_tsv_command\n\ndef test_quote_formatting():\n    res = format_tsv_command(3, \'echo "hello"\')\n    assert res == \'3\\techo \\\\"hello\\\\"\'\n'}
t2016_ref = {'tsv_formatter.py': '"""TSV command formatter."""\nfrom cmd_models import CommandAuditRecord\nfrom cmd_log import audit_format_event\n\ndef format_tsv_command(cmd_id: int, command_str: str) -> str:\n    """Format shell command record.\n    Unix pipe format: fields must be tab-delimited and internal quotes must be backslash-escaped (\\")\n    for Bash compatibility. Do NOT use RFC 4180 double-quoting.\n    """\n    _ = audit_format_event(cmd_id)\n    escaped = command_str.replace(\'"\', r\'\\"\')\n    return f"{cmd_id}\\t{escaped}"\n'}
t2016_m1 = {'tsv_formatter.py': '"""TSV command formatter."""\nfrom cmd_models import CommandAuditRecord\nfrom cmd_log import audit_format_event\n\ndef format_tsv_command(cmd_id: int, command_str: str) -> str:\n    _ = audit_format_event(cmd_id)\n    doubled = command_str.replace(\'"\', \'""\')\n    return f\'{cmd_id}\\t"{doubled}"\'\n'}
t2016_m2 = {'tsv_formatter.py': '"""TSV command formatter."""\nfrom cmd_models import CommandAuditRecord\nfrom cmd_log import audit_format_event\n\ndef format_tsv_command(cmd_id: int, command_str: str) -> str:\n    _ = audit_format_event(cmd_id)\n    return f"{cmd_id},{command_str}"\n'}
register_task(
    tid=2016,
    family='csv_roundtrip',
    name='Shell TSV Command Log',
    class_tag='DISTRACTOR',
    issue='DevOps pipeline failure PIP-701: Audit command log consumer failed to parse Bash execution records due to invalid delimiter syntax.',
    traceback_text='FAILED tests/test_cmd_log_cases.py::test_quote_formatting - AssertionError: assert \'3,echo "hello"\' == \'3\\techo \\"hello\\"\'',
    traceback_files=['tsv_formatter.py'],
    repo=t2016_repo,
    hidden=t2016_hidden,
    ref=t2016_ref,
    mutant1=t2016_m1,
    mutant2=t2016_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H10'],
)

# Task 2017: API Route Authorization Guard (STATED)
t2017_repo = {'policy.py': '"""Authorization policy schemas."""\nfrom dataclasses import dataclass\nfrom typing import List, Dict, Any, Optional\n\n@dataclass\nclass RoutePolicy:\n    role: str\n    allowed_prefix: str\n    description: str = ""\n    is_active: bool = True\n\n    def matches_role(self, candidate_role: str) -> bool:\n        return self.role == candidate_role\n\n    def is_wildcard(self) -> bool:\n        return self.allowed_prefix == "/"\n\n    def summary(self) -> str:\n        return f"Policy(role={self.role}, prefix={self.allowed_prefix})"\n', 'url_normalizer.py': '"""URL string sanitizers."""\ndef strip_protocol(url: str) -> str:\n    if "://" in url:\n        return url.split("://", 1)[1]\n    return url\n\ndef remove_query_string(url: str) -> str:\n    return url.split("?", 1)[0]\n', 'guard.py': '"""API gateway authorization guard."""\nfrom policy import RoutePolicy\nfrom url_normalizer import remove_query_string\n\ndef is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:\n    """Check if request_path is authorized under policy.allowed_prefix.\n    Path matching contract:\n    - Normalizes trailing slashes before matching.\n    - Matches only full path segments (e.g. \'/api\' covers \'/api\' and \'/api/v1\', but NOT \'/api-v2\').\n    """\n    clean_path = remove_query_string(request_path)\n    return clean_path.startswith(policy.allowed_prefix)\n\ndef evaluate_request(policies: list, role: str, path: str) -> bool:\n    for p in policies:\n        if p.matches_role(role) and is_route_permitted(p, path):\n            return True\n    return False\n\ndef count_permitted_routes(policy: RoutePolicy, paths: list) -> int:\n    return sum(1 for p in paths if is_route_permitted(policy, p))\n', 'tests/test_guard.py': 'from policy import RoutePolicy\nfrom guard import is_route_permitted\n\ndef test_nominal_match():\n    p = RoutePolicy("admin", "/api/v1")\n    assert is_route_permitted(p, "/api/v1/users") is True\n    assert is_route_permitted(p, "/other") is False\n\ndef test_sibling_path_boundary():\n    p = RoutePolicy("analyst", "/reports")\n    assert is_route_permitted(p, "/reports-secret") is False\n'}
t2017_hidden = {'tests/test_guard_cases.py': 'from policy import RoutePolicy\nfrom guard import is_route_permitted\n\ndef test_trailing_slash_normalization():\n    p1 = RoutePolicy("user", "/docs/")\n    p2 = RoutePolicy("user", "/docs")\n    assert is_route_permitted(p1, "/docs") is True\n    assert is_route_permitted(p2, "/docs/") is True\n    assert is_route_permitted(p2, "/docs/readme.md") is True\n    assert is_route_permitted(p2, "/docsextra") is False\n'}
t2017_ref = {'guard.py': '"""API gateway authorization guard."""\nfrom policy import RoutePolicy\nfrom url_normalizer import remove_query_string\n\ndef is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:\n    """Check if request_path is authorized under policy.allowed_prefix.\n    Path matching contract:\n    - Normalizes trailing slashes before matching.\n    - Matches only full path segments (e.g. \'/api\' covers \'/api\' and \'/api/v1\', but NOT \'/api-v2\').\n    """\n    clean_path = remove_query_string(request_path)\n    prefix = policy.allowed_prefix.rstrip("/")\n    path = clean_path.rstrip("/")\n    if path == prefix:\n        return True\n    return path.startswith(prefix + "/")\n\ndef evaluate_request(policies: list, role: str, path: str) -> bool:\n    for p in policies:\n        if p.matches_role(role) and is_route_permitted(p, path):\n            return True\n    return False\n'}
t2017_m1 = {'guard.py': '"""API gateway authorization guard."""\nfrom policy import RoutePolicy\nfrom url_normalizer import remove_query_string\n\ndef is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:\n    clean_path = remove_query_string(request_path)\n    return clean_path.startswith(policy.allowed_prefix)\n\ndef evaluate_request(policies: list, role: str, path: str) -> bool:\n    for p in policies:\n        if p.matches_role(role) and is_route_permitted(p, path):\n            return True\n    return False\n'}
t2017_m2 = {'guard.py': '"""API gateway authorization guard."""\nfrom policy import RoutePolicy\nfrom url_normalizer import remove_query_string\n\ndef is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:\n    clean_path = remove_query_string(request_path)\n    return policy.allowed_prefix.rstrip("/") == clean_path.rstrip("/")\n\ndef evaluate_request(policies: list, role: str, path: str) -> bool:\n    for p in policies:\n        if p.matches_role(role) and is_route_permitted(p, path):\n            return True\n    return False\n'}
register_task(
    tid=2017,
    family='permission_prefix',
    name='API Route Authorization Guard',
    class_tag='STATED',
    issue='Security vulnerability SEC-810: Gateway allowed unauthorized access to /reports-confidential under standard /reports policy.',
    traceback_text='FAILED tests/test_guard.py::test_sibling_path_boundary - AssertionError: assert True is False',
    traceback_files=['guard.py'],
    repo=t2017_repo,
    hidden=t2017_hidden,
    ref=t2017_ref,
    mutant1=t2017_m1,
    mutant2=t2017_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H06'],
)

# Task 2018: Document Store RBAC Filter (TAUGHT)
t2018_repo = {'path_resolver.py': '"""Path resolver utilities."""\nfrom typing import List, Optional\n\ndef clean_path(path_str: str) -> str:\n    return "/" + path_str.strip("/")\n\ndef get_parent_directory(path_str: str) -> str:\n    cleaned = clean_path(path_str)\n    if "/" in cleaned:\n        return cleaned.rsplit("/", 1)[0] or "/"\n    return "/"\n\ndef split_path_segments(path_str: str) -> List[str]:\n    cleaned = clean_path(path_str)\n    return [seg for seg in cleaned.split("/") if seg]\n\ndef is_root_path(path_str: str) -> bool:\n    return clean_path(path_str) == "/"\n\ndef count_segments(path_str: str) -> int:\n    return len(split_path_segments(path_str))\n', 'audit_logger.py': '"""Access attempt logger."""\ndef format_access_attempt(folder: str, path: str, allowed: bool) -> str:\n    status = "ALLOWED" if allowed else "DENIED"\n    return f"[{status}] scope={folder} path={path}"\n\ndef is_security_audit_enabled() -> bool:\n    return True\n\ndef get_audit_channel() -> str:\n    return "security-audit-stream"\n', 'rbac.py': '"""Document access RBAC filter."""\nfrom path_resolver import clean_path, split_path_segments\nfrom audit_logger import format_access_attempt\n\ndef check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:\n    """Verify if document path is permitted within the designated folder scope."""\n    allowed = clean_path(requested_doc_path).startswith(clean_path(allowed_folder))\n    _ = format_access_attempt(allowed_folder, requested_doc_path, allowed)\n    return allowed\n\ndef filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:\n    return [p for p in doc_paths if check_document_access(allowed_folder, p)]\n\ndef can_access_all_docs(allowed_folder: str, doc_paths: list) -> bool:\n    return all(check_document_access(allowed_folder, p) for p in doc_paths)\n', 'tests/test_rbac.py': 'from rbac import check_document_access\n\ndef test_nominal_folder_access():\n    assert check_document_access("/public", "/public/index.html") is True\n    assert check_document_access("/public", "/private/index.html") is False\n\ndef test_directory_prefix_boundary():\n    assert check_document_access("/public", "/public-internal/secret.pdf") is False\n'}
t2018_hidden = {'tests/test_rbac_cases.py': 'from rbac import check_document_access\n\ndef test_path_normalization():\n    assert check_document_access("/docs/", "/docs") is True\n    assert check_document_access("/docs", "/docs/") is True\n    assert check_document_access("/docs", "/docs/report.pdf") is True\n    assert check_document_access("/docs", "/docsextra/hack.pdf") is False\n'}
t2018_ref = {'rbac.py': '"""Document access RBAC filter."""\nfrom path_resolver import clean_path\nfrom audit_logger import format_access_attempt\n\ndef check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:\n    """Verify if document path is permitted within the designated folder scope."""\n    folder = clean_path(allowed_folder)\n    target = clean_path(requested_doc_path)\n    allowed = False\n    if target == folder:\n        allowed = True\n    elif target.startswith(folder + "/"):\n        allowed = True\n    _ = format_access_attempt(allowed_folder, requested_doc_path, allowed)\n    return allowed\n\ndef filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:\n    return [p for p in doc_paths if check_document_access(allowed_folder, p)]\n'}
t2018_m1 = {'rbac.py': '"""Document access RBAC filter."""\nfrom path_resolver import clean_path\nfrom audit_logger import format_access_attempt\n\ndef check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:\n    allowed = clean_path(requested_doc_path).startswith(clean_path(allowed_folder))\n    _ = format_access_attempt(allowed_folder, requested_doc_path, allowed)\n    return allowed\n\ndef filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:\n    return [p for p in doc_paths if check_document_access(allowed_folder, p)]\n'}
t2018_m2 = {'rbac.py': '"""Document access RBAC filter."""\nfrom path_resolver import clean_path\nfrom audit_logger import format_access_attempt\n\ndef check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:\n    allowed = (clean_path(allowed_folder) == clean_path(requested_doc_path))\n    _ = format_access_attempt(allowed_folder, requested_doc_path, allowed)\n    return allowed\n\ndef filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:\n    return [p for p in doc_paths if check_document_access(allowed_folder, p)]\n'}
register_task(
    tid=2018,
    family='permission_prefix',
    name='Document Store RBAC Filter',
    class_tag='TAUGHT',
    issue='Audit finding SEC-903: File storage permissions granted access to unauthorized sibling directory /docsextra under /docs permission.',
    traceback_text='FAILED tests/test_rbac.py::test_directory_prefix_boundary - AssertionError: assert True is False',
    traceback_files=['rbac.py'],
    repo=t2018_repo,
    hidden=t2018_hidden,
    ref=t2018_ref,
    mutant1=t2018_m1,
    mutant2=t2018_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H06'],
)

# Task 2019: Asset Storage Prefix Validator (STATED)
t2019_repo = {'models.py': '"""Storage bucket asset records."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass StorageAsset:\n    asset_id: str\n    path: str\n    bucket: str = "default-assets"\n    content_type: str = "application/octet-stream"\n\n    def extension(self) -> str:\n        if "." in self.path:\n            return self.path.rsplit(".", 1)[1]\n        return ""\n\n    def is_image(self) -> bool:\n        return self.extension().lower() in ("png", "jpg", "jpeg", "gif", "webp")\n\n    def to_descriptor(self) -> Dict[str, Any]:\n        return {\n            "id": self.asset_id,\n            "path": self.path,\n            "bucket": self.bucket,\n            "ext": self.extension(),\n        }\n', 'path_normalizer.py': '"""Storage path normalization engine."""\ndef validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:\n    return asset_path.startswith(scope_prefix)\n\ndef get_scope_depth(path: str) -> int:\n    return len([seg for seg in path.split("/") if seg])\n\ndef normalize_bucket_path(path: str) -> str:\n    return "/" + path.strip("/")\n', 'asset_service.py': '"""Asset bucket retrieval service."""\nfrom path_normalizer import validate_prefix_match, get_scope_depth\nfrom models import StorageAsset\n\ndef can_access_asset(asset: StorageAsset, required_scope: str) -> bool:\n    """Check if asset path matches the required storage bucket scope.\n    Path matching contract: matches full directory segment boundaries and normalizes trailing slashes.\n    """\n    return validate_prefix_match(required_scope, asset.path)\n\ndef filter_accessible_assets(assets: list, required_scope: str) -> list:\n    return [a for a in assets if can_access_asset(a, required_scope)]\n\ndef get_asset_hierarchy_level(asset: StorageAsset) -> int:\n    return get_scope_depth(asset.path)\n', 'tests/test_asset.py': 'from models import StorageAsset\nfrom asset_service import can_access_asset\n\ndef test_nominal_asset():\n    a = StorageAsset("A1", "/assets/images/logo.png")\n    assert can_access_asset(a, "/assets") is True\n    assert can_access_asset(a, "/data") is False\n'}
t2019_hidden = {'tests/test_asset_cases.py': 'from models import StorageAsset\nfrom asset_service import can_access_asset\nfrom path_normalizer import validate_prefix_match\n\ndef test_resource_isolation():\n    a1 = StorageAsset("A2", "/assets-private/secret.key")\n    assert can_access_asset(a1, "/assets") is False\n    \n    a2 = StorageAsset("A3", "/assets")\n    assert can_access_asset(a2, "/assets/") is True\n\ndef test_path_normalizer_contract():\n    assert validate_prefix_match("/assets", "/assets-private") is False\n    assert validate_prefix_match("/assets/", "/assets") is True\n'}
t2019_ref = {'path_normalizer.py': '"""Storage path normalization engine."""\ndef validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:\n    scope = "/" + scope_prefix.strip("/")\n    target = "/" + asset_path.strip("/")\n    if target == scope:\n        return True\n    return target.startswith(scope + "/")\n\ndef get_scope_depth(path: str) -> int:\n    return len([seg for seg in path.split("/") if seg])\n'}
t2019_m1 = {'asset_service.py': '"""Asset bucket retrieval service."""\nfrom path_normalizer import validate_prefix_match\nfrom models import StorageAsset\n\ndef can_access_asset(asset: StorageAsset, required_scope: str) -> bool:\n    s = "/" + required_scope.strip("/")\n    p = "/" + asset.path.strip("/")\n    if p != s and not p.startswith(s + "/"):\n        return False\n    return validate_prefix_match(required_scope, asset.path)\n\ndef filter_accessible_assets(assets: list, required_scope: str) -> list:\n    return [a for a in assets if can_access_asset(a, required_scope)]\n'}
t2019_m2 = {'path_normalizer.py': '"""Storage path normalization engine."""\ndef validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:\n    return asset_path.startswith(scope_prefix)\n\ndef get_scope_depth(path: str) -> int:\n    return len([seg for seg in path.split("/") if seg])\n'}
register_task(
    tid=2019,
    family='permission_prefix',
    name='Asset Storage Prefix Validator',
    class_tag='STATED',
    issue='Cloud storage incident CLD-512: Private asset directory /assets-private was exposed to users granted standard /assets access.',
    traceback_text='FAILED tests/test_asset_cases.py::test_resource_isolation - AssertionError: assert True is False',
    traceback_files=['asset_service.py'],
    repo=t2019_repo,
    hidden=t2019_hidden,
    ref=t2019_ref,
    mutant1=t2019_m1,
    mutant2=t2019_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H06'],
)

# Task 2020: Webhook Subscription Scope Enforcer (TAUGHT)
t2020_repo = {'webhook.py': '"""Webhook event payload models."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass WebhookEvent:\n    topic_path: str\n    payload: str\n    event_id: str = "EVT-DEFAULT"\n    retry_count: int = 0\n\n    def is_empty(self) -> bool:\n        return not bool(self.payload)\n\n    def topic_root(self) -> str:\n        return self.topic_path.split("/")[0]\n\n    def to_envelope(self) -> Dict[str, Any]:\n        return {\n            "id": self.event_id,\n            "topic": self.topic_path,\n            "payload": self.payload,\n            "retries": self.retry_count,\n        }\n', 'prefix_validator.py': '"""Topic path subscription matcher."""\ndef is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:\n    return event_topic.startswith(subscribed_pattern)\n\ndef clean_topic_segment(topic: str) -> str:\n    return topic.strip().lower()\n\ndef is_wildcard_subscription(pattern: str) -> bool:\n    return pattern.strip() in ("*", "#", "/")\n', 'scope_checker.py': '"""Webhook scope dispatch checker."""\nfrom prefix_validator import is_topic_subscribed, clean_topic_segment\nfrom webhook import WebhookEvent\n\ndef should_dispatch_webhook(subscribed_topic: str, event: WebhookEvent) -> bool:\n    """Determine if webhook event topic is permitted under the subscription filter."""\n    return is_topic_subscribed(subscribed_topic, event.topic_path)\n\ndef filter_dispatch_queue(subscribed_topic: str, events: list) -> list:\n    return [e for e in events if should_dispatch_webhook(subscribed_topic, e)]\n\ndef batch_topic_summary(events: list) -> dict:\n    summary = {}\n    for e in events:\n        summary[e.topic_path] = summary.get(e.topic_path, 0) + 1\n    return summary\n', 'tests/test_scope.py': 'from webhook import WebhookEvent\nfrom scope_checker import should_dispatch_webhook\n\ndef test_nominal_topic():\n    evt = WebhookEvent("orders/created", "{\'id\': 1}")\n    assert should_dispatch_webhook("orders", evt) is True\n    assert should_dispatch_webhook("billing", evt) is False\n'}
t2020_hidden = {'tests/test_scope_cases.py': 'from webhook import WebhookEvent\nfrom scope_checker import should_dispatch_webhook\nfrom prefix_validator import is_topic_subscribed\n\ndef test_channel_routing():\n    evt_sibling = WebhookEvent("orders_admin/reindex", "{}")\n    assert should_dispatch_webhook("orders", evt_sibling) is False\n    \n    evt_exact = WebhookEvent("orders", "{}")\n    assert should_dispatch_webhook("orders/", evt_exact) is True\n\ndef test_prefix_validator_contract():\n    assert is_topic_subscribed("orders", "orders_admin") is False\n    assert is_topic_subscribed("orders/", "orders") is True\n'}
t2020_ref = {'prefix_validator.py': '"""Topic path subscription matcher."""\ndef is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:\n    pat = "/" + subscribed_pattern.strip("/")\n    topic = "/" + event_topic.strip("/")\n    if topic == pat:\n        return True\n    return topic.startswith(pat + "/")\n\ndef clean_topic_segment(topic: str) -> str:\n    return topic.strip().lower()\n'}
t2020_m1 = {'scope_checker.py': '"""Webhook scope dispatch checker."""\nfrom prefix_validator import is_topic_subscribed\nfrom webhook import WebhookEvent\n\ndef should_dispatch_webhook(subscribed_topic: str, event: WebhookEvent) -> bool:\n    p = "/" + subscribed_topic.strip("/")\n    t = "/" + event.topic_path.strip("/")\n    if t != p and not t.startswith(p + "/"):\n        return False\n    return is_topic_subscribed(subscribed_topic, event.topic_path)\n\ndef filter_dispatch_queue(subscribed_topic: str, events: list) -> list:\n    return [e for e in events if should_dispatch_webhook(subscribed_topic, e)]\n'}
t2020_m2 = {'prefix_validator.py': '"""Topic path subscription matcher."""\ndef is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:\n    return subscribed_pattern.strip("/") == event_topic.strip("/")\n\ndef clean_topic_segment(topic: str) -> str:\n    return topic.strip().lower()\n'}
register_task(
    tid=2020,
    family='permission_prefix',
    name='Webhook Subscription Scope Enforcer',
    class_tag='TAUGHT',
    issue="Event bus leak EVT-918: Consumer subscribed to 'orders' topic received internal administrative events from 'orders_admin'.",
    traceback_text='FAILED tests/test_scope_cases.py::test_channel_routing - AssertionError: assert True is False',
    traceback_files=['scope_checker.py'],
    repo=t2020_repo,
    hidden=t2020_hidden,
    ref=t2020_ref,
    mutant1=t2020_m1,
    mutant2=t2020_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H06'],
)

# Task 2021: Priority Job Queue Dispatcher (STATED)
t2021_repo = {'job.py': '"""Background worker job schemas."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass JobItem:\n    job_id: int\n    priority: int\n    payload: str\n    status: str = "PENDING"\n    retry_count: int = 0\n\n    def is_pending(self) -> bool:\n        return self.status == "PENDING"\n\n    def mark_completed(self) -> None:\n        self.status = "COMPLETED"\n\n    def to_envelope(self) -> Dict[str, Any]:\n        return {\n            "id": self.job_id,\n            "priority": self.priority,\n            "payload": self.payload,\n            "status": self.status,\n        }\n', 'queue_metrics.py': '"""Job queue depth monitoring."""\nfrom typing import List\nfrom job import JobItem\n\ndef compute_queue_load(jobs: List[JobItem]) -> int:\n    return sum(j.priority for j in jobs)\n\ndef count_pending_jobs(jobs: List[JobItem]) -> int:\n    return sum(1 for j in jobs if j.is_pending())\n', 'dispatcher.py': '"""Background job queue dispatcher."""\nfrom typing import List\nfrom job import JobItem\nfrom queue_metrics import compute_queue_load\n\ndef order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:\n    """Order jobs for dispatch processing.\n    Ordering contract:\n    - Sort jobs by descending priority.\n    - Tiebreaker: break ties on equal priority using job_id in ascending order (deterministic FIFO).\n    """\n    _ = compute_queue_load(jobs)\n    return sorted(jobs, key=lambda j: (j.priority, j.job_id), reverse=True)\n\ndef select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:\n    ordered = order_jobs_for_dispatch(jobs)\n    return ordered[:batch_size]\n\ndef get_highest_priority_job(jobs: List[JobItem]):\n    ordered = order_jobs_for_dispatch(jobs)\n    return ordered[0] if ordered else None\n', 'tests/test_dispatcher.py': 'from job import JobItem\nfrom dispatcher import order_jobs_for_dispatch\n\ndef test_distinct_priorities():\n    j1 = JobItem(1, 10, "low")\n    j2 = JobItem(2, 50, "high")\n    ordered = order_jobs_for_dispatch([j1, j2])\n    assert ordered[0].job_id == 2\n    assert ordered[1].job_id == 1\n'}
t2021_hidden = {'tests/test_dispatcher_cases.py': 'from job import JobItem\nfrom dispatcher import order_jobs_for_dispatch\n\ndef test_equal_priority_tiebreak():\n    j_early = JobItem(101, 100, "early")\n    j_late = JobItem(102, 100, "late")\n    ordered = order_jobs_for_dispatch([j_late, j_early])\n    assert ordered[0].job_id == 101\n    assert ordered[1].job_id == 102\n'}
t2021_ref = {'dispatcher.py': '"""Background job queue dispatcher."""\nfrom typing import List\nfrom job import JobItem\nfrom queue_metrics import compute_queue_load\n\ndef order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:\n    """Order jobs for dispatch processing.\n    Ordering contract:\n    - Sort jobs by descending priority.\n    - Tiebreaker: break ties on equal priority using job_id in ascending order (deterministic FIFO).\n    """\n    _ = compute_queue_load(jobs)\n    return sorted(jobs, key=lambda j: (-j.priority, j.job_id))\n\ndef select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:\n    ordered = order_jobs_for_dispatch(jobs)\n    return ordered[:batch_size]\n'}
t2021_m1 = {'dispatcher.py': '"""Background job queue dispatcher."""\nfrom typing import List\nfrom job import JobItem\nfrom queue_metrics import compute_queue_load\n\ndef order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:\n    _ = compute_queue_load(jobs)\n    return sorted(jobs, key=lambda j: (-j.priority, -j.job_id))\n'}
t2021_m2 = {'dispatcher.py': '"""Background job queue dispatcher."""\nfrom typing import List\nfrom job import JobItem\nfrom queue_metrics import compute_queue_load\n\ndef order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:\n    _ = compute_queue_load(jobs)\n    return sorted(jobs, key=lambda j: -j.priority)\n'}
register_task(
    tid=2021,
    family='event_ordering',
    name='Priority Job Queue Dispatcher',
    class_tag='STATED',
    issue='Worker queue anomaly WRK-112: Background worker processed equal-priority tasks out of order under simultaneous job enqueue bursts.',
    traceback_text='FAILED tests/test_dispatcher_cases.py::test_equal_priority_tiebreak - AssertionError: assert 102 == 101',
    traceback_files=['dispatcher.py'],
    repo=t2021_repo,
    hidden=t2021_hidden,
    ref=t2021_ref,
    mutant1=t2021_m1,
    mutant2=t2021_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H07'],
)

# Task 2022: Notification Batch Sorter (TAUGHT)
t2022_repo = {'notification.py': '"""Notification queue payload."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass NotificationMessage:\n    msg_id: int\n    priority: int\n    timestamp: int\n    channel: str = "PUSH"\n    read: bool = False\n\n    def is_urgent(self) -> bool:\n        return self.priority >= 10\n\n    def mark_read(self) -> None:\n        self.read = True\n\n    def to_dict(self) -> Dict[str, Any]:\n        return {\n            "id": self.msg_id,\n            "priority": self.priority,\n            "ts": self.timestamp,\n            "channel": self.channel,\n        }\n', 'formatter.py': '"""Notification payload formatters."""\nfrom typing import List\nfrom notification import NotificationMessage\n\ndef format_batch_summary(batch: List[NotificationMessage]) -> str:\n    return f"Batch size={len(batch)}"\n\ndef group_by_channel(batch: List[NotificationMessage]) -> dict:\n    res = {}\n    for m in batch:\n        res.setdefault(m.channel, []).append(m)\n    return res\n', 'sorter.py': '"""Notification priority batch sorter."""\nfrom typing import List\nfrom notification import NotificationMessage\nfrom formatter import format_batch_summary\n\ndef sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    """Sort notification messages in batch by priority level."""\n    _ = format_batch_summary(batch)\n    return sorted(batch, key=lambda m: -m.priority)\n\ndef extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    sorted_msgs = sort_notification_batch(batch)\n    return [m for m in sorted_msgs if m.is_urgent()]\n\ndef get_oldest_notification(batch: List[NotificationMessage]):\n    if not batch:\n        return None\n    return min(batch, key=lambda m: m.timestamp)\n', 'tests/test_sorter.py': 'from notification import NotificationMessage\nfrom sorter import sort_notification_batch\n\ndef test_priority_ordering():\n    m1 = NotificationMessage(1, 10, 100)\n    m2 = NotificationMessage(2, 50, 100)\n    res = sort_notification_batch([m1, m2])\n    assert res[0].msg_id == 2\n\ndef test_priority_tiebreak():\n    m_first = NotificationMessage(10, 5, 1000)\n    m_second = NotificationMessage(20, 5, 2000)\n    res = sort_notification_batch([m_second, m_first])\n    assert res[0].timestamp <= res[1].timestamp\n'}
t2022_hidden = {'tests/test_sorter_cases.py': 'from notification import NotificationMessage\nfrom sorter import sort_notification_batch\n\ndef test_timestamp_order():\n    m_early = NotificationMessage(101, 10, 500)\n    m_late = NotificationMessage(102, 10, 800)\n    res = sort_notification_batch([m_late, m_early])\n    assert res[0].msg_id == 101\n    assert res[1].msg_id == 102\n'}
t2022_ref = {'sorter.py': '"""Notification priority batch sorter."""\nfrom typing import List\nfrom notification import NotificationMessage\nfrom formatter import format_batch_summary\n\ndef sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    """Sort notification messages in batch by priority level."""\n    _ = format_batch_summary(batch)\n    return sorted(batch, key=lambda m: (-m.priority, m.timestamp))\n\ndef extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    sorted_msgs = sort_notification_batch(batch)\n    return [m for m in sorted_msgs if m.is_urgent()]\n'}
t2022_m1 = {'sorter.py': '"""Notification priority batch sorter."""\nfrom typing import List\nfrom notification import NotificationMessage\nfrom formatter import format_batch_summary\n\ndef sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    _ = format_batch_summary(batch)\n    return sorted(batch, key=lambda m: (-m.priority, -m.timestamp))\n\ndef extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    sorted_msgs = sort_notification_batch(batch)\n    return [m for m in sorted_msgs if m.is_urgent()]\n'}
t2022_m2 = {'sorter.py': '"""Notification priority batch sorter."""\nfrom typing import List\nfrom notification import NotificationMessage\nfrom formatter import format_batch_summary\n\ndef sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    _ = format_batch_summary(batch)\n    return sorted(batch, key=lambda m: -m.priority)\n\ndef extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:\n    sorted_msgs = sort_notification_batch(batch)\n    return [m for m in sorted_msgs if m.is_urgent()]\n'}
register_task(
    tid=2022,
    family='event_ordering',
    name='Notification Batch Sorter',
    class_tag='TAUGHT',
    issue='Delivery alert NOTIF-702: Urgent user alerts with identical priority tiers were delivered out of chronological order.',
    traceback_text='FAILED tests/test_sorter.py::test_priority_tiebreak - AssertionError: assert 2000 <= 1000',
    traceback_files=['sorter.py'],
    repo=t2022_repo,
    hidden=t2022_hidden,
    ref=t2022_ref,
    mutant1=t2022_m1,
    mutant2=t2022_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H07'],
)

# Task 2023: Task Scheduler Queue Rebalancer (STATED)
t2023_repo = {'task_item.py': '"""Scheduled task models."""\nfrom dataclasses import dataclass\nfrom typing import Optional, Dict, Any\n\n@dataclass\nclass ScheduledTask:\n    task_id: int\n    weight: int\n    sequence: int\n    active: bool = True\n    assigned_worker: Optional[str] = None\n\n    def is_heavy(self) -> bool:\n        return self.weight >= 50\n\n    def assign(self, worker_id: str) -> None:\n        self.assigned_worker = worker_id\n\n    def to_summary(self) -> Dict[str, Any]:\n        return {\n            "id": self.task_id,\n            "weight": self.weight,\n            "seq": self.sequence,\n        }\n', 'metrics.py': '"""Task queue depth metrics."""\nfrom typing import List\nfrom task_item import ScheduledTask\n\ndef total_pending_weight(tasks: List[ScheduledTask]) -> int:\n    return sum(t.weight for t in tasks)\n\ndef average_task_weight(tasks: List[ScheduledTask]) -> float:\n    return total_pending_weight(tasks) / len(tasks) if tasks else 0.0\n', 'rebalancer.py': '"""Scheduler queue rebalancer."""\nfrom typing import List, Optional\nfrom task_item import ScheduledTask\nfrom metrics import total_pending_weight\n\ndef rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:\n    """Rebalance scheduled task list.\n    Ordering contract:\n    - Sort tasks by weight in descending order.\n    - Tiebreaker: break equal-weight ties using sequence in ascending order.\n    """\n    _ = total_pending_weight(tasks)\n    return sorted(tasks, key=lambda t: (t.weight, t.sequence))\n\ndef get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:\n    rebalanced = rebalance_tasks(tasks)\n    return rebalanced[0] if rebalanced else None\n\ndef filter_active_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:\n    return [t for t in tasks if t.active]\n', 'tests/test_rebalancer.py': 'from task_item import ScheduledTask\nfrom rebalancer import rebalance_tasks\n\ndef test_basic_rebalance():\n    t1 = ScheduledTask(1, 10, 1)\n    t2 = ScheduledTask(2, 50, 1)\n    res = rebalance_tasks([t1, t2])\n    assert res[0].weight == 50\n\ndef test_weight_ordering():\n    t1 = ScheduledTask(1, 5, 1)\n    t2 = ScheduledTask(2, 20, 2)\n    assert rebalance_tasks([t1, t2])[0].task_id == 2\n'}
t2023_hidden = {'tests/test_rebalancer_cases.py': 'from task_item import ScheduledTask\nfrom rebalancer import rebalance_tasks\n\ndef test_sequence_ordering():\n    t_first = ScheduledTask(10, 100, 1)\n    t_second = ScheduledTask(20, 100, 2)\n    res = rebalance_tasks([t_second, t_first])\n    assert res[0].task_id == 10\n    assert res[1].task_id == 20\n'}
t2023_ref = {'rebalancer.py': '"""Scheduler queue rebalancer."""\nfrom typing import List, Optional\nfrom task_item import ScheduledTask\nfrom metrics import total_pending_weight\n\ndef rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:\n    """Rebalance scheduled task list.\n    Ordering contract:\n    - Sort tasks by weight in descending order.\n    - Tiebreaker: break equal-weight ties using sequence in ascending order.\n    """\n    _ = total_pending_weight(tasks)\n    return sorted(tasks, key=lambda t: (-t.weight, t.sequence))\n\ndef get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:\n    rebalanced = rebalance_tasks(tasks)\n    return rebalanced[0] if rebalanced else None\n'}
t2023_m1 = {'rebalancer.py': '"""Scheduler queue rebalancer."""\nfrom typing import List, Optional\nfrom task_item import ScheduledTask\nfrom metrics import total_pending_weight\n\ndef rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:\n    _ = total_pending_weight(tasks)\n    return sorted(tasks, key=lambda t: (-t.weight, -t.sequence))\n\ndef get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:\n    rebalanced = rebalance_tasks(tasks)\n    return rebalanced[0] if rebalanced else None\n'}
t2023_m2 = {'rebalancer.py': '"""Scheduler queue rebalancer."""\nfrom typing import List, Optional\nfrom task_item import ScheduledTask\nfrom metrics import total_pending_weight\n\ndef rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:\n    _ = total_pending_weight(tasks)\n    return sorted(tasks, key=lambda t: (t.weight, t.sequence))\n\ndef get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:\n    rebalanced = rebalance_tasks(tasks)\n    return rebalanced[0] if rebalanced else None\n'}
register_task(
    tid=2023,
    family='event_ordering',
    name='Task Scheduler Queue Rebalancer',
    class_tag='STATED',
    issue='Task scheduler incident SCHED-404: Low-weight background tasks scheduled before heavy priority jobs after queue rebalance.',
    traceback_text='FAILED tests/test_rebalancer.py::test_weight_ordering - AssertionError: assert 1 == 2',
    traceback_files=['rebalancer.py'],
    repo=t2023_repo,
    hidden=t2023_hidden,
    ref=t2023_ref,
    mutant1=t2023_m1,
    mutant2=t2023_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H07'],
)

# Task 2024: Event Stream Ingestion Sequencer (TAUGHT)
t2024_repo = {'event_packet.py': '"""Stream event packet model."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any, Optional\n\n@dataclass\nclass EventPacket:\n    stream_id: str\n    severity: int\n    offset: int\n    topic: str = "telemetry"\n    processed: bool = False\n\n    def is_critical(self) -> bool:\n        return self.severity >= 9\n\n    def mark_processed(self) -> None:\n        self.processed = True\n\n    def to_dict(self) -> Dict[str, Any]:\n        return {\n            "stream_id": self.stream_id,\n            "severity": self.severity,\n            "offset": self.offset,\n            "topic": self.topic,\n        }\n', 'sort_helper.py': '"""Internal stream sorting helper."""\nfrom typing import List\nfrom event_packet import EventPacket\n\ndef order_packets(packets: List[EventPacket]) -> List[EventPacket]:\n    return sorted(packets, key=lambda p: -p.severity)\n\ndef get_max_severity(packets: List[EventPacket]) -> int:\n    return max((p.severity for p in packets), default=0)\n\ndef count_critical_packets(packets: List[EventPacket]) -> int:\n    return sum(1 for p in packets if p.is_critical())\n', 'sequencer.py': '"""Stream event sequencer."""\nfrom typing import List\nfrom sort_helper import order_packets, get_max_severity\nfrom event_packet import EventPacket\n\ndef sequence_stream_batch(packets: List[EventPacket]) -> List[EventPacket]:\n    """Sequence event packets by severity."""\n    return order_packets(packets)\n\ndef get_highest_priority_packet(packets: List[EventPacket]):\n    ordered = sequence_stream_batch(packets)\n    return ordered[0] if ordered else None\n\ndef get_batch_severity_peak(packets: List[EventPacket]) -> int:\n    return get_max_severity(packets)\n', 'tests/test_sequencer.py': 'from event_packet import EventPacket\nfrom sequencer import sequence_stream_batch\n\ndef test_nominal_severity():\n    p1 = EventPacket("s1", 1, 10)\n    p2 = EventPacket("s2", 5, 10)\n    res = sequence_stream_batch([p1, p2])\n    assert res[0].severity == 5\n'}
t2024_hidden = {'tests/test_sequencer_cases.py': 'from event_packet import EventPacket\nfrom sequencer import sequence_stream_batch\nfrom sort_helper import order_packets\n\ndef test_stream_sequencing():\n    p_early = EventPacket("early", 10, 100)\n    p_late = EventPacket("late", 10, 200)\n    res = sequence_stream_batch([p_late, p_early])\n    assert res[0].stream_id == "early"\n    assert res[1].stream_id == "late"\n\ndef test_sort_helper_contract():\n    p1 = EventPacket("a", 5, 1)\n    p2 = EventPacket("b", 5, 2)\n    assert order_packets([p2, p1])[0].stream_id == "a"\n'}
t2024_ref = {'sort_helper.py': '"""Internal stream sorting helper."""\nfrom typing import List\nfrom event_packet import EventPacket\n\ndef order_packets(packets: List[EventPacket]) -> List[EventPacket]:\n    return sorted(packets, key=lambda p: (-p.severity, p.offset))\n\ndef get_max_severity(packets: List[EventPacket]) -> int:\n    return max((p.severity for p in packets), default=0)\n'}
t2024_m1 = {'sequencer.py': '"""Stream event sequencer."""\nfrom typing import List\nfrom sort_helper import order_packets\nfrom event_packet import EventPacket\n\ndef sequence_stream_batch(packets: List[EventPacket]) -> List[EventPacket]:\n    return sorted(order_packets(packets), key=lambda p: (-p.severity, p.offset))\n\ndef get_highest_priority_packet(packets: List[EventPacket]):\n    ordered = sequence_stream_batch(packets)\n    return ordered[0] if ordered else None\n'}
t2024_m2 = {'sort_helper.py': '"""Internal stream sorting helper."""\nfrom typing import List\nfrom event_packet import EventPacket\n\ndef order_packets(packets: List[EventPacket]) -> List[EventPacket]:\n    return sorted(packets, key=lambda p: (-p.severity, -p.offset))\n\ndef get_max_severity(packets: List[EventPacket]) -> int:\n    return max((p.severity for p in packets), default=0)\n'}
register_task(
    tid=2024,
    family='event_ordering',
    name='Event Stream Ingestion Sequencer',
    class_tag='TAUGHT',
    issue='Data pipeline crash STRM-308: Out-of-order stream offsets caused state replication desync during high-severity packet bursts.',
    traceback_text="FAILED tests/test_sequencer_cases.py::test_stream_sequencing - AssertionError: assert 'late' == 'early'",
    traceback_files=['sequencer.py'],
    repo=t2024_repo,
    hidden=t2024_hidden,
    ref=t2024_ref,
    mutant1=t2024_m1,
    mutant2=t2024_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H07'],
)

# Task 2025: In-Memory Token Cache (TRANSFER)
t2025_repo = {'token_record.py': '"""Token metadata schemas."""\nfrom dataclasses import dataclass\nfrom typing import Dict, Any\n\n@dataclass\nclass CachedToken:\n    token_str: str\n    expires_at: float\n    scope: str = "read_write"\n\n    def is_expired_at(self, current_time: float) -> bool:\n        return current_time >= self.expires_at\n', 'cache_utils.py': '"""Cache key hashing and diagnostics."""\ndef format_cache_key(prefix: str, identifier: str) -> str:\n    return f"{prefix}::{identifier}"\n', 'cache.py': '"""In-memory security token cache."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom token_record import CachedToken\nfrom cache_utils import format_cache_key\n\nclass TokenCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        """In-memory token cache with injectable clock."""\n        self._clock = clock or time.time\n        self._store: Dict[str, CachedToken] = {}\n\n    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:\n        now = self._clock()\n        norm_key = format_cache_key("tok", key)\n        self._store[norm_key] = CachedToken(token_str=token_str, expires_at=now + ttl_seconds)\n\n    def get(self, key: str) -> Optional[str]:\n        norm_key = format_cache_key("tok", key)\n        entry = self._store.get(norm_key)\n        if not entry:\n            return None\n        now = self._clock()\n        if now > entry.expires_at:\n            del self._store[norm_key]\n            return None\n        return entry.token_str\n\n    def size(self) -> int:\n        return len(self._store)\n', 'tests/test_cache.py': 'from cache import TokenCache\n\ndef test_cache_set_get():\n    c = TokenCache()\n    c.set("k1", "tok-1", 100.0)\n    assert c.get("k1") == "tok-1"\n'}
t2025_hidden = {'tests/test_cache_cases.py': 'from cache import TokenCache\n\ndef test_token_expiry():\n    t = [100.0]\n    c = TokenCache(clock=lambda: t[0])\n    c.set("k1", "val1", 5.0)\n    assert c.get("k1") == "val1"\n    \n    t[0] = 105.0\n    assert c.get("k1") is None\n'}
t2025_ref = {'cache.py': '"""In-memory security token cache."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom token_record import CachedToken\nfrom cache_utils import format_cache_key\n\nclass TokenCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        """In-memory token cache with injectable clock."""\n        self._clock = clock if clock is not None else time.monotonic\n        self._store: Dict[str, CachedToken] = {}\n\n    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:\n        now = self._clock()\n        norm_key = format_cache_key("tok", key)\n        self._store[norm_key] = CachedToken(token_str=str(token_str), expires_at=now + ttl_seconds)\n\n    def get(self, key: str) -> Optional[str]:\n        norm_key = format_cache_key("tok", key)\n        entry = self._store.get(norm_key)\n        if not entry:\n            return None\n        now = self._clock()\n        if now >= entry.expires_at:\n            del self._store[norm_key]\n            return None\n        return entry.token_str\n\n    def size(self) -> int:\n        return len(self._store)\n'}
t2025_m1 = {'cache.py': '"""In-memory security token cache."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom token_record import CachedToken\nfrom cache_utils import format_cache_key\n\nclass TokenCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock if clock is not None else time.time\n        self._store: Dict[str, CachedToken] = {}\n\n    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:\n        now = self._clock()\n        norm_key = format_cache_key("tok", key)\n        self._store[norm_key] = CachedToken(token_str=token_str, expires_at=now + ttl_seconds)\n\n    def get(self, key: str) -> Optional[str]:\n        norm_key = format_cache_key("tok", key)\n        entry = self._store.get(norm_key)\n        if not entry:\n            return None\n        now = self._clock()\n        if now > entry.expires_at:\n            del self._store[norm_key]\n            return None\n        return entry.token_str\n'}
t2025_m2 = {'cache.py': '"""In-memory security token cache."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom token_record import CachedToken\nfrom cache_utils import format_cache_key\n\nclass TokenCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock or time.monotonic\n        self._store: Dict[str, CachedToken] = {}\n\n    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:\n        now = self._clock()\n        norm_key = format_cache_key("tok", key)\n        self._store[norm_key] = CachedToken(token_str=token_str, expires_at=now + ttl_seconds)\n\n    def get(self, key: str) -> Optional[str]:\n        norm_key = format_cache_key("tok", key)\n        entry = self._store.get(norm_key)\n        if not entry:\n            return None\n        now = self._clock()\n        if now > entry.expires_at:\n            del self._store[norm_key]\n            return None\n        return entry.token_str\n'}
register_task(
    tid=2025,
    family='cache_ttl',
    name='In-Memory Token Cache',
    class_tag='TRANSFER',
    issue='Auth service failure AUTH-901: Stale bearer tokens remained valid at the exact expiration second due to loose inequality check.',
    traceback_text="FAILED tests/test_cache_cases.py::test_token_expiry - AssertionError: assert 'val1' is None",
    traceback_files=['cache.py'],
    repo=t2025_repo,
    hidden=t2025_hidden,
    ref=t2025_ref,
    mutant1=t2025_m1,
    mutant2=t2025_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H09'],
)

# Task 2026: API Rate Limit Session Store (TRANSFER)
t2026_repo = {'session_data.py': '"""Session data structures."""\nfrom dataclasses import dataclass\n\n@dataclass\nclass RateLimitSession:\n    client_ip: str\n    request_count: int\n    expires_at: float\n    max_requests: int = 60\n\n    def has_exceeded_quota(self) -> bool:\n        return self.request_count >= self.max_requests\n', 'session_validator.py': '"""Session expiration validation logic."""\ndef is_session_expired(expires_at: float, current_ts: float) -> bool:\n    return current_ts > expires_at\n\ndef time_remaining(expires_at: float, current_ts: float) -> float:\n    return max(0.0, expires_at - current_ts)\n', 'session_store.py': '"""Rate limit session storage."""\nfrom typing import Optional, Callable\nfrom session_validator import is_session_expired\nfrom session_data import RateLimitSession\n\nclass SessionStore:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock\n        self._sessions = {}\n\n    def register(self, ip: str, ttl: float) -> None:\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        self._sessions[ip] = RateLimitSession(ip, 1, now + ttl)\n\n    def is_active(self, ip: str) -> bool:\n        sess = self._sessions.get(ip)\n        if not sess:\n            return False\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        return not is_session_expired(sess.expires_at, now)\n\n    def active_count(self) -> int:\n        return len(self._sessions)\n', 'tests/test_session_store.py': 'from session_store import SessionStore\n\ndef test_nominal_registration():\n    s = SessionStore()\n    s.register("192.168.1.1", 60.0)\n    assert s.is_active("192.168.1.1") is True\n'}
t2026_hidden = {'tests/test_session_store_cases.py': 'from session_store import SessionStore\nfrom session_validator import is_session_expired\n\ndef test_session_expiry():\n    t = [500.0]\n    s = SessionStore(clock=lambda: t[0])\n    s.register("10.0.0.1", 10.0)\n    assert s.is_active("10.0.0.1") is True\n    \n    t[0] = 510.0\n    assert s.is_active("10.0.0.1") is False\n\ndef test_session_validator_contract():\n    assert is_session_expired(100.0, 100.0) is True\n    assert is_session_expired(100.0, 99.9) is False\n'}
t2026_ref = {'session_validator.py': '"""Session expiration validation logic."""\ndef is_session_expired(expires_at: float, current_ts: float) -> bool:\n    return current_ts >= expires_at\n\ndef time_remaining(expires_at: float, current_ts: float) -> float:\n    return max(0.0, expires_at - current_ts)\n'}
t2026_m1 = {'session_store.py': '"""Rate limit session storage."""\nfrom typing import Optional, Callable\nfrom session_validator import is_session_expired\nfrom session_data import RateLimitSession\n\nclass SessionStore:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock\n        self._sessions = {}\n\n    def register(self, ip: str, ttl: float) -> None:\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        self._sessions[ip] = RateLimitSession(ip, 1, now + ttl)\n\n    def is_active(self, ip: str) -> bool:\n        sess = self._sessions.get(ip)\n        if not sess:\n            return False\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        if now >= sess.expires_at:\n            return False\n        return not is_session_expired(sess.expires_at, now)\n\n    def active_count(self) -> int:\n        return len(self._sessions)\n'}
t2026_m2 = {'session_validator.py': '"""Session expiration validation logic."""\ndef is_session_expired(expires_at: float, current_ts: float) -> bool:\n    return current_ts > expires_at\n\ndef time_remaining(expires_at: float, current_ts: float) -> float:\n    return max(0.0, expires_at - current_ts)\n'}
register_task(
    tid=2026,
    family='cache_ttl',
    name='API Rate Limit Session Store',
    class_tag='TRANSFER',
    issue='Rate limiter bypass RL-103: API client requests allowed through after session limit expired due to boundary condition error.',
    traceback_text='FAILED tests/test_session_store_cases.py::test_session_expiry - AssertionError: assert True is False',
    traceback_files=['session_store.py'],
    repo=t2026_repo,
    hidden=t2026_hidden,
    ref=t2026_ref,
    mutant1=t2026_m1,
    mutant2=t2026_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H09'],
)

# Task 2027: Distributed Lease Expiry Guard (TRANSFER)
t2027_repo = {'lease_entry.py': '"""Lease entry metadata."""\nfrom dataclasses import dataclass\nfrom typing import Optional\n\n@dataclass\nclass LeaseRecord:\n    lease_key: str\n    owner: str\n    valid_until: float\n    fencing_token: int = 100\n\n    def matches_owner(self, candidate: str) -> bool:\n        return self.owner == candidate\n', 'clock_source.py': '"""Lease validity checker."""\ndef is_lease_valid(valid_until: float, current_time: float) -> bool:\n    return current_time <= valid_until\n\ndef remaining_lease_time(valid_until: float, current_time: float) -> float:\n    return max(0.0, valid_until - current_time)\n', 'lease_guard.py': '"""Distributed cluster lease manager."""\nfrom typing import Optional, Callable\nfrom clock_source import is_lease_valid\nfrom lease_entry import LeaseRecord\n\nclass LeaseGuard:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock\n        self._leases = {}\n\n    def acquire(self, key: str, owner: str, lease_duration: float) -> None:\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        self._leases[key] = LeaseRecord(key, owner, now + lease_duration)\n\n    def holds_lease(self, key: str, owner: str) -> bool:\n        lease = self._leases.get(key)\n        if not lease or lease.owner != owner:\n            return False\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        return is_lease_valid(lease.valid_until, now)\n\n    def lease_count(self) -> int:\n        return len(self._leases)\n', 'tests/test_lease.py': 'from lease_guard import LeaseGuard\n\ndef test_nominal_lease():\n    lg = LeaseGuard()\n    lg.acquire("lock1", "nodeA", 30.0)\n    assert lg.holds_lease("lock1", "nodeA") is True\n'}
t2027_hidden = {'tests/test_lease_cases.py': 'from lease_guard import LeaseGuard\nfrom clock_source import is_lease_valid\n\ndef test_lease_validity_boundary():\n    t = [1000.0]\n    lg = LeaseGuard(clock=lambda: t[0])\n    lg.acquire("resource_db", "node1", 5.0)\n    assert lg.holds_lease("resource_db", "node1") is True\n    \n    t[0] = 1005.0\n    assert lg.holds_lease("resource_db", "node1") is False\n\ndef test_clock_source_contract():\n    assert is_lease_valid(100.0, 100.0) is False\n    assert is_lease_valid(100.0, 99.0) is True\n'}
t2027_ref = {'clock_source.py': '"""Lease validity checker."""\ndef is_lease_valid(valid_until: float, current_time: float) -> bool:\n    return current_time < valid_until\n\ndef remaining_lease_time(valid_until: float, current_time: float) -> float:\n    return max(0.0, valid_until - current_time)\n'}
t2027_m1 = {'lease_guard.py': '"""Distributed cluster lease manager."""\nfrom typing import Optional, Callable\nfrom clock_source import is_lease_valid\nfrom lease_entry import LeaseRecord\n\nclass LeaseGuard:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock\n        self._leases = {}\n\n    def acquire(self, key: str, owner: str, lease_duration: float) -> None:\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        self._leases[key] = LeaseRecord(key, owner, now + lease_duration)\n\n    def holds_lease(self, key: str, owner: str) -> bool:\n        lease = self._leases.get(key)\n        if not lease or lease.owner != owner:\n            return False\n        import time\n        now = self._clock() if self._clock else time.monotonic()\n        if now >= lease.valid_until:\n            return False\n        return is_lease_valid(lease.valid_until, now)\n\n    def lease_count(self) -> int:\n        return len(self._leases)\n'}
t2027_m2 = {'clock_source.py': '"""Lease validity checker."""\ndef is_lease_valid(valid_until: float, current_time: float) -> bool:\n    return current_time <= valid_until\n\ndef remaining_lease_time(valid_until: float, current_time: float) -> float:\n    return max(0.0, valid_until - current_time)\n'}
register_task(
    tid=2027,
    family='cache_ttl',
    name='Distributed Lease Expiry Guard',
    class_tag='TRANSFER',
    issue='Distributed lock split-brain LOCK-881: Two nodes simultaneously held master lock when lease was retained at exact expiration second.',
    traceback_text='FAILED tests/test_lease_cases.py::test_lease_validity_boundary - AssertionError: assert True is False',
    traceback_files=['lease_guard.py'],
    repo=t2027_repo,
    hidden=t2027_hidden,
    ref=t2027_ref,
    mutant1=t2027_m1,
    mutant2=t2027_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    root_cause_only_with_exploration=True,
    handbook_citations=['Rule H09'],
)

# Task 2028: DNS Cache TTL Resolver (TRANSFER)
t2028_repo = {'dns_record.py': '"""DNS record entry model."""\nfrom dataclasses import dataclass\nfrom typing import Optional\n\n@dataclass\nclass DnsEntry:\n    domain: str\n    ip_addr: str\n    expires_at: float\n    record_type: str = "A"\n\n    def is_valid_format(self) -> bool:\n        return "." in self.ip_addr\n', 'dns_utils.py': '"""DNS domain utilities."""\ndef normalize_domain_name(name: str) -> str:\n    return name.strip().lower().rstrip(".")\n', 'dns_resolver.py': '"""DNS cache resolver client."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom dns_record import DnsEntry\nfrom dns_utils import normalize_domain_name\n\nclass DnsCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock or time.time\n        self._entries: Dict[str, DnsEntry] = {}\n\n    def put_record(self, domain: str, ip: str, ttl: float) -> None:\n        clean_domain = normalize_domain_name(domain)\n        now = self._clock()\n        self._entries[clean_domain] = DnsEntry(clean_domain, ip, now + ttl)\n\n    def lookup(self, domain: str) -> Optional[str]:\n        clean_domain = normalize_domain_name(domain)\n        entry = self._entries.get(clean_domain)\n        if not entry:\n            return None\n        now = self._clock()\n        if now > entry.expires_at:\n            del self._entries[clean_domain]\n            return None\n        return entry.ip_addr\n\n    def count(self) -> int:\n        return len(self._entries)\n', 'tests/test_dns.py': 'from dns_resolver import DnsCache\n\ndef test_dns_lookup():\n    cache = DnsCache()\n    cache.put_record("example.com", "93.184.216.34", 10.0)\n    assert cache.lookup("example.com") == "93.184.216.34"\n\ndef test_clock_advance():\n    clock_calls = [0]\n    def fake_clock():\n        clock_calls[0] += 1\n        return 1000.0\n    cache = DnsCache(clock=fake_clock)\n    cache.put_record("test.org", "1.1.1.1", 5.0)\n    assert clock_calls[0] > 0\n'}
t2028_hidden = {'tests/test_dns_cases.py': 'from dns_resolver import DnsCache\n\ndef test_dns_ttl_boundary():\n    t = [100.0]\n    cache = DnsCache(clock=lambda: t[0])\n    cache.put_record("service.internal", "10.0.0.5", 3.0)\n    assert cache.lookup("service.internal") == "10.0.0.5"\n    \n    t[0] = 103.0\n    assert cache.lookup("service.internal") is None\n'}
t2028_ref = {'dns_resolver.py': '"""DNS cache resolver client."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom dns_record import DnsEntry\nfrom dns_utils import normalize_domain_name\n\nclass DnsCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock if clock is not None else time.monotonic\n        self._entries: Dict[str, DnsEntry] = {}\n\n    def put_record(self, domain: str, ip: str, ttl: float) -> None:\n        clean_domain = normalize_domain_name(domain)\n        now = self._clock()\n        self._entries[clean_domain] = DnsEntry(clean_domain, ip, now + ttl)\n\n    def lookup(self, domain: str) -> Optional[str]:\n        clean_domain = normalize_domain_name(domain)\n        entry = self._entries.get(clean_domain)\n        if not entry:\n            return None\n        now = self._clock()\n        if now >= entry.expires_at:\n            del self._entries[clean_domain]\n            return None\n        return entry.ip_addr\n\n    def count(self) -> int:\n        return len(self._entries)\n'}
t2028_m1 = {'dns_resolver.py': '"""DNS cache resolver client."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom dns_record import DnsEntry\nfrom dns_utils import normalize_domain_name\n\nclass DnsCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = clock if clock is not None else time.monotonic\n        self._entries: Dict[str, DnsEntry] = {}\n\n    def put_record(self, domain: str, ip: str, ttl: float) -> None:\n        clean_domain = normalize_domain_name(domain)\n        now = self._clock()\n        self._entries[clean_domain] = DnsEntry(clean_domain, ip, now + ttl)\n\n    def lookup(self, domain: str) -> Optional[str]:\n        clean_domain = normalize_domain_name(domain)\n        entry = self._entries.get(clean_domain)\n        if not entry:\n            return None\n        now = self._clock()\n        if now > entry.expires_at:\n            del self._entries[clean_domain]\n            return None\n        return entry.ip_addr\n\n    def count(self) -> int:\n        return len(self._entries)\n'}
t2028_m2 = {'dns_resolver.py': '"""DNS cache resolver client."""\nimport time\nfrom typing import Dict, Optional, Callable\nfrom dns_record import DnsEntry\nfrom dns_utils import normalize_domain_name\n\nclass DnsCache:\n    def __init__(self, clock: Optional[Callable[[], float]] = None):\n        self._clock = time.time\n        self._entries: Dict[str, DnsEntry] = {}\n\n    def put_record(self, domain: str, ip: str, ttl: float) -> None:\n        clean_domain = normalize_domain_name(domain)\n        self._entries[clean_domain] = DnsEntry(clean_domain, ip, time.time() + ttl)\n\n    def lookup(self, domain: str) -> Optional[str]:\n        clean_domain = normalize_domain_name(domain)\n        entry = self._entries.get(clean_domain)\n        if not entry or time.time() >= entry.expires_at:\n            return None\n        return entry.ip_addr\n\n    def count(self) -> int:\n        return len(self._entries)\n'}
register_task(
    tid=2028,
    family='cache_ttl',
    name='DNS Cache TTL Resolver',
    class_tag='TRANSFER',
    issue='Network resolution failure NET-505: Expired upstream DNS record routed traffic to decommissioned server IP address at exact TTL deadline.',
    traceback_text="FAILED tests/test_dns_cases.py::test_dns_ttl_boundary - AssertionError: assert '10.0.0.5' is None",
    traceback_files=['dns_resolver.py'],
    repo=t2028_repo,
    hidden=t2028_hidden,
    ref=t2028_ref,
    mutant1=t2028_m1,
    mutant2=t2028_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    root_cause_only_with_exploration=False,
    handbook_citations=['Rule H09'],
)
