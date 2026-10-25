"""Family 1: money_rounding (Tasks 2001 - 2004).

Governing Rule: Rule H02 (Half-Up Rounding: round half up on cents).
Competing Alternatives: Banker's rounding, truncation, ceil.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_1(add_task):
    # =========================================================================
    # Task 2001: Order Tax Calculation (STATED, HRC=True, VTS=False)
    # =========================================================================
    t2001_repo = {
        "models.py": '''"""Data models for commerce order line items."""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class LineItem:
    sku: str
    price_cents: int
    quantity: int = 1

    def subtotal(self) -> int:
        return self.price_cents * self.quantity

@dataclass
class OrderSummary:
    order_id: str
    items: List[LineItem]
    net_cents: int
    tax_cents: int
    gross_cents: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "net_cents": self.net_cents,
            "tax_cents": self.tax_cents,
            "gross_cents": self.gross_cents,
        }
''',
        "tax_engine.py": '''"""Low-level tax rate computation engine."""
from typing import Dict, Any

DEFAULT_TAX_JURISDICTIONS = {
    "standard": 0.20,
    "reduced": 0.10,
    "exempt": 0.0,
}

def get_rate_for_jurisdiction(code: str) -> float:
    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)

def calculate_vat(net_cents: int, vat_rate: float) -> int:
    """Compute VAT in integer cents for given net amount."""
    return int(net_cents * vat_rate)
''',
        "pricing.py": '''"""Order pricing calculation with itemized taxes."""
from typing import List, Tuple, Optional
from models import LineItem, OrderSummary
from tax_engine import calculate_vat, get_rate_for_jurisdiction

def calculate_order_total(items: List[Tuple[int, int]], vat_rate: float = 0.20, order_id: str = "ORD-001") -> OrderSummary:
    """Calculate order total including tax.
    items: list of (price_cents, quantity).
    Returns OrderSummary.
    Tax calculation must use half-up rounding (ROUND_HALF_UP: ties broken towards positive infinity) on exact half-cents.
    """
    line_objs = [LineItem(sku=f"SKU-{i+1}", price_cents=p, quantity=q) for i, (p, q) in enumerate(items)]
    net = sum(item.subtotal() for item in line_objs)
    tax = calculate_vat(net, vat_rate)
    return OrderSummary(order_id=order_id, items=line_objs, net_cents=net, tax_cents=tax, gross_cents=net + tax)
''',
        "tests/test_pricing.py": '''from pricing import calculate_order_total

def test_single_item():
    summary = calculate_order_total([(100, 1)], vat_rate=0.20)
    assert summary.net_cents == 100
    assert summary.tax_cents == 20
    assert summary.gross_cents == 120

def test_multi_item():
    summary = calculate_order_total([(100, 2), (200, 1)], vat_rate=0.10)
    assert summary.net_cents == 400
    assert summary.tax_cents == 40
    assert summary.gross_cents == 440
'''
    }

    t2001_hidden = {
        "tests/test_pricing_cases.py": '''import pytest
from pricing import calculate_order_total
from tax_engine import calculate_vat

def test_vat_rate_calculation():
    assert calculate_order_total([(135, 1)], vat_rate=0.10).tax_cents == 14
    assert calculate_order_total([(145, 1)], vat_rate=0.10).tax_cents == 15
    assert calculate_order_total([(155, 1)], vat_rate=0.10).tax_cents == 16
    assert calculate_order_total([(165, 1)], vat_rate=0.10).tax_cents == 17
    assert calculate_order_total([(141, 1)], vat_rate=0.10).tax_cents == 14

def test_tax_engine_contract():
    assert calculate_vat(135, 0.10) == 14
    assert calculate_vat(145, 0.10) == 15
'''
    }

    t2001_ref = {
        "tax_engine.py": '''"""Low-level tax rate computation engine."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

DEFAULT_TAX_JURISDICTIONS = {
    "standard": 0.20,
    "reduced": 0.10,
    "exempt": 0.0,
}

def get_rate_for_jurisdiction(code: str) -> float:
    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)

def calculate_vat(net_cents: int, vat_rate: float) -> int:
    """Compute VAT in integer cents for given net amount using half-up rounding."""
    d_net = Decimal(str(net_cents))
    d_rate = Decimal(str(vat_rate))
    return int((d_net * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
'''
    }

    t2001_m1 = {
        "pricing.py": '''"""Order pricing calculation with itemized taxes."""
from typing import List, Tuple, Optional
from models import LineItem, OrderSummary
from tax_engine import calculate_vat, get_rate_for_jurisdiction
from decimal import Decimal, ROUND_HALF_EVEN

def calculate_order_total(items: List[Tuple[int, int]], vat_rate: float = 0.20, order_id: str = "ORD-001") -> OrderSummary:
    line_objs = [LineItem(sku=f"SKU-{i+1}", price_cents=p, quantity=q) for i, (p, q) in enumerate(items)]
    net = sum(item.subtotal() for item in line_objs)
    tax = int((Decimal(str(net)) * Decimal(str(vat_rate))).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
    return OrderSummary(order_id=order_id, items=line_objs, net_cents=net, tax_cents=tax, gross_cents=net + tax)
'''
    }

    t2001_m2 = {
        "tax_engine.py": '''"""Low-level tax rate computation engine."""
import math
from typing import Dict, Any

DEFAULT_TAX_JURISDICTIONS = {
    "standard": 0.20,
    "reduced": 0.10,
    "exempt": 0.0,
}

def get_rate_for_jurisdiction(code: str) -> float:
    return DEFAULT_TAX_JURISDICTIONS.get(code, 0.20)

def calculate_vat(net_cents: int, vat_rate: float) -> int:
    return int(math.ceil(net_cents * vat_rate))
'''
    }

    add_task(
        tid=2001,
        family="money_rounding",
        name="Order Tax Calculation",
        class_tag="STATED",
        issue="Incident INC-8401: Itemized billing batch reconciliation failed for customer order line items under variable VAT rates.",
        traceback_text="FAILED tests/test_pricing_cases.py::test_vat_rate_calculation - AssertionError: assert 13 == 14",
        traceback_files=["pricing.py"],
        repo=t2001_repo,
        hidden=t2001_hidden,
        ref=t2001_ref,
        mutant1=t2001_m1,
        mutant2=t2001_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H02"],
        assertions=[
            ("test_vat_rate_calculation", "pricing.py docstring: 'Tax calculation must use half-up rounding (ROUND_HALF_UP)'", "Yes", "STATED"),
            ("test_tax_engine_contract", "tax_engine.py module contract", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2002: Invoice Discount Allocation (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2002_repo = {
        "models.py": '''"""Discount rule models and line items."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class LineDiscount:
    line_id: int
    allocated_cents: int

@dataclass
class AllocationResult:
    discounts: List[int]
    total_allocated: int
    is_fully_allocated: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "discounts": self.discounts,
            "total_allocated": self.total_allocated,
            "is_fully_allocated": self.is_fully_allocated,
        }
''',
        "utils.py": '''"""Invoice discount validation helpers."""
from typing import List

def validate_line_totals(lines: List[int]) -> bool:
    return all(isinstance(x, int) and x >= 0 for x in lines)

def compute_total_cents(lines: List[int]) -> int:
    return sum(lines)
''',
        "discount.py": '''"""Invoice discount allocation module."""
from typing import List
from models import AllocationResult
from utils import validate_line_totals

def prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:
    """Prorate discount across lines proportionally to their value.
    line_totals: list of integer cents.
    Returns list of discount cents per line.
    """
    if not validate_line_totals(line_totals):
        raise ValueError("Line totals must be non-negative integers")
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    return [int(cents * total_discount_cents // total) for cents in line_totals]

def allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:
    """Wrapper returning structured allocation result."""
    allocs = prorate_discount(line_totals, total_discount_cents)
    tot = sum(allocs)
    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))
''',
        "tests/test_discount.py": '''from discount import prorate_discount, allocate_discounts

def test_even_split():
    assert prorate_discount([100, 100], 20) == [10, 10]
    res = allocate_discounts([200, 100], 30)
    assert res.discounts == [20, 10]
    assert res.total_allocated == 30

def test_zero_total():
    assert prorate_discount([0, 0], 50) == [0, 0]

def test_proportional_distribution():
    res = prorate_discount([100, 300], 100)
    assert res == [25, 75]
'''
    }

    t2002_hidden = {
        "tests/test_discount_cases.py": '''import pytest
from discount import prorate_discount

def test_fractional_split():
    assert prorate_discount([100, 100], 25) == [13, 13]
    assert prorate_discount([100, 100], 35) == [18, 18]
    assert prorate_discount([100, 100], 45) == [23, 23]

def test_multi_line_allocation():
    assert sum(prorate_discount([100, 100, 100], 30)) == 30
'''
    }

    t2002_ref = {
        "discount.py": '''"""Invoice discount allocation module."""
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from models import AllocationResult
from utils import validate_line_totals

def prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:
    """Prorate discount across lines proportionally to their value.
    line_totals: list of integer cents.
    Returns list of discount cents per line.
    """
    if not validate_line_totals(line_totals):
        raise ValueError("Line totals must be non-negative integers")
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    d_total = Decimal(str(total))
    d_disc = Decimal(str(total_discount_cents))
    res = []
    for cents in line_totals:
        share = (Decimal(str(cents)) * d_disc / d_total).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        res.append(int(share))
    return res

def allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:
    """Wrapper returning structured allocation result."""
    allocs = prorate_discount(line_totals, total_discount_cents)
    tot = sum(allocs)
    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))
'''
    }

    t2002_m1 = {
        "discount.py": '''"""Invoice discount allocation module."""
from typing import List
from decimal import Decimal, ROUND_HALF_EVEN
from models import AllocationResult
from utils import validate_line_totals

def prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:
    if not validate_line_totals(line_totals):
        raise ValueError("Line totals must be non-negative integers")
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    d_total = Decimal(str(total))
    d_disc = Decimal(str(total_discount_cents))
    return [int((Decimal(str(c)) * d_disc / d_total).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)) for c in line_totals]

def allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:
    allocs = prorate_discount(line_totals, total_discount_cents)
    tot = sum(allocs)
    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))
'''
    }

    t2002_m2 = {
        "discount.py": '''"""Invoice discount allocation module."""
from typing import List
from models import AllocationResult
from utils import validate_line_totals

def prorate_discount(line_totals: List[int], total_discount_cents: int) -> List[int]:
    if not validate_line_totals(line_totals):
        raise ValueError("Line totals must be non-negative integers")
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    return [int(c * total_discount_cents // total) for c in line_totals]

def allocate_discounts(line_totals: List[int], total_discount_cents: int) -> AllocationResult:
    allocs = prorate_discount(line_totals, total_discount_cents)
    tot = sum(allocs)
    return AllocationResult(discounts=allocs, total_allocated=tot, is_fully_allocated=(tot == total_discount_cents))
'''
    }

    add_task(
        tid=2002,
        family="money_rounding",
        name="Invoice Discount Allocation",
        class_tag="TAUGHT",
        issue="Incident INC-3902: Promotional discount allocation across invoice line items results in an unallocated penny mismatch during checkout settlement.",
        traceback_text="FAILED tests/test_discount_cases.py::test_fractional_split - AssertionError: assert [12, 12] == [13, 13]",
        traceback_files=["discount.py"],
        repo=t2002_repo,
        hidden=t2002_hidden,
        ref=t2002_ref,
        mutant1=t2002_m1,
        mutant2=t2002_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H02"],
        assertions=[
            ("test_fractional_split", "HANDBOOK.md Rule H02: Half-up rounding on half-cent boundaries", "No", "TAUGHT"),
            ("test_multi_line_allocation", "HANDBOOK.md Rule H02: Half-up rounding on half-cent boundaries", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2003: Multi-Currency Fee Conversion (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2003_repo = {
        "rates.py": '''"""Foreign exchange conversion models."""
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class FxQuote:
    base_currency: str
    quote_currency: str
    rate: float
    provider: str = "ECB"

    def is_inverted(self) -> bool:
        return self.rate < 1.0

@dataclass
class ConversionSummary:
    source_cents: int
    converted_cents: int
    applied_rate: float
''',
        "fx_engine.py": '''"""Low-level exchange rate computation."""
from typing import Tuple

def apply_fx_rate(cents: int, rate: float) -> int:
    """Compute converted currency amount in cents."""
    return int(cents * rate)

def compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:
    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)
    return apply_fx_rate(cents, effective_rate), effective_rate
''',
        "converter.py": '''"""Currency amount converter interface."""
from rates import FxQuote, ConversionSummary
from fx_engine import apply_fx_rate

def convert_currency_amount(amount_cents: int, quote: FxQuote) -> int:
    """Convert amount in base currency cents to quote currency cents.
    amount_cents: source currency amount in cents.
    quote: exchange rate quote.
    """
    return apply_fx_rate(amount_cents, quote.rate)

def build_conversion_summary(amount_cents: int, quote: FxQuote) -> ConversionSummary:
    converted = convert_currency_amount(amount_cents, quote)
    return ConversionSummary(source_cents=amount_cents, converted_cents=converted, applied_rate=quote.rate)
''',
        "tests/test_fx.py": '''from converter import convert_currency_amount, build_conversion_summary
from rates import FxQuote

def test_integer_rate():
    quote = FxQuote("USD", "EUR", 2.0)
    assert convert_currency_amount(100, quote) == 200

def test_summary_builder():
    quote = FxQuote("USD", "GBP", 0.5)
    s = build_conversion_summary(200, quote)
    assert s.converted_cents == 100
'''
    }

    t2003_hidden = {
        "tests/test_fx_cases.py": '''from converter import convert_currency_amount
from rates import FxQuote
from fx_engine import apply_fx_rate

def test_fx_conversion():
    quote = FxQuote("USD", "JPY", 1.5)
    assert convert_currency_amount(135, quote) == 203
    assert convert_currency_amount(145, quote) == 218

def test_fx_engine_contract():
    assert apply_fx_rate(135, 1.5) == 203
    assert apply_fx_rate(145, 1.5) == 218
'''
    }

    t2003_ref = {
        "fx_engine.py": '''"""Low-level exchange rate computation."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

def apply_fx_rate(cents: int, rate: float) -> int:
    """Compute converted currency amount in cents using half-up rounding."""
    d_cents = Decimal(str(cents))
    d_rate = Decimal(str(rate))
    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:
    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)
    return apply_fx_rate(cents, effective_rate), effective_rate
'''
    }

    t2003_m1 = {
        "converter.py": '''"""Currency amount converter interface."""
from rates import FxQuote, ConversionSummary
from fx_engine import apply_fx_rate
from decimal import Decimal, ROUND_HALF_EVEN

def convert_currency_amount(amount_cents: int, quote: FxQuote) -> int:
    d_cents = Decimal(str(amount_cents))
    d_rate = Decimal(str(quote.rate))
    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))

def build_conversion_summary(amount_cents: int, quote: FxQuote) -> ConversionSummary:
    converted = convert_currency_amount(amount_cents, quote)
    return ConversionSummary(source_cents=amount_cents, converted_cents=converted, applied_rate=quote.rate)
'''
    }

    t2003_m2 = {
        "fx_engine.py": '''"""Low-level exchange rate computation."""
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Tuple

def apply_fx_rate(cents: int, rate: float) -> int:
    d_cents = Decimal(str(cents))
    d_rate = Decimal(str(rate))
    return int((d_cents * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))

def compute_spread(cents: int, base_rate: float, spread_bps: int = 10) -> Tuple[int, float]:
    effective_rate = base_rate * (1.0 + spread_bps / 10000.0)
    return apply_fx_rate(cents, effective_rate), effective_rate
'''
    }

    add_task(
        tid=2003,
        family="money_rounding",
        name="Multi-Currency Fee Conversion",
        class_tag="TAUGHT",
        issue="Payment gateway ticket PAY-501: Cross-border clearing failed settlement reconciliation on fractional cent conversion batches.",
        traceback_text="FAILED tests/test_fx_cases.py::test_fx_conversion - AssertionError: assert 202 == 203",
        traceback_files=["converter.py"],
        repo=t2003_repo,
        hidden=t2003_hidden,
        ref=t2003_ref,
        mutant1=t2003_m1,
        mutant2=t2003_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H02"],
        assertions=[
            ("test_fx_conversion", "HANDBOOK.md Rule H02: Half-up rounding on half-cents", "No", "TAUGHT"),
            ("test_fx_engine_contract", "HANDBOOK.md Rule H02: Half-up rounding on half-cents", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2004: Legacy Payroll Tax Ceiling (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2004_repo = {
        "models.py": '''"""Payroll record data models."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class WithholdingRecord:
    employee_id: int
    gross_cents: int
    tax_cents: int
    exempt: bool = False
    state_code: str = "CA"

    def net_pay(self) -> int:
        return self.gross_cents - self.tax_cents

    def to_payload(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "gross_cents": self.gross_cents,
            "tax_cents": self.tax_cents,
            "exempt": self.exempt,
            "state_code": self.state_code,
        }
''',
        "validator.py": '''"""Payroll audit validators."""
from models import WithholdingRecord

def verify_withholding(record: WithholdingRecord, minimum_cents: int = 0) -> bool:
    return record.tax_cents >= minimum_cents
''',
        "payroll.py": '''"""Payroll statutory tax calculation."""
import math
from models import WithholdingRecord
from validator import verify_withholding

def compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:
    """Compute statutory payroll tax withholding.
    Statutory requirement: payroll withholding MUST round fractional cents UP (ceiling)
    to guarantee tax obligations are never under-withheld. Do NOT use half-up rounding.
    """
    return int(gross_cents * tax_rate)

def build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:
    if exempt:
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)
    else:
        tax = compute_payroll_withholding(gross_cents, tax_rate)
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)
    if not verify_withholding(rec, 0):
        raise ValueError("Negative withholding calculated")
    return rec
''',
        "tests/test_payroll.py": '''from payroll import compute_payroll_withholding, build_withholding_record

def test_integer_withholding():
    assert compute_payroll_withholding(1000, 0.10) == 100
    rec = build_withholding_record(101, 2000, 0.05)
    assert rec.tax_cents == 100

def test_fractional_withholding():
    assert compute_payroll_withholding(105, 0.10) == 11
'''
    }

    t2004_hidden = {
        "tests/test_payroll_cases.py": '''import pytest
from payroll import compute_payroll_withholding

def test_payroll_deduction_rate():
    assert compute_payroll_withholding(125, 0.10) == 13
    assert compute_payroll_withholding(145, 0.10) == 15
    assert compute_payroll_withholding(101, 0.10) == 11
'''
    }

    t2004_ref = {
        "payroll.py": '''"""Payroll statutory tax calculation."""
import math
from models import WithholdingRecord
from validator import verify_withholding

def compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:
    """Compute statutory payroll tax withholding.
    Statutory requirement: payroll withholding MUST round fractional cents UP (ceiling)
    to guarantee tax obligations are never under-withheld. Do NOT use half-up rounding.
    """
    return int(math.ceil(gross_cents * tax_rate))

def build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:
    if exempt:
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)
    else:
        tax = compute_payroll_withholding(gross_cents, tax_rate)
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)
    if not verify_withholding(rec, 0):
        raise ValueError("Negative withholding calculated")
    return rec
'''
    }

    t2004_m1 = {
        "payroll.py": '''"""Payroll statutory tax calculation."""
from decimal import Decimal, ROUND_HALF_UP
from models import WithholdingRecord
from validator import verify_withholding

def compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:
    # Mutant 1: Blindly applies Half-up rounding
    d_gross = Decimal(str(gross_cents))
    d_rate = Decimal(str(tax_rate))
    return int((d_gross * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:
    if exempt:
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)
    else:
        tax = compute_payroll_withholding(gross_cents, tax_rate)
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)
    if not verify_withholding(rec, 0):
        raise ValueError("Negative withholding calculated")
    return rec
'''
    }

    t2004_m2 = {
        "payroll.py": '''"""Payroll statutory tax calculation."""
from models import WithholdingRecord
from validator import verify_withholding

def compute_payroll_withholding(gross_cents: int, tax_rate: float) -> int:
    # Mutant 2: Truncation
    return int(gross_cents * tax_rate)

def build_withholding_record(employee_id: int, gross_cents: int, tax_rate: float, exempt: bool = False) -> WithholdingRecord:
    if exempt:
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=0, exempt=True)
    else:
        tax = compute_payroll_withholding(gross_cents, tax_rate)
        rec = WithholdingRecord(employee_id=employee_id, gross_cents=gross_cents, tax_cents=tax)
    if not verify_withholding(rec, 0):
        raise ValueError("Negative withholding calculated")
    return rec
'''
    }

    add_task(
        tid=2004,
        family="money_rounding",
        name="Legacy Payroll Tax Ceiling",
        class_tag="DISTRACTOR",
        issue="Compliance alert PAY-89: Statutory state tax withholding calculation is under-withholding on payroll processing batches.",
        traceback_text="FAILED tests/test_payroll_cases.py::test_payroll_deduction_rate - AssertionError: assert 12 == 13",
        traceback_files=["payroll.py"],
        repo=t2004_repo,
        hidden=t2004_hidden,
        ref=t2004_ref,
        mutant1=t2004_m1,
        mutant2=t2004_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H02"],
        assertions=[
            ("test_payroll_deduction_rate", "payroll.py docstring: 'MUST round fractional cents UP (ceiling)'", "Yes", "DISTRACTOR")
        ]
    )

    print("Family 1 registered (Tasks 2001-2004).")
