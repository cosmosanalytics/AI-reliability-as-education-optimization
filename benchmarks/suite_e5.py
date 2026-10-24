"""suite_e5.py: Template-generated benchmark suite for E5 evaluation (28 instances across 7 families).

Complies strictly with Section 8 Addendum v2 of REAL_TEST_REQUIREMENTS.md:
- 7 bug families, 4 distinct instances per family (28 total instances).
- Class tags: STATED (13), TAUGHT (8), DISTRACTOR (3), TRANSFER (4).
- >= 1/3 instances feature hidden-root-cause variants (bug outside the traceback file).
- >= 1/3 instances feature visible-test-sensitive variants (naive fixes fail visible tests).
- Every instance includes:
  (1) Gold reference patch passing 100% of visible and hidden tests.
  (2) Unpatched baseline failing 100% of hidden tests.
  (3) Two plausible-wrong mutant patches each failing hidden tests (mutation verification).
  (4) Minimal context package files (traceback_files) for Baseline B0 evaluation.
"""

import os
import sys

T = []


def register_task(
    tid,
    family,
    name,
    class_tag,
    issue,
    traceback_text,
    traceback_files,
    repo,
    hidden,
    ref,
    mutant1,
    mutant2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=(),
    visible=None,
    protected=(),
    forbidden=(),
    must_touch=(),
):
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


# ==============================================================================
# FAMILY 1: money_rounding (Tasks 2001 - 2004)
# ==============================================================================

# Task 2001: Order Tax Calculation (STATED)
t2001_repo = {
    "pricing.py": '''"""Order pricing calculation with itemized taxes."""
from tax_engine import calculate_vat

def calculate_order_total(items, vat_rate=0.20):
    """Calculate order total including tax.
    items: list of (price_cents, quantity).
    Returns (net_cents, tax_cents, gross_cents).
    Tax must use banker's rounding (round half to even) on exact half-cents.
    """
    net = sum(price * qty for price, qty in items)
    tax = calculate_vat(net, vat_rate)
    return net, tax, net + tax
''',
    "tax_engine.py": '''"""Low-level tax rate computation."""
def calculate_vat(net_cents, vat_rate):
    # BUG: naive float truncation
    return int(net_cents * vat_rate)
''',
    "tests/test_pricing.py": '''from pricing import calculate_order_total

def test_single_item():
    net, tax, gross = calculate_order_total([(100, 1)], vat_rate=0.20)
    assert net == 100
    assert tax == 20
    assert gross == 120
'''
}

t2001_hidden = {
    "tests/test_pricing_hidden.py": '''import pytest
from pricing import calculate_order_total
from tax_engine import calculate_vat

def test_bankers_rounding_half_cents():
    # 125 * 0.20 = 25.0 -> 25
    # 135 * 0.10 = 13.5 -> 14 (round to even)
    # 145 * 0.10 = 14.5 -> 14 (round to even)
    # 155 * 0.10 = 15.5 -> 16 (round to even)
    assert calculate_order_total([(135, 1)], vat_rate=0.10)[1] == 14
    assert calculate_order_total([(145, 1)], vat_rate=0.10)[1] == 14
    assert calculate_order_total([(155, 1)], vat_rate=0.10)[1] == 16
    assert calculate_order_total([(165, 1)], vat_rate=0.10)[1] == 16

def test_tax_engine_direct():
    assert calculate_vat(135, 0.10) == 14
    assert calculate_vat(145, 0.10) == 14
'''
}

t2001_ref = {
    "tax_engine.py": '''"""Low-level tax rate computation."""
from decimal import Decimal, ROUND_HALF_EVEN

def calculate_vat(net_cents, vat_rate):
    d_net = Decimal(str(net_cents))
    d_rate = Decimal(str(vat_rate))
    return int((d_net * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
'''
}

t2001_m1 = {
    "pricing.py": '''"""Order pricing calculation with itemized taxes."""
from tax_engine import calculate_vat
from decimal import Decimal, ROUND_HALF_EVEN

def calculate_order_total(items, vat_rate=0.20):
    net = sum(price * qty for price, qty in items)
    # Mutant 1: Workaround in pricing.py without fixing tax_engine.py
    tax = int((Decimal(str(net)) * Decimal(str(vat_rate))).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
    return net, tax, net + tax
''',
    "tax_engine.py": '''"""Low-level tax rate computation."""
def calculate_vat(net_cents, vat_rate):
    return int(net_cents * vat_rate)
'''
}

t2001_m2 = {
    "tax_engine.py": '''"""Low-level tax rate computation."""
def calculate_vat(net_cents, vat_rate):
    # Mutant 2: Ceiling rounding
    import math
    return int(math.ceil(net_cents * vat_rate))
'''
}

register_task(
    tid=2001,
    family="money_rounding",
    name="Order Tax Calculation",
    class_tag="STATED",
    issue="Order tax calculation truncates fractional cents instead of using banker's rounding.",
    traceback_text="FAILED tests/test_pricing_hidden.py::test_bankers_rounding_half_cents - in calculate_order_total (pricing.py:11): assert (100, 13, 113) == (100, 14, 114)",
    traceback_files=["pricing.py"],
    repo=t2001_repo,
    hidden=t2001_hidden,
    ref=t2001_ref,
    mutant1=t2001_m1,
    mutant2=t2001_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    handbook_citations=["Rule H02"],
)


# Task 2002: Invoice Discount Proration (TAUGHT)
t2002_repo = {
    "discount.py": '''"""Invoice discount allocation."""
def prorate_discount(line_totals, total_discount_cents):
    """Prorate discount across lines proportionally to their value.
    line_totals: list of integer cents.
    Returns list of discount cents per line.
    Residual rounding cents must adhere to standard company rounding invariants.
    """
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    # BUG: naive truncation leaves unpaid discount
    return [int(t * total_discount_cents / total) for t in line_totals]
''',
    "tests/test_discount.py": '''from discount import prorate_discount

def test_equal_split():
    assert prorate_discount([100, 100], 50) == [25, 25]

def test_proportional_split():
    assert prorate_discount([100, 300], 40) == [10, 30]
'''
}

t2002_hidden = {
    "tests/test_discount_hidden.py": '''from discount import prorate_discount

def test_exact_bankers_rounding_half():
    # Split 15 cents across 100 and 100: each gets 7.5 -> 8 and 7, sum == 15
    res = prorate_discount([100, 100], 15)
    assert sum(res) == 15
    # 3 lines of 100 with discount 10: 3.333 each -> 3, 3, 4 (sum == 10)
    res2 = prorate_discount([100, 100, 100], 10)
    assert sum(res2) == 10
'''
}

t2002_ref = {
    "discount.py": '''"""Invoice discount allocation."""
from decimal import Decimal, ROUND_HALF_EVEN

def prorate_discount(line_totals, total_discount_cents):
    total = sum(line_totals)
    if total == 0:
        return [0] * len(line_totals)
    d_total = Decimal(str(total))
    d_disc = Decimal(str(total_discount_cents))
    allocated = []
    accumulated = 0
    for i, t in enumerate(line_totals):
        if i == len(line_totals) - 1:
            allocated.append(total_discount_cents - accumulated)
        else:
            share = (Decimal(str(t)) * d_disc / d_total).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
            val = int(share)
            allocated.append(val)
            accumulated += val
    return allocated
'''
}

t2002_m1 = {
    "discount.py": '''"""Invoice discount allocation."""
def prorate_discount(line_totals, total_discount_cents):
    # Mutant 1: Does not conserve total discount (no residual absorption)
    total = sum(line_totals)
    if total == 0: return [0] * len(line_totals)
    return [round(t * total_discount_cents / total) for t in line_totals]
'''
}

t2002_m2 = {
    "discount.py": '''"""Invoice discount allocation."""
def prorate_discount(line_totals, total_discount_cents):
    # Mutant 2: Floor allocation
    return [0] * len(line_totals)
'''
}

register_task(
    tid=2002,
    family="money_rounding",
    name="Invoice Discount Proration",
    class_tag="TAUGHT",
    issue="Prorated discount lines do not sum up to total discount and violate company rounding rules.",
    traceback_text="FAILED tests/test_discount_hidden.py::test_exact_bankers_rounding_half - assert 14 == 15",
    traceback_files=["discount.py"],
    repo=t2002_repo,
    hidden=t2002_hidden,
    ref=t2002_ref,
    mutant1=t2002_m1,
    mutant2=t2002_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H02"],
)


# Task 2003: Multi-currency FX Ledger (TAUGHT, HIDDEN ROOT CAUSE)
t2003_repo = {
    "ledger.py": '''"""Multi-currency ledger aggregator."""
from fx_converter import convert_currency

def record_converted_entry(ledger, amount_foreign, fx_rate):
    """Converts foreign amount to base currency cents and records entry."""
    base_cents = convert_currency(amount_foreign, fx_rate)
    ledger.append(base_cents)
    return sum(ledger)
''',
    "fx_converter.py": '''"""Foreign exchange converter."""
def convert_currency(amount, rate):
    # BUG: Float multiplication without banker's rounding
    return int(amount * rate)
''',
    "tests/test_ledger.py": '''from ledger import record_converted_entry

def test_integer_fx():
    ledger = []
    assert record_converted_entry(ledger, 100, 1.0) == 100
'''
}

t2003_hidden = {
    "tests/test_fx_hidden.py": '''from ledger import record_converted_entry
from fx_converter import convert_currency

def test_fx_bankers_rounding():
    # 25.5 -> 26, 24.5 -> 24
    assert record_converted_entry([], 10, 2.55) == 26
    assert record_converted_entry([], 10, 2.45) == 24

def test_fx_converter_direct():
    assert convert_currency(10, 2.55) == 26
    assert convert_currency(10, 2.45) == 24
'''
}

t2003_ref = {
    "fx_converter.py": '''"""Foreign exchange converter."""
from decimal import Decimal, ROUND_HALF_EVEN

def convert_currency(amount, rate):
    d_amt = Decimal(str(amount))
    d_rate = Decimal(str(rate))
    return int((d_amt * d_rate).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
'''
}

t2003_m1 = {
    "ledger.py": '''"""Multi-currency ledger aggregator."""
from fx_converter import convert_currency

def record_converted_entry(ledger, amount_foreign, fx_rate):
    # Mutant 1: Edits ledger.py rather than root cause in fx_converter.py
    base_cents = int(round(amount_foreign * fx_rate))
    ledger.append(base_cents)
    return sum(ledger)
''',
    "fx_converter.py": '''"""Foreign exchange converter."""
def convert_currency(amount, rate):
    return int(amount * rate)
'''
}

t2003_m2 = {
    "fx_converter.py": '''"""Foreign exchange converter."""
def convert_currency(amount, rate):
    # Mutant 2: Floor truncation
    return int(amount * rate)
'''
}

register_task(
    tid=2003,
    family="money_rounding",
    name="Multi-currency FX Ledger",
    class_tag="TAUGHT",
    issue="Ledger FX entries disagree on half-cent boundaries.",
    traceback_text="FAILED tests/test_fx_hidden.py::test_fx_bankers_rounding - in record_converted_entry (ledger.py:5): assert 25 == 26",
    traceback_files=["ledger.py"],
    repo=t2003_repo,
    hidden=t2003_hidden,
    ref=t2003_ref,
    mutant1=t2003_m1,
    mutant2=t2003_m2,
    hidden_root_cause=True,  # Root cause is in fx_converter.py, not ledger.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H02"],
)


# Task 2004: Coupon Rebate Allocation (DISTRACTOR)
t2004_repo = {
    "rebate.py": '''"""Customer rebate allocation."""
def calculate_rebate(gross_amount_cents, pct_rebate):
    """Regulatory requirement: consumer refunds and rebates MUST always round UP
    to the next whole cent (ceiling rule), overriding standard banker's rounding conventions.
    """
    # BUG: used truncation
    return int(gross_amount_cents * pct_rebate)
''',
    "tests/test_rebate.py": '''from rebate import calculate_rebate

def test_whole_cents():
    assert calculate_rebate(100, 0.10) == 10

def test_fractional_cent_rounds_up():
    assert calculate_rebate(105, 0.10) == 11
'''
}

t2004_hidden = {
    "tests/test_rebate_hidden.py": '''from rebate import calculate_rebate

def test_ceiling_rounding():
    # Any fraction must round UP
    assert calculate_rebate(101, 0.10) == 11 # 10.1 -> 11
    assert calculate_rebate(105, 0.10) == 11 # 10.5 -> 11 (Banker's would say 10 or 10.5)
    assert calculate_rebate(109, 0.10) == 11 # 10.9 -> 11
'''
}

t2004_ref = {
    "rebate.py": '''"""Customer rebate allocation."""
import math

def calculate_rebate(gross_amount_cents, pct_rebate):
    """Regulatory requirement: consumer refunds and rebates MUST always round UP
    to the next whole cent (ceiling rule), overriding standard banker's rounding conventions.
    """
    return int(math.ceil(gross_amount_cents * pct_rebate))
'''
}

t2004_m1 = {
    "rebate.py": '''"""Customer rebate allocation."""
from decimal import Decimal, ROUND_HALF_EVEN

def calculate_rebate(gross_amount_cents, pct_rebate):
    # Mutant 1: Blindly applies Handbook Rule H02 (Banker's rounding)
    d_cents = Decimal(str(gross_amount_cents))
    d_pct = Decimal(str(pct_rebate))
    return int((d_cents * d_pct).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
'''
}

t2004_m2 = {
    "rebate.py": '''"""Customer rebate allocation."""
def calculate_rebate(gross_amount_cents, pct_rebate):
    # Mutant 2: Floor truncation
    return int(gross_amount_cents * pct_rebate)
'''
}

register_task(
    tid=2004,
    family="money_rounding",
    name="Coupon Rebate Allocation",
    class_tag="DISTRACTOR",
    issue="Rebates must round up per regulatory mandate, but currently truncate.",
    traceback_text="FAILED tests/test_rebate_hidden.py::test_ceiling_rounding - assert 10 == 11",
    traceback_files=["rebate.py"],
    repo=t2004_repo,
    hidden=t2004_hidden,
    ref=t2004_ref,
    mutant1=t2004_m1,
    mutant2=t2004_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H02 (Distractor: ticket explicitly overrides with ceiling rule)"],
)


# ==============================================================================
# FAMILY 2: config_merge (Tasks 2005 - 2008)
# ==============================================================================

# Task 2005: Hierarchical App Settings (STATED)
t2005_repo = {
    "settings.py": '''"""Application configuration loader."""
def merge_settings(base, override):
    """Merge base settings dict with override dict recursively.
    Sibling keys in nested dicts must be preserved.
    Base and override dicts must not be mutated.
    """
    # BUG: shallow update drops sibling keys
    res = dict(base)
    res.update(override)
    return res
''',
    "tests/test_settings.py": '''from settings import merge_settings

def test_flat():
    assert merge_settings({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

def test_nested_sibling_retention():
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 5433}}
    res = merge_settings(base, override)
    assert res["db"]["host"] == "localhost"
    assert res["db"]["port"] == 5433
'''
}

t2005_hidden = {
    "tests/test_settings_hidden.py": '''from settings import merge_settings

def test_nested_siblings_and_immutability():
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 5433}}
    res = merge_settings(base, override)
    assert res == {"db": {"host": "localhost", "port": 5433}}
    assert base["db"]["port"] == 5432 # immutable
'''
}

t2005_ref = {
    "settings.py": '''"""Application configuration loader."""
import copy

def merge_settings(base, override):
    result = copy.deepcopy(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_settings(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result
'''
}

t2005_m1 = {
    "settings.py": '''"""Application configuration loader."""
def merge_settings(base, override):
    # Mutant 1: Mutates base in place
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            base[k] = merge_settings(base[k], v)
        else:
            base[k] = v
    return base
'''
}

t2005_m2 = {
    "settings.py": '''"""Application configuration loader."""
def merge_settings(base, override):
    # Mutant 2: Shallow copy
    res = dict(base)
    res.update(override)
    return res
'''
}

register_task(
    tid=2005,
    family="config_merge",
    name="Hierarchical App Settings",
    class_tag="STATED",
    issue="merge_settings overwrites entire nested dictionaries, losing sibling configuration parameters.",
    traceback_text="FAILED tests/test_settings_hidden.py::test_nested_siblings_and_immutability - KeyError: 'host'",
    traceback_files=["settings.py"],
    repo=t2005_repo,
    hidden=t2005_hidden,
    ref=t2005_ref,
    mutant1=t2005_m1,
    mutant2=t2005_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H03"],
)


# Task 2006: Plugin Parameter Resolver (TAUGHT, HIDDEN ROOT CAUSE)
t2006_repo = {
    "plugin_manager.py": '''"""Plugin configuration manager."""
from dict_combiner import combine_defaults

def apply_plugin_defaults(defaults, user_opts):
    """Applies user options over plugin defaults according to company immutability invariants.
    """
    return combine_defaults(defaults, user_opts)
''',
    "dict_combiner.py": '''"""Low-level configuration combiner."""
def combine_defaults(defaults, user_opts):
    # BUG: mutates user_opts and shares references
    for k, v in defaults.items():
        if k not in user_opts:
            user_opts[k] = v
    return user_opts
''',
    "tests/test_plugin.py": '''from plugin_manager import apply_plugin_defaults

def test_missing_filled():
    assert apply_plugin_defaults({"retries": 3}, {}) == {"retries": 3}
'''
}

t2006_hidden = {
    "tests/test_plugin_hidden.py": '''from plugin_manager import apply_plugin_defaults
from dict_combiner import combine_defaults

def test_immutability_and_deep_isolation():
    defaults = {"auth": {"type": "bearer", "scopes": ["read"]}}
    user_opts = {"auth": {"type": "oauth"}}
    res = apply_plugin_defaults(defaults, user_opts)
    assert res["auth"]["scopes"] == ["read"]
    res["auth"]["scopes"].append("write")
    assert defaults["auth"]["scopes"] == ["read"] # Defaults not corrupted
    assert "scopes" not in user_opts["auth"] # User opts not mutated

def test_combiner_direct():
    d = {"sub": {"a": [1]}}
    res = combine_defaults(d, {})
    res["sub"]["a"].append(2)
    assert d["sub"]["a"] == [1]
'''
}

t2006_ref = {
    "dict_combiner.py": '''"""Low-level configuration combiner."""
import copy

def combine_defaults(defaults, user_opts):
    result = copy.deepcopy(defaults)
    for k, v in user_opts.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = combine_defaults(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result
'''
}

t2006_m1 = {
    "plugin_manager.py": '''"""Plugin configuration manager."""
from dict_combiner import combine_defaults
import copy

def apply_plugin_defaults(defaults, user_opts):
    # Mutant 1: Workaround in plugin_manager.py without fixing dict_combiner.py
    res = copy.deepcopy(defaults)
    res.update(copy.deepcopy(user_opts))
    return res
''',
    "dict_combiner.py": '''"""Low-level configuration combiner."""
def combine_defaults(defaults, user_opts):
    for k, v in defaults.items():
        if k not in user_opts:
            user_opts[k] = v
    return user_opts
'''
}

t2006_m2 = {
    "dict_combiner.py": '''"""Low-level configuration combiner."""
def combine_defaults(defaults, user_opts):
    # Mutant 2: Mutates defaults in place
    defaults.update(user_opts)
    return defaults
'''
}

register_task(
    tid=2006,
    family="config_merge",
    name="Plugin Parameter Resolver",
    class_tag="TAUGHT",
    issue="Plugin parameter resolution corrupts global default structures due to mutable reference sharing.",
    traceback_text="FAILED tests/test_plugin_hidden.py::test_immutability_and_deep_isolation - in apply_plugin_defaults (plugin_manager.py:6): AssertionError",
    traceback_files=["plugin_manager.py"],
    repo=t2006_repo,
    hidden=t2006_hidden,
    ref=t2006_ref,
    mutant1=t2006_m1,
    mutant2=t2006_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    handbook_citations=["Rule H03"],
)


# Task 2007: Cloud Environment Layering (STATED, HIDDEN ROOT CAUSE)
t2007_repo = {
    "app.py": '''"""Application runner."""
from env_loader import load_env_layers

def init_app(base_cfg, env_name):
    cfg = load_env_layers(base_cfg, env_name)
    return cfg["cluster"]["region"], cfg["cluster"]["nodes"]
''',
    "env_loader.py": '''"""Environment file loader."""
def load_env_layers(base_cfg, env_name):
    # BUG: returns shallow dict replacement
    return {"cluster": {"region": "us-east-1"}}
''',
    "tests/test_app.py": '''from app import init_app

def test_app_init():
    reg, nodes = init_app({"cluster": {"region": "us-east-1", "nodes": 3}}, "prod")
    assert reg == "us-east-1"
'''
}

t2007_hidden = {
    "tests/test_app_hidden.py": '''import pytest
from app import init_app
from env_loader import load_env_layers

def test_app_nodes_preserved():
    reg, nodes = init_app({"cluster": {"region": "us-west-2", "nodes": 5}}, "prod")
    assert reg == "us-east-1"
    assert nodes == 5

def test_env_loader_direct():
    cfg = load_env_layers({"cluster": {"region": "us-west-2", "nodes": 8}}, "prod")
    assert cfg["cluster"]["nodes"] == 8
'''
}

t2007_ref = {
    "env_loader.py": '''"""Environment file loader."""
import copy

def load_env_layers(base_cfg, env_name):
    res = copy.deepcopy(base_cfg)
    if "cluster" not in res:
        res["cluster"] = {}
    res["cluster"]["region"] = "us-east-1"
    return res
'''
}

t2007_m1 = {
    "app.py": '''"""Application runner."""
from env_loader import load_env_layers

def init_app(base_cfg, env_name):
    # Mutant 1: Modifies app.py rather than env_loader.py
    cfg = load_env_layers(base_cfg, env_name)
    nodes = base_cfg.get("cluster", {}).get("nodes", 1)
    return cfg["cluster"]["region"], nodes
''',
    "env_loader.py": '''"""Environment file loader."""
def load_env_layers(base_cfg, env_name):
    return {"cluster": {"region": "us-east-1"}}
'''
}

t2007_m2 = {
    "env_loader.py": '''"""Environment file loader."""
def load_env_layers(base_cfg, env_name):
    # Mutant 2: Hardcoded dummy
    return {"cluster": {"region": "us-east-1", "nodes": 1}}
'''
}

register_task(
    tid=2007,
    family="config_merge",
    name="Cloud Environment Layering",
    class_tag="STATED",
    issue="Layering cloud environments drops node cluster sizing configuration.",
    traceback_text="FAILED tests/test_app_hidden.py::test_app_nodes_preserved - in init_app (app.py:6): KeyError: 'nodes'",
    traceback_files=["app.py"],
    repo=t2007_repo,
    hidden=t2007_hidden,
    ref=t2007_ref,
    mutant1=t2007_m1,
    mutant2=t2007_m2,
    hidden_root_cause=True,  # Bug is in env_loader.py, not app.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H03"],
)


# Task 2008: Audit Policy Config (DISTRACTOR)
t2008_repo = {
    "fast_merge.py": '''"""High-performance audit policy merger."""
def update_policy_in_place(active_policy, updates):
    """Performance-critical security cache: in-place dictionary mutation is EXPLICITLY REQUIRED
    for memory reuse and shared cache synchronization. Do NOT create a copy; callers rely on identity.
    """
    # BUG: returns new dict instead of updating in-place
    res = dict(active_policy)
    res.update(updates)
    return res
''',
    "tests/test_fast_merge.py": '''from fast_merge import update_policy_in_place

def test_basic_merge():
    p = {"role": "guest"}
    assert update_policy_in_place(p, {"role": "admin"})["role"] == "admin"

def test_in_place_identity():
    p = {"role": "guest"}
    res = update_policy_in_place(p, {"role": "admin"})
    assert res is p
'''
}

t2008_hidden = {
    "tests/test_fast_merge_hidden.py": '''from fast_merge import update_policy_in_place

def test_strict_identity_and_mutation():
    p = {"role": "guest", "flags": [1]}
    res = update_policy_in_place(p, {"flags": [1, 2]})
    assert res is p # Caller identity contract
    assert p["flags"] == [1, 2]
'''
}

t2008_ref = {
    "fast_merge.py": '''"""High-performance audit policy merger."""
def update_policy_in_place(active_policy, updates):
    """Performance-critical security cache: in-place dictionary mutation is EXPLICITLY REQUIRED
    for memory reuse and shared cache synchronization. Do NOT create a copy; callers rely on identity.
    """
    active_policy.update(updates)
    return active_policy
'''
}

t2008_m1 = {
    "fast_merge.py": '''"""High-performance audit policy merger."""
import copy

def update_policy_in_place(active_policy, updates):
    # Mutant 1: Blindly applies Handbook Rule H03 (Immutability / deepcopy)
    res = copy.deepcopy(active_policy)
    res.update(updates)
    return res
'''
}

t2008_m2 = {
    "fast_merge.py": '''"""High-performance audit policy merger."""
def update_policy_in_place(active_policy, updates):
    # Mutant 2: No-op
    return active_policy
'''
}

register_task(
    tid=2008,
    family="config_merge",
    name="Audit Policy Config",
    class_tag="DISTRACTOR",
    issue="In-place policy mutation cache returns new dict instance, breaking caller identity contract.",
    traceback_text="FAILED tests/test_fast_merge_hidden.py::test_strict_identity_and_mutation - assert res is p (AssertionError)",
    traceback_files=["fast_merge.py"],
    repo=t2008_repo,
    hidden=t2008_hidden,
    ref=t2008_ref,
    mutant1=t2008_m1,
    mutant2=t2008_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H03 (Distractor: ticket explicitly mandates in-place mutation)"],
)


# ==============================================================================
# FAMILY 3: calendar_recurrence (Tasks 2009 - 2012)
# ==============================================================================

# Task 2009: Monthly Subscription Billed on Month-End (STATED)
t2009_repo = {
    "recurrence.py": '''"""Calendar recurrence schedule calculation."""
import calendar
from datetime import date

def next_monthly_billing_date(start_date, month_increment=1):
    """Calculate next billing date.
    If start_date is on day 29, 30, or 31 and target month has fewer days,
    clamp to the last valid day of target month (e.g. Jan 31 -> Feb 28/29).
    """
    # BUG: naive month replace throws ValueError on day 31
    new_month = start_date.month + month_increment
    new_year = start_date.year + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1
    return date(new_year, new_month, start_date.day)
''',
    "tests/test_recurrence.py": '''from datetime import date
from recurrence import next_monthly_billing_date

def test_mid_month():
    assert next_monthly_billing_date(date(2024, 1, 15)) == date(2024, 2, 15)
'''
}

t2009_hidden = {
    "tests/test_recurrence_hidden.py": '''from datetime import date
from recurrence import next_monthly_billing_date

def test_month_end_clamping():
    assert next_monthly_billing_date(date(2024, 1, 31)) == date(2024, 2, 29) # Leap year
    assert next_monthly_billing_date(date(2023, 1, 31)) == date(2023, 2, 28) # Non-leap year
    assert next_monthly_billing_date(date(2024, 3, 31)) == date(2024, 4, 30)
'''
}

t2009_ref = {
    "recurrence.py": '''"""Calendar recurrence schedule calculation."""
import calendar
from datetime import date

def next_monthly_billing_date(start_date, month_increment=1):
    new_month = start_date.month + month_increment
    new_year = start_date.year + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1
    max_days = calendar.monthrange(new_year, new_month)[1]
    new_day = min(start_date.day, max_days)
    return date(new_year, new_month, new_day)
'''
}

t2009_m1 = {
    "recurrence.py": '''"""Calendar recurrence schedule calculation."""
from datetime import date, timedelta

def next_monthly_billing_date(start_date, month_increment=1):
    # Mutant 1: Naive 30 days addition
    return start_date + timedelta(days=30 * month_increment)
'''
}

t2009_m2 = {
    "recurrence.py": '''"""Calendar recurrence schedule calculation."""
from datetime import date

def next_monthly_billing_date(start_date, month_increment=1):
    # Mutant 2: Always clamp to 28
    new_month = start_date.month + month_increment
    new_year = start_date.year + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1
    return date(new_year, new_month, min(start_date.day, 28))
'''
}

register_task(
    tid=2009,
    family="calendar_recurrence",
    name="Monthly Subscription Month-End",
    class_tag="STATED",
    issue="Billing date generator crashes with ValueError when billing on day 31.",
    traceback_text="FAILED tests/test_recurrence_hidden.py::test_month_end_clamping - ValueError: day is out of range for month",
    traceback_files=["recurrence.py"],
    repo=t2009_repo,
    hidden=t2009_hidden,
    ref=t2009_ref,
    mutant1=t2009_m1,
    mutant2=t2009_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H05"],
)


# Task 2010: Quarterly Compliance Audit Schedule (TAUGHT, HIDDEN ROOT CAUSE)
t2010_repo = {
    "audit_manager.py": '''"""Quarterly compliance audit period matcher."""
from datetime import date
from date_window import is_in_period

def events_in_audit_window(events, start_date, end_date):
    """Filters events within the company reporting period window.
    events: list of (date, event_name).
    Interval bounds follow standard company convention.
    """
    return [name for d, name in events if is_in_period(d, start_date, end_date)]
''',
    "date_window.py": '''"""Date period window evaluator."""
def is_in_period(d, start_date, end_date):
    # BUG: uses closed interval (start <= d <= end)
    return start_date <= d <= end_date
''',
    "tests/test_compliance.py": '''from datetime import date
from audit_manager import events_in_audit_window

def test_events_mid():
    evs = [(date(2024, 2, 1), "audit1")]
    assert events_in_audit_window(evs, date(2024, 1, 1), date(2024, 3, 1)) == ["audit1"]
'''
}

t2010_hidden = {
    "tests/test_compliance_hidden.py": '''from datetime import date
from audit_manager import events_in_audit_window
from date_window import is_in_period

def test_half_open_window():
    # Rule H05: [start, end) includes start, strictly excludes end
    evs = [
        (date(2024, 1, 1), "ev_start"),
        (date(2024, 2, 1), "ev_mid"),
        (date(2024, 3, 1), "ev_end"),
    ]
    res = events_in_audit_window(evs, date(2024, 1, 1), date(2024, 3, 1))
    assert "ev_start" in res
    assert "ev_mid" in res
    assert "ev_end" not in res # Excluded

def test_date_window_direct():
    assert is_in_period(date(2024, 3, 1), date(2024, 1, 1), date(2024, 3, 1)) is False
'''
}

t2010_ref = {
    "date_window.py": '''"""Date period window evaluator."""
def is_in_period(d, start_date, end_date):
    return start_date <= d < end_date
'''
}

t2010_m1 = {
    "audit_manager.py": '''"""Quarterly compliance audit period matcher."""
from datetime import date
from date_window import is_in_period

def events_in_audit_window(events, start_date, end_date):
    # Mutant 1: Workaround in audit_manager.py without fixing date_window.py
    return [name for d, name in events if start_date <= d < end_date]
''',
    "date_window.py": '''"""Date period window evaluator."""
def is_in_period(d, start_date, end_date):
    return start_date <= d <= end_date
'''
}

t2010_m2 = {
    "date_window.py": '''"""Date period window evaluator."""
def is_in_period(d, start_date, end_date):
    # Mutant 2: Open interval (start, end)
    return start_date < d < end_date
'''
}

register_task(
    tid=2010,
    family="calendar_recurrence",
    name="Quarterly Compliance Audit Schedule",
    class_tag="TAUGHT",
    issue="Audit window filters include events occurring on the concluding cutoff boundary.",
    traceback_text="FAILED tests/test_compliance_hidden.py::test_half_open_window - in events_in_audit_window (audit_manager.py:9): AssertionError: assert 'ev_end' not in ['ev_start', 'ev_mid', 'ev_end']",
    traceback_files=["audit_manager.py"],
    repo=t2010_repo,
    hidden=t2010_hidden,
    ref=t2010_ref,
    mutant1=t2010_m1,
    mutant2=t2010_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    handbook_citations=["Rule H05"],
)


# Task 2011: Shift Roster Generator (STATED, VISIBLE-TEST SENSITIVE)
t2011_repo = {
    "roster.py": '''"""Shift roster weekly schedule generator."""
from datetime import date, timedelta

def generate_weekly_shifts(start_date, count=4):
    """Generates weekly shift dates every 7 days.
    Input start_date must not be mutated.
    Returns list of dates.
    """
    # BUG: returns wrong interval (daily instead of weekly)
    return [start_date + timedelta(days=i) for i in range(count)]
''',
    "tests/test_roster.py": '''from datetime import date
from roster import generate_weekly_shifts

def test_visible_weekly():
    # Obvious naive fix of returning [start_date, start_date+7, ...] must preserve list length count
    shifts = generate_weekly_shifts(date(2024, 1, 1), count=3)
    assert len(shifts) == 3
    assert shifts[1] == date(2024, 1, 8)
'''
}

t2011_hidden = {
    "tests/test_roster_hidden.py": '''from datetime import date
from roster import generate_weekly_shifts

def test_multi_month_weekly_shifts():
    shifts = generate_weekly_shifts(date(2024, 1, 15), count=6)
    assert shifts[0] == date(2024, 1, 15)
    assert shifts[1] == date(2024, 1, 22)
    assert shifts[2] == date(2024, 1, 29)
    assert shifts[3] == date(2024, 2, 5)
    assert shifts[4] == date(2024, 2, 12)
    assert shifts[5] == date(2024, 2, 19)
'''
}

t2011_ref = {
    "roster.py": '''"""Shift roster weekly schedule generator."""
from datetime import date, timedelta

def generate_weekly_shifts(start_date, count=4):
    return [start_date + timedelta(days=7 * i) for i in range(count)]
'''
}

t2011_m1 = {
    "roster.py": '''"""Shift roster weekly schedule generator."""
from datetime import date, timedelta

def generate_weekly_shifts(start_date, count=4):
    # Mutant 1: Naive fix fails on count > 4
    return [start_date + timedelta(days=7 * i) for i in range(min(count, 4))]
'''
}

t2011_m2 = {
    "roster.py": '''"""Shift roster weekly schedule generator."""
from datetime import date, timedelta

def generate_weekly_shifts(start_date, count=4):
    # Mutant 2: Daily shifts
    return [start_date + timedelta(days=i) for i in range(count)]
'''
}

register_task(
    tid=2011,
    family="calendar_recurrence",
    name="Shift Roster Generator",
    class_tag="STATED",
    issue="Roster generator outputs consecutive daily shifts rather than weekly intervals.",
    traceback_text="FAILED tests/test_roster.py::test_visible_weekly - assert date(2024, 1, 2) == date(2024, 1, 8)",
    traceback_files=["roster.py"],
    repo=t2011_repo,
    hidden=t2011_hidden,
    ref=t2011_ref,
    mutant1=t2011_m1,
    mutant2=t2011_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H05"],
)


# Task 2012: Billing Period Usage Aggregator (TAUGHT, HIDDEN ROOT CAUSE)
t2012_repo = {
    "usage.py": '''"""Usage metrics aggregator."""
from period_calc import get_period_timestamps

def aggregate_usage_events(events, year, month):
    """Aggregates usage in billing month [start, end)."""
    start_ts, end_ts = get_period_timestamps(year, month)
    return [e for ts, e in events if start_ts <= ts < end_ts]
''',
    "period_calc.py": '''"""Period timestamp converter."""
from datetime import datetime

def get_period_timestamps(year, month):
    # BUG: Calculates end timestamp at day 28 regardless of month
    start_ts = datetime(year, month, 1)
    end_ts = datetime(year, month, 28)
    return start_ts, end_ts
''',
    "tests/test_usage.py": '''from datetime import datetime
from usage import aggregate_usage_events

def test_early_event():
    evs = [(datetime(2024, 1, 10), "login")]
    assert aggregate_usage_events(evs, 2024, 1) == ["login"]
'''
}

t2012_hidden = {
    "tests/test_usage_hidden.py": '''from datetime import datetime
from usage import aggregate_usage_events
from period_calc import get_period_timestamps

def test_month_end_events_included():
    # Events on Jan 29, 30, 31 must be included in Jan period
    evs = [
        (datetime(2024, 1, 29), "ev29"),
        (datetime(2024, 1, 31, 23, 59), "ev31"),
        (datetime(2024, 2, 1, 0, 0), "ev_feb"),
    ]
    res = aggregate_usage_events(evs, 2024, 1)
    assert "ev29" in res
    assert "ev31" in res
    assert "ev_feb" not in res

def test_period_calc_direct():
    start_ts, end_ts = get_period_timestamps(2024, 1)
    assert end_ts == datetime(2024, 2, 1)
'''
}

t2012_ref = {
    "period_calc.py": '''"""Period timestamp converter."""
import calendar
from datetime import datetime, timedelta

def get_period_timestamps(year, month):
    start_ts = datetime(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    end_ts = start_ts + timedelta(days=days_in_month)
    return start_ts, end_ts
'''
}

t2012_m1 = {
    "usage.py": '''"""Usage metrics aggregator."""
from period_calc import get_period_timestamps

def aggregate_usage_events(events, year, month):
    # Mutant 1: Patches usage.py rather than root cause in period_calc.py
    return [e for ts, e in events if ts.month == month and ts.year == year]
''',
    "period_calc.py": '''"""Period timestamp converter."""
from datetime import datetime

def get_period_timestamps(year, month):
    return datetime(year, month, 1), datetime(year, month, 28)
'''
}

t2012_m2 = {
    "period_calc.py": '''"""Period timestamp converter."""
from datetime import datetime

def get_period_timestamps(year, month):
    # Mutant 2: Hardcoded 30 days
    return datetime(year, month, 1), datetime(year, month, 30)
'''
}

register_task(
    tid=2012,
    family="calendar_recurrence",
    name="Billing Period Usage Aggregator",
    class_tag="TAUGHT",
    issue="Monthly usage reports drop events occurring in the final days of the month.",
    traceback_text="FAILED tests/test_usage_hidden.py::test_month_end_events_included - in aggregate_usage_events (usage.py:7): assert 'ev29' in []",
    traceback_files=["usage.py"],
    repo=t2012_repo,
    hidden=t2012_hidden,
    ref=t2012_ref,
    mutant1=t2012_m1,
    mutant2=t2012_m2,
    hidden_root_cause=True,  # Root cause is in period_calc.py, not usage.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H05"],
)


# ==============================================================================
# FAMILY 4: csv_roundtrip (Tasks 2013 - 2016)
# ==============================================================================

# Task 2013: Export User Profile with Commas (STATED)
t2013_repo = {
    "csv_format.py": '''"""RFC 4180 compliant CSV line serializer."""
def serialize_csv_row(fields):
    """Encodes a list of fields into a CSV line without trailing newline.
    If a field contains a comma, double quote, CR, LF, or has leading/trailing spaces,
    enclose it in double quotes. Internal double quotes must be doubled ("").
    """
    # BUG: naive join without quoting
    return ",".join(str(f) for f in fields)
''',
    "tests/test_csv.py": '''from csv_format import serialize_csv_row

def test_simple_row():
    assert serialize_csv_row(["a", "b", "c"]) == "a,b,c"

def test_comma_quoted():
    assert serialize_csv_row(["Smith, John", "admin"]) == '"Smith, John",admin'
'''
}

t2013_hidden = {
    "tests/test_csv_hidden.py": '''from csv_format import serialize_csv_row

def test_quoting_rules():
    assert serialize_csv_row(["Smith, John", "admin"]) == '"Smith, John",admin'
    assert serialize_csv_row(['Say "hello"', "12"]) == '"Say ""hello""",12'
    assert serialize_csv_row(["line1\\nline2", "ok"]) == '"line1\\nline2",ok'
'''
}

t2013_ref = {
    "csv_format.py": '''"""RFC 4180 compliant CSV line serializer."""
def serialize_csv_row(fields):
    out = []
    for f in fields:
        s = str(f) if f is not None else ""
        needs_quote = any(c in s for c in [",", '"', "\\r", "\\n"]) or s.startswith(" ") or s.endswith(" ")
        if needs_quote:
            escaped = s.replace('"', '""')
            out.append(f'"{escaped}"')
        else:
            out.append(s)
    return ",".join(out)
'''
}

t2013_m1 = {
    "csv_format.py": '''"""RFC 4180 compliant CSV line serializer."""
def serialize_csv_row(fields):
    # Mutant 1: Quotes commas but fails to double internal quotes
    out = []
    for f in fields:
        s = str(f)
        if "," in s: out.append(f'"{s}"')
        else: out.append(s)
    return ",".join(out)
'''
}

t2013_m2 = {
    "csv_format.py": '''"""RFC 4180 compliant CSV line serializer."""
def serialize_csv_row(fields):
    # Mutant 2: Always quote everything naively
    return ",".join(f'"{f}"' for f in fields)
'''
}

register_task(
    tid=2013,
    family="csv_roundtrip",
    name="Export User Profile with Commas",
    class_tag="STATED",
    issue="CSV serializer outputs unquoted fields containing commas, corrupting tabular exports.",
    traceback_text="FAILED tests/test_csv_hidden.py::test_quoting_rules - assert 'Smith, John,admin' == '\"Smith, John\",admin'",
    traceback_files=["csv_format.py"],
    repo=t2013_repo,
    hidden=t2013_hidden,
    ref=t2013_ref,
    mutant1=t2013_m1,
    mutant2=t2013_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H10"],
)


# Task 2014: Data Ingestion Pipeline (TAUGHT)
t2014_repo = {
    "csv_reader.py": '''"""Streaming CSV record parser."""
def parse_csv_record(text):
    """Parses a CSV string into a list of field strings.
    Adheres to company RFC 4180 error handling conventions.
    """
    # BUG: naive split, does not validate unterminated quotes
    return text.split(",")
''',
    "tests/test_reader.py": '''from csv_reader import parse_csv_record

def test_basic_parse():
    assert parse_csv_record("a,b,c") == ["a", "b", "c"]
'''
}

t2014_hidden = {
    "tests/test_reader_hidden.py": '''import pytest
from csv_reader import parse_csv_record

def test_unterminated_quote_raises_value_error():
    # Rule H10 & H04: Unterminated quote MUST raise ValueError
    with pytest.raises(ValueError):
        parse_csv_record('a,"unterminated field,c')

def test_escaped_quotes_and_commas():
    assert parse_csv_record('"a,b","c ""d"""') == ["a,b", 'c "d"']
'''
}

t2014_ref = {
    "csv_reader.py": '''"""Streaming CSV record parser."""
import csv
import io

def parse_csv_record(text):
    if text.count('"') % 2 != 0:
        raise ValueError("Unterminated quote in CSV record")
    reader = csv.reader(io.StringIO(text))
    try:
        rows = list(reader)
        return rows[0] if rows else []
    except csv.Error as e:
        raise ValueError(f"CSV parse error: {e}")
'''
}

t2014_m1 = {
    "csv_reader.py": '''"""Streaming CSV record parser."""
def parse_csv_record(text):
    # Mutant 1: Raises generic Exception instead of ValueError
    if text.count('"') % 2 != 0:
        raise Exception("Unterminated quote")
    return text.split(",")
'''
}

t2014_m2 = {
    "csv_reader.py": '''"""Streaming CSV record parser."""
def parse_csv_record(text):
    # Mutant 2: Returns None on unterminated quote
    if text.count('"') % 2 != 0:
        return None
    return text.split(",")
'''
}

register_task(
    tid=2014,
    family="csv_roundtrip",
    name="Data Ingestion Pipeline",
    class_tag="TAUGHT",
    issue="CSV reader silently accepts corrupted records with unterminated quotes without raising ValueError.",
    traceback_text="FAILED tests/test_reader_hidden.py::test_unterminated_quote_raises_value_error - Failed: DID NOT RAISE <class 'ValueError'>",
    traceback_files=["csv_reader.py"],
    repo=t2014_repo,
    hidden=t2014_hidden,
    ref=t2014_ref,
    mutant1=t2014_m1,
    mutant2=t2014_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H10", "Rule H04"],
)


# Task 2015: Audit Log Stream Exporter (STATED, HIDDEN ROOT CAUSE)
t2015_repo = {
    "exporter.py": '''"""Audit event exporter."""
from sanitizer import sanitize_field

def export_audit_row(event_id, message):
    safe_msg = sanitize_field(message)
    return f"{event_id},{safe_msg}"
''',
    "sanitizer.py": '''"""Field sanitizer."""
def sanitize_field(val):
    # BUG: strips quotes rather than escaping them
    return str(val).replace('"', '')
''',
    "tests/test_exporter.py": '''from exporter import export_audit_row

def test_plain():
    assert export_audit_row(1, "normal") == "1,normal"
'''
}

t2015_hidden = {
    "tests/test_exporter_hidden.py": '''from exporter import export_audit_row
from sanitizer import sanitize_field

def test_quote_preservation():
    # Quotes must be doubled and field wrapped
    assert export_audit_row(2, 'Said "halt"') == '2,"Said ""halt"""'

def test_sanitizer_direct():
    assert sanitize_field('Said "halt"') == '"Said ""halt"""'
'''
}

t2015_ref = {
    "sanitizer.py": '''"""Field sanitizer."""
def sanitize_field(val):
    s = str(val)
    if any(c in s for c in [",", '"', "\\n", "\\r"]):
        return f'"{s.replace(chr(34), chr(34)*2)}"'
    return s
'''
}

t2015_m1 = {
    "exporter.py": '''"""Audit event exporter."""
from sanitizer import sanitize_field

def export_audit_row(event_id, message):
    # Mutant 1: Patches exporter.py rather than sanitizer.py
    if '"' in message: message = f'"{message.replace(chr(34), chr(34)*2)}"'
    return f"{event_id},{message}"
''',
    "sanitizer.py": '''"""Field sanitizer."""
def sanitize_field(val):
    return str(val).replace('"', '')
'''
}

t2015_m2 = {
    "sanitizer.py": '''"""Field sanitizer."""
def sanitize_field(val):
    # Mutant 2: Backslash escaping instead of RFC 4180 doubled quotes
    return str(val).replace('"', '\\"')
'''
}

register_task(
    tid=2015,
    family="csv_roundtrip",
    name="Audit Log Stream Exporter",
    class_tag="STATED",
    issue="Audit log exporter strips internal quotation marks, corrupting forensic event payloads.",
    traceback_text="FAILED tests/test_exporter_hidden.py::test_quote_preservation - in export_audit_row (exporter.py:6): assert '2,Said halt' == '2,\"Said \"\"halt\"\"\"'",
    traceback_files=["exporter.py"],
    repo=t2015_repo,
    hidden=t2015_hidden,
    ref=t2015_ref,
    mutant1=t2015_m1,
    mutant2=t2015_m2,
    hidden_root_cause=True,  # Root cause in sanitizer.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H10"],
)


# Task 2016: Tab-Separated TSV Batch Parser (DISTRACTOR)
t2016_repo = {
    "tsv_parser.py": '''"""Tab-separated value batch parser."""
def parse_tsv_line(line):
    """Format specification: This format is raw TSV without quote escaping.
    Literal quotes and commas are treated strictly as plain text characters without quotes.
    Split strictly on '\\t'.
    """
    # BUG: uses comma split
    return line.split(",")
''',
    "tests/test_tsv.py": '''from tsv_parser import parse_tsv_line

def test_single():
    assert parse_tsv_line("abc") == ["abc"]
'''
}

t2016_hidden = {
    "tests/test_tsv_hidden.py": '''from tsv_parser import parse_tsv_line

def test_raw_tsv_quotes():
    # Quotes and commas are literal text, never stripped or parsed as RFC 4180 CSV
    line = '1\\t"quoted"\\ta,b'
    assert parse_tsv_line(line) == ['1', '"quoted"', 'a,b']
'''
}

t2016_ref = {
    "tsv_parser.py": '''"""Tab-separated value batch parser."""
def parse_tsv_line(line):
    """Format specification: This format is raw TSV without quote escaping.
    Literal quotes and commas are treated strictly as plain text characters without quotes.
    Split strictly on '\\t'.
    """
    return line.split("\\t")
'''
}

t2016_m1 = {
    "tsv_parser.py": '''"""Tab-separated value batch parser."""
import csv, io

def parse_tsv_line(line):
    # Mutant 1: Blindly applies Handbook Rule H10 (RFC 4180 CSV escaping)
    reader = csv.reader(io.StringIO(line), delimiter='\\t')
    return list(reader)[0]
'''
}

t2016_m2 = {
    "tsv_parser.py": '''"""Tab-separated value batch parser."""
def parse_tsv_line(line):
    # Mutant 2: Comma split
    return line.split(",")
'''
}

register_task(
    tid=2016,
    family="csv_roundtrip",
    name="Tab-Separated TSV Batch Parser",
    class_tag="DISTRACTOR",
    issue="TSV parser splits on commas instead of tabs, failing on comma-separated values inside tab columns.",
    traceback_text="FAILED tests/test_tsv_hidden.py::test_raw_tsv_quotes - assert ['1\\t\"quoted\"\\ta', 'b'] == ['1', '\"quoted\"', 'a,b']",
    traceback_files=["tsv_parser.py"],
    repo=t2016_repo,
    hidden=t2016_hidden,
    ref=t2016_ref,
    mutant1=t2016_m1,
    mutant2=t2016_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H10 (Distractor: ticket explicitly defines raw TSV parsing)"],
)


# ==============================================================================
# FAMILY 5: permission_prefix (Tasks 2017 - 2020)
# ==============================================================================

# Task 2017: API Endpoint Access Control (STATED)
t2017_repo = {
    "acl.py": '''"""API endpoint permission evaluator."""
def check_permission(rules, path, method):
    """Rules is list of (path_prefix, method, effect) where effect is 'allow' or 'deny'.
    A rule matches if path_prefix is a path-segment prefix of path
    ('/api' matches '/api' and '/api/v1', but NOT '/apiv1').
    Longest matching prefix wins. Default deny.
    """
    # BUG: naive startswith matches substring prefixes like /apiv1
    matching = []
    for prefix, m, effect in rules:
        if path.startswith(prefix) and (m == method or m == "*"):
            matching.append((len(prefix), effect))
    if not matching:
        return False
    matching.sort(key=lambda x: x[0], reverse=True)
    return matching[0][1] == "allow"
''',
    "tests/test_acl.py": '''from acl import check_permission

def test_exact_path():
    rules = [("/api", "GET", "allow")]
    assert check_permission(rules, "/api", "GET") is True

def test_segment_boundary_rejection():
    rules = [("/api", "GET", "allow")]
    assert check_permission(rules, "/apiv2", "GET") is False
'''
}

t2017_hidden = {
    "tests/test_acl_hidden.py": '''from acl import check_permission

def test_segment_boundary():
    rules = [("/api", "GET", "allow")]
    assert check_permission(rules, "/api/users", "GET") is True
    assert check_permission(rules, "/apiv2", "GET") is False # Not a segment prefix!
'''
}

t2017_ref = {
    "acl.py": '''"""API endpoint permission evaluator."""
def _is_segment_prefix(prefix, path):
    p_parts = [p for p in prefix.strip("/").split("/") if p]
    t_parts = [t for t in path.strip("/").split("/") if t]
    if len(p_parts) > len(t_parts):
        return False
    return t_parts[:len(p_parts)] == p_parts

def check_permission(rules, path, method):
    matching = []
    for prefix, m, effect in rules:
        if _is_segment_prefix(prefix, path) and (m == method or m == "*"):
            matching.append((len(prefix), effect))
    if not matching:
        return False
    matching.sort(key=lambda x: x[0], reverse=True)
    return matching[0][1] == "allow"
'''
}

t2017_m1 = {
    "acl.py": '''"""API endpoint permission evaluator."""
def check_permission(rules, path, method):
    # Mutant 1: Still uses startswith
    matching = [eff for pref, m, eff in rules if path.startswith(pref)]
    return "allow" in matching
'''
}

t2017_m2 = {
    "acl.py": '''"""API endpoint permission evaluator."""
def check_permission(rules, path, method):
    # Mutant 2: Always denies
    return False
'''
}

register_task(
    tid=2017,
    family="permission_prefix",
    name="API Endpoint Access Control",
    class_tag="STATED",
    issue="ACL check allows access to unauthorized endpoints due to naive string prefix matching.",
    traceback_text="FAILED tests/test_acl_hidden.py::test_segment_boundary - assert True is False (path '/apiv2' allowed by '/api')",
    traceback_files=["acl.py"],
    repo=t2017_repo,
    hidden=t2017_hidden,
    ref=t2017_ref,
    mutant1=t2017_m1,
    mutant2=t2017_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H06"],
)


# Task 2018: Multi-tenant Document Permission (TAUGHT)
t2018_repo = {
    "doc_perm.py": '''"""Multi-tenant document permission evaluator."""
def is_doc_accessible(rules, doc_path):
    """Evaluates access to doc_path according to company prefix normalization rules.
    rules: list of (prefix, 'allow'|'deny').
    Longest prefix wins. Default deny.
    """
    # BUG: fails when rule prefix has trailing slash (e.g. '/docs/')
    p_clean = doc_path.strip("/")
    matching = []
    for pref, eff in rules:
        # Splits without stripping trailing slash, creating empty segment
        parts = pref.split("/")
        if doc_path.startswith(pref):
            matching.append((len(pref), eff))
    if not matching:
        return False
    matching.sort(key=lambda x: x[0], reverse=True)
    return matching[0][1] == "allow"
''',
    "tests/test_doc_perm.py": '''from doc_perm import is_doc_accessible

def test_simple_doc():
    assert is_doc_accessible([("/docs", "allow")], "/docs/report.pdf") is True
'''
}

t2018_hidden = {
    "tests/test_doc_perm_hidden.py": '''from doc_perm import is_doc_accessible

def test_trailing_slash_normalization():
    # Rule H06: Redundant trailing slashes on rule prefixes must be normalized
    # A rule of "/docs/" must match "/docs" and "/docs/report.pdf", but never "/docsextra/hack.pdf"
    rules = [("/docs/", "allow"), ("/docs/private/", "deny")]
    assert is_doc_accessible(rules, "/docs") is True
    assert is_doc_accessible(rules, "/docs/report.pdf") is True
    assert is_doc_accessible(rules, "/docs/private/salary.pdf") is False
    assert is_doc_accessible(rules, "/docsextra/hack.pdf") is False
'''
}

t2018_ref = {
    "doc_perm.py": '''"""Multi-tenant document permission evaluator."""
def _match(pref, path):
    norm_pref = pref.rstrip("/") if pref != "/" else "/"
    p_parts = [x for x in norm_pref.strip("/").split("/") if x]
    d_parts = [x for x in path.strip("/").split("/") if x]
    if len(p_parts) > len(d_parts):
        return False
    return d_parts[:len(p_parts)] == p_parts

def is_doc_accessible(rules, doc_path):
    matching = []
    for pref, eff in rules:
        if _match(pref, doc_path):
            norm_len = len(pref.rstrip("/"))
            matching.append((norm_len, eff))
    if not matching:
        return False
    matching.sort(key=lambda x: x[0], reverse=True)
    return matching[0][1] == "allow"
'''
}

t2018_m1 = {
    "doc_perm.py": '''"""Multi-tenant document permission evaluator."""
def is_doc_accessible(rules, doc_path):
    # Mutant 1: Naive strip without segment boundary check (matches /docsextra for /docs)
    matching = []
    for pref, eff in rules:
        p = pref.rstrip("/")
        if doc_path.startswith(p):
            matching.append((len(p), eff))
    if not matching: return False
    matching.sort(key=lambda x: x[0], reverse=True)
    return matching[0][1] == "allow"
'''
}

t2018_m2 = {
    "doc_perm.py": '''"""Multi-tenant document permission evaluator."""
def is_doc_accessible(rules, doc_path):
    # Mutant 2: Always returns allow
    return True
'''
}

register_task(
    tid=2018,
    family="permission_prefix",
    name="Multi-tenant Document Permission",
    class_tag="TAUGHT",
    issue="Document ACL ignores rules whose path prefixes contain trailing slashes.",
    traceback_text="FAILED tests/test_doc_perm_hidden.py::test_trailing_slash_normalization - assert False is True (path '/docs/report.pdf' denied by '/docs/')",
    traceback_files=["doc_perm.py"],
    repo=t2018_repo,
    hidden=t2018_hidden,
    ref=t2018_ref,
    mutant1=t2018_m1,
    mutant2=t2018_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H06"],
)


# Task 2019: Admin Group Role Inheritance (STATED, HIDDEN ROOT CAUSE)
t2019_repo = {
    "evaluator.py": '''"""Role permission evaluator."""
from group_resolver import resolve_user_groups

def user_can_admin(user_id, group_graph):
    """Returns True if user belongs to admin group directly or through nested groups."""
    groups = resolve_user_groups(user_id, group_graph)
    return "admin" in groups
''',
    "group_resolver.py": '''"""Group hierarchy resolver."""
def resolve_user_groups(user_id, group_graph):
    # BUG: only checks direct memberships, does not traverse nested groups
    return set(group_graph.get(user_id, []))
''',
    "tests/test_evaluator.py": '''from evaluator import user_can_admin

def test_direct_admin():
    graph = {"alice": ["admin"]}
    assert user_can_admin("alice", graph) is True
'''
}

t2019_hidden = {
    "tests/test_evaluator_hidden.py": '''from evaluator import user_can_admin

def test_nested_admin_inheritance():
    # bob -> dev -> admin
    graph = {
        "bob": ["dev"],
        "dev": ["admin"],
        "alice": ["ops"]
    }
    assert user_can_admin("bob", graph) is True
    assert user_can_admin("alice", graph) is False
'''
}

t2019_ref = {
    "group_resolver.py": '''"""Group hierarchy resolver."""
def resolve_user_groups(user_id, group_graph):
    visited = set()
    stack = list(group_graph.get(user_id, []))
    while stack:
        g = stack.pop()
        if g not in visited:
            visited.add(g)
            stack.extend(group_graph.get(g, []))
    return visited
'''
}

t2019_m1 = {
    "evaluator.py": '''"""Role permission evaluator."""
from group_resolver import resolve_user_groups

def user_can_admin(user_id, group_graph):
    # Mutant 1: Patches evaluator.py instead of root cause in group_resolver.py
    if user_id == "bob": return True
    return False
''',
    "group_resolver.py": '''"""Group hierarchy resolver."""
def resolve_user_groups(user_id, group_graph):
    return set(group_graph.get(user_id, []))
'''
}

t2019_m2 = {
    "group_resolver.py": '''"""Group hierarchy resolver."""
def resolve_user_groups(user_id, group_graph):
    # Mutant 2: Infinite loop on cycle
    return set(group_graph.keys())
'''
}

register_task(
    tid=2019,
    family="permission_prefix",
    name="Admin Group Role Inheritance",
    class_tag="STATED",
    issue="Users in nested groups fail to inherit administrative privileges.",
    traceback_text="FAILED tests/test_evaluator_hidden.py::test_nested_admin_inheritance - in user_can_admin (evaluator.py:7): assert False is True",
    traceback_files=["evaluator.py"],
    repo=t2019_repo,
    hidden=t2019_hidden,
    ref=t2019_ref,
    mutant1=t2019_m1,
    mutant2=t2019_m2,
    hidden_root_cause=True,  # Bug in group_resolver.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H06"],
)


# Task 2020: Wildcard Action Matrix (TAUGHT)
t2020_repo = {
    "action_gate.py": '''"""Action authorization gate."""
def authorize_action(allowed_actions, requested_action):
    """Authorizes requested_action against allowed_actions set.
    If unauthorized, must raise standard company exception type.
    """
    # BUG: returns False instead of raising PermissionError
    if "*" in allowed_actions or requested_action in allowed_actions:
        return True
    return False
''',
    "tests/test_action.py": '''from action_gate import authorize_action

def test_allowed():
    assert authorize_action(["read", "write"], "read") is True
'''
}

t2020_hidden = {
    "tests/test_action_hidden.py": '''import pytest
from action_gate import authorize_action

def test_unauthorized_raises_permission_error():
    # Rule H04: Denied access must raise PermissionError
    with pytest.raises(PermissionError):
        authorize_action(["read"], "delete")
'''
}

t2020_ref = {
    "action_gate.py": '''"""Action authorization gate."""
def authorize_action(allowed_actions, requested_action):
    if "*" in allowed_actions or requested_action in allowed_actions:
        return True
    raise PermissionError(f"Action '{requested_action}' not permitted.")
'''
}

t2020_m1 = {
    "action_gate.py": '''"""Action authorization gate."""
def authorize_action(allowed_actions, requested_action):
    # Mutant 1: Raises ValueError instead of PermissionError
    if "*" in allowed_actions or requested_action in allowed_actions:
        return True
    raise ValueError("Access denied")
'''
}

t2020_m2 = {
    "action_gate.py": '''"""Action authorization gate."""
def authorize_action(allowed_actions, requested_action):
    # Mutant 2: Returns False
    return False
'''
}

register_task(
    tid=2020,
    family="permission_prefix",
    name="Wildcard Action Matrix",
    class_tag="TAUGHT",
    issue="Action authorization gate returns boolean False instead of raising PermissionError on violation.",
    traceback_text="FAILED tests/test_action_hidden.py::test_unauthorized_raises_permission_error - Failed: DID NOT RAISE <class 'PermissionError'>",
    traceback_files=["action_gate.py"],
    repo=t2020_repo,
    hidden=t2020_hidden,
    ref=t2020_ref,
    mutant1=t2020_m1,
    mutant2=t2020_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H04"],
)


# ==============================================================================
# FAMILY 6: event_ordering (Tasks 2021 - 2024)
# ==============================================================================

# Task 2021: Async Job Priority Dispatcher (STATED)
t2021_repo = {
    "dispatcher.py": '''"""Priority job dispatcher."""
def schedule_jobs(jobs):
    """Sorts jobs by priority descending (higher number = higher priority).
    Ties in priority must be broken deterministically by unique task ID in ascending order.
    jobs: list of dicts with 'id', 'priority'.
    """
    # BUG: ties in priority broken by id descending
    return sorted(jobs, key=lambda j: (j["priority"], j["id"]), reverse=True)
''',
    "tests/test_dispatch.py": '''from dispatcher import schedule_jobs

def test_distinct_priorities():
    jobs = [{"id": 1, "priority": 10}, {"id": 2, "priority": 20}]
    assert [j["id"] for j in schedule_jobs(jobs)] == [2, 1]
'''
}

t2021_hidden = {
    "tests/test_dispatch_hidden.py": '''from dispatcher import schedule_jobs

def test_deterministic_tie_breaking():
    # Priority ties must be broken deterministically by ascending job id (Rule H07)
    jobs = [
        {"id": 102, "priority": 5},
        {"id": 101, "priority": 5},
        {"id": 103, "priority": 10},
    ]
    res = [j["id"] for j in schedule_jobs(jobs)]
    assert res == [103, 101, 102]
'''
}

t2021_ref = {
    "dispatcher.py": '''"""Priority job dispatcher."""
def schedule_jobs(jobs):
    return sorted(jobs, key=lambda j: (-j["priority"], j["id"]))
'''
}

t2021_m1 = {
    "dispatcher.py": '''"""Priority job dispatcher."""
def schedule_jobs(jobs):
    # Mutant 1: Sorts only by priority, preserving arrival order (not ascending id)
    return sorted(jobs, key=lambda j: j["priority"], reverse=True)
'''
}

t2021_m2 = {
    "dispatcher.py": '''"""Priority job dispatcher."""
def schedule_jobs(jobs):
    # Mutant 2: Breaks ties in priority by ID descending instead of ascending
    return sorted(jobs, key=lambda j: (-j["priority"], -j["id"]))
'''
}

register_task(
    tid=2021,
    family="event_ordering",
    name="Async Job Priority Dispatcher",
    class_tag="STATED",
    issue="Job dispatcher breaks priority ties arbitrarily, violating FIFO sequence.",
    traceback_text="FAILED tests/test_dispatch_hidden.py::test_deterministic_tie_breaking - assert [103, 102, 101] == [103, 101, 102]",
    traceback_files=["dispatcher.py"],
    repo=t2021_repo,
    hidden=t2021_hidden,
    ref=t2021_ref,
    mutant1=t2021_m1,
    mutant2=t2021_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H07"],
)


# Task 2022: Webhook Event Bus (TAUGHT)
t2022_repo = {
    "bus.py": '''"""In-process event bus."""
class EventBus:
    def __init__(self):
        self.listeners = []

    def subscribe(self, callback):
        self.listeners.append(callback)

    def unsubscribe(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def emit(self, event):
        """Dispatches event to listeners according to company reentrancy invariants."""
        # BUG: direct iteration over self.listeners crashes if listener unsubscribes
        for l in self.listeners:
            l(event)
''',
    "tests/test_bus.py": '''from bus import EventBus

def test_basic_emit():
    bus = EventBus()
    out = []
    bus.subscribe(lambda e: out.append(e))
    bus.emit("ping")
    assert out == ["ping"]

def test_listener_mutation_during_dispatch():
    bus = EventBus()
    calls = []
    def unhook(e):
        calls.append("first")
        bus.unsubscribe(unhook)
    bus.subscribe(unhook)
    bus.subscribe(lambda e: calls.append("second"))
    bus.emit("go")
    assert calls == ["first", "second"]
'''
}

t2022_hidden = {
    "tests/test_bus_hidden.py": '''from bus import EventBus

def test_reentrant_unsubscribe():
    # Rule H08: Listener unregistering itself during emit must not crash or skip
    bus = EventBus()
    log = []
    def one_shot(e):
        log.append(f"one_{e}")
        bus.unsubscribe(one_shot)
    def persistent(e):
        log.append(f"per_{e}")

    bus.subscribe(one_shot)
    bus.subscribe(persistent)
    bus.emit("msg1")
    assert log == ["one_msg1", "per_msg1"]
    bus.emit("msg2")
    assert log == ["one_msg1", "per_msg1", "per_msg2"]
'''
}

t2022_ref = {
    "bus.py": '''"""In-process event bus."""
class EventBus:
    def __init__(self):
        self.listeners = []

    def subscribe(self, callback):
        self.listeners.append(callback)

    def unsubscribe(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def emit(self, event):
        for l in list(self.listeners):
            l(event)
'''
}

t2022_m1 = {
    "bus.py": '''"""In-process event bus."""
class EventBus:
    def __init__(self):
        self.listeners = []
    def subscribe(self, callback): self.listeners.append(callback)
    def unsubscribe(self, callback): pass
    def emit(self, event):
        # Mutant 1: Unsubscribe is a no-op
        for l in list(self.listeners): l(event)
'''
}

t2022_m2 = {
    "bus.py": '''"""In-process event bus."""
class EventBus:
    def __init__(self):
        self.listeners = []
    def subscribe(self, callback): self.listeners.append(callback)
    def unsubscribe(self, callback): self.listeners.clear()
    def emit(self, event): pass
'''
}

register_task(
    tid=2022,
    family="event_ordering",
    name="Webhook Event Bus",
    class_tag="TAUGHT",
    issue="Event bus emits crash or skip listeners when a subscriber unregisters inside a callback.",
    traceback_text="FAILED tests/test_bus_hidden.py::test_reentrant_unsubscribe - assert ['one_msg1'] == ['one_msg1', 'per_msg1']",
    traceback_files=["bus.py"],
    repo=t2022_repo,
    hidden=t2022_hidden,
    ref=t2022_ref,
    mutant1=t2022_m1,
    mutant2=t2022_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H08"],
)


# Task 2023: Task Scheduler with Preemption (STATED, VISIBLE-TEST SENSITIVE)
t2023_repo = {
    "scheduler.py": '''"""Preemptive task scheduler."""
class Scheduler:
    def __init__(self):
        self.queue = []

    def add_task(self, task_id, priority):
        self.queue.append((priority, task_id))

    def next_task(self):
        # BUG: pop(0) without sorting
        if not self.queue:
            return None
        return self.queue.pop(0)[1]
''',
    "tests/test_scheduler.py": '''from scheduler import Scheduler

def test_order_visible():
    s = Scheduler()
    s.add_task("low", 1)
    s.add_task("high", 10)
    # Naive fix of sorting descending must pop highest first
    assert s.next_task() == "high"
    assert s.next_task() == "low"
'''
}

t2023_hidden = {
    "tests/test_scheduler_hidden.py": '''from scheduler import Scheduler

def test_dynamic_add_during_execution():
    s = Scheduler()
    s.add_task("t1", 5)
    s.add_task("t2", 10)
    assert s.next_task() == "t2"
    s.add_task("t3", 15) # Preempts t1
    assert s.next_task() == "t3"
    assert s.next_task() == "t1"
'''
}

t2023_ref = {
    "scheduler.py": '''"""Preemptive task scheduler."""
class Scheduler:
    def __init__(self):
        self.queue = []

    def add_task(self, task_id, priority):
        self.queue.append((priority, task_id))

    def next_task(self):
        if not self.queue:
            return None
        self.queue.sort(key=lambda x: x[0], reverse=True)
        return self.queue.pop(0)[1]
'''
}

t2023_m1 = {
    "scheduler.py": '''"""Preemptive task scheduler."""
class Scheduler:
    def __init__(self):
        self.queue = []
    def add_task(self, task_id, priority): self.queue.append((priority, task_id))
    def next_task(self):
        # Mutant 1: Sorts ascending (lowest first)
        if not self.queue: return None
        self.queue.sort(key=lambda x: x[0])
        return self.queue.pop(0)[1]
'''
}

t2023_m2 = {
    "scheduler.py": '''"""Preemptive task scheduler."""
class Scheduler:
    def __init__(self): pass
    def add_task(self, task_id, priority): pass
    def next_task(self): return None
'''
}

register_task(
    tid=2023,
    family="event_ordering",
    name="Task Scheduler with Preemption",
    class_tag="STATED",
    issue="Task scheduler fails to prioritize higher priority tasks added dynamically.",
    traceback_text="FAILED tests/test_scheduler.py::test_order_visible - assert 'low' == 'high'",
    traceback_files=["scheduler.py"],
    repo=t2023_repo,
    hidden=t2023_hidden,
    ref=t2023_ref,
    mutant1=t2023_m1,
    mutant2=t2023_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H07"],
)


# Task 2024: Telemetry Metric Collector (TAUGHT, HIDDEN ROOT CAUSE)
t2024_repo = {
    "collector.py": '''"""Telemetry metric collector."""
from queue_engine import PriorityBuffer

def drain_telemetry_batch(buffer_instance):
    """Drains top telemetry items from buffer in deterministic sequence."""
    return buffer_instance.drain()
''',
    "queue_engine.py": '''"""Underlying buffer queue."""
class PriorityBuffer:
    def __init__(self):
        self.items = []

    def push(self, name, severity):
        self.items.append((severity, name))

    def drain(self):
        # BUG: unsorted drain
        res = [name for s, name in self.items]
        self.items.clear()
        return res
''',
    "tests/test_collector.py": '''from collector import drain_telemetry_batch
from queue_engine import PriorityBuffer

def test_collector():
    buf = PriorityBuffer()
    buf.push("ping", 1)
    assert drain_telemetry_batch(buf) == ["ping"]
'''
}

t2024_hidden = {
    "tests/test_collector_hidden.py": '''from collector import drain_telemetry_batch
from queue_engine import PriorityBuffer

def test_deterministic_severity_drain():
    # Rule H07: Highest severity first, ties preserve insertion sequence
    buf = PriorityBuffer()
    buf.push("warn1", 2)
    buf.push("crit", 5)
    buf.push("warn2", 2)
    assert drain_telemetry_batch(buf) == ["crit", "warn1", "warn2"]
'''
}

t2024_ref = {
    "queue_engine.py": '''"""Underlying buffer queue."""
class PriorityBuffer:
    def __init__(self):
        self.items = []

    def push(self, name, severity):
        self.items.append((severity, len(self.items), name))

    def drain(self):
        self.items.sort(key=lambda x: (-x[0], x[1]))
        res = [name for s, idx, name in self.items]
        self.items.clear()
        return res
'''
}

t2024_m1 = {
    "collector.py": '''"""Telemetry metric collector."""
def drain_telemetry_batch(buffer_instance):
    # Mutant 1: Edits collector.py rather than root cause in queue_engine.py
    res = buffer_instance.drain()
    return list(reversed(res))
''',
    "queue_engine.py": '''"""Underlying buffer queue."""
class PriorityBuffer:
    def __init__(self): self.items = []
    def push(self, name, severity): self.items.append((severity, name))
    def drain(self):
        res = [name for s, name in self.items]
        self.items.clear()
        return res
'''
}

t2024_m2 = {
    "queue_engine.py": '''"""Underlying buffer queue."""
class PriorityBuffer:
    def __init__(self): self.items = []
    def push(self, name, severity): pass
    def drain(self): return []
'''
}

register_task(
    tid=2024,
    family="event_ordering",
    name="Telemetry Metric Collector",
    class_tag="TAUGHT",
    issue="Telemetry buffer emits metrics in arbitrary insertion order regardless of severity level.",
    traceback_text="FAILED tests/test_collector_hidden.py::test_deterministic_severity_drain - in drain (queue_engine.py:12): assert ['warn1', 'crit', 'warn2'] == ['crit', 'warn1', 'warn2']",
    traceback_files=["collector.py"],
    repo=t2024_repo,
    hidden=t2024_hidden,
    ref=t2024_ref,
    mutant1=t2024_m1,
    mutant2=t2024_m2,
    hidden_root_cause=True,  # Root cause in queue_engine.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H07"],
)


# ==============================================================================
# FAMILY 7: cache_ttl (Tasks 2025 - 2028) -- TRANSFER FAMILY
# ==============================================================================

# Task 2025: In-Memory Key-Value Store with TTL (TRANSFER)
t2025_repo = {
    "ttl_cache.py": '''"""In-memory key-value cache with TTL."""
import time

class TTLCache:
    def __init__(self, default_ttl_sec=60, clock=None):
        self.ttl = default_ttl_sec
        self.clock = clock or time.monotonic
        self.store = {}

    def set(self, key, value):
        # BUG: does not record creation timestamp
        self.store[key] = value

    def get(self, key):
        # BUG: never expires entries
        return self.store.get(key)
''',
    "tests/test_ttl_cache.py": '''from ttl_cache import TTLCache

def test_cache_set_get():
    c = TTLCache()
    c.set("k1", "v1")
    assert c.get("k1") == "v1"
'''
}

t2025_hidden = {
    "tests/test_ttl_hidden.py": '''from ttl_cache import TTLCache

def test_expiry_with_injectable_clock():
    now = [1000.0]
    fake_clock = lambda: now[0]
    c = TTLCache(default_ttl_sec=10, clock=fake_clock)
    c.set("session", "active")
    assert c.get("session") == "active"
    
    # Advance clock past TTL
    now[0] = 1011.0
    assert c.get("session") is None
'''
}

t2025_ref = {
    "ttl_cache.py": '''"""In-memory key-value cache with TTL."""
import time

class TTLCache:
    def __init__(self, default_ttl_sec=60, clock=None):
        self.ttl = default_ttl_sec
        self.clock = clock or time.monotonic
        self.store = {}

    def set(self, key, value):
        now = self.clock()
        self.store[key] = (value, now + self.ttl)

    def get(self, key):
        if key not in self.store:
            return None
        val, expiry = self.store[key]
        if self.clock() >= expiry:
            del self.store[key]
            return None
        return val
'''
}

t2025_m1 = {
    "ttl_cache.py": '''"""In-memory key-value cache with TTL."""
import time

class TTLCache:
    def __init__(self, default_ttl_sec=60, clock=None):
        # Mutant 1: Hardcodes time.monotonic, ignores clock parameter
        self.store = {}
    def set(self, key, value): self.store[key] = value
    def get(self, key): return self.store.get(key)
'''
}

t2025_m2 = {
    "ttl_cache.py": '''"""In-memory key-value cache with TTL."""
class TTLCache:
    def __init__(self, default_ttl_sec=60, clock=None): pass
    def set(self, key, value): pass
    def get(self, key): return None
'''
}

register_task(
    tid=2025,
    family="cache_ttl",
    name="In-Memory Key-Value Store with TTL",
    class_tag="TRANSFER",
    issue="TTLCache retains expired entries indefinitely and fails to support injectable clocks.",
    traceback_text="FAILED tests/test_ttl_hidden.py::test_expiry_with_injectable_clock - assert 'active' is None",
    traceback_files=["ttl_cache.py"],
    repo=t2025_repo,
    hidden=t2025_hidden,
    ref=t2025_ref,
    mutant1=t2025_m1,
    mutant2=t2025_m2,
    hidden_root_cause=False,
    visible_test_sensitive=False,
    handbook_citations=["Rule H09"],
)


# Task 2026: Session Token Cache (TRANSFER, HIDDEN ROOT CAUSE)
t2026_repo = {
    "session_store.py": '''"""User session token store."""
import time
from session_validator import validate_session_expiry

class SessionStore:
    def __init__(self, clock=None):
        self.clock = clock or time.monotonic
        self.sessions = {}

    def save_session(self, token, user_id, ttl_seconds=300):
        self.sessions[token] = (user_id, self.clock() + ttl_seconds)

    def get_user(self, token):
        """Retrieves user_id.
        If token is expired or absent, must raise KeyError per company standards.
        """
        if token not in self.sessions:
            raise KeyError(f"Session token '{token}' not found.")
        user_id, exp = self.sessions[token]
        validate_session_expiry(token, exp, self.clock())
        return user_id
''',
    "session_validator.py": '''"""Session expiration validator."""
def validate_session_expiry(token, exp_time, current_time):
    # BUG: returns False instead of raising KeyError
    if current_time >= exp_time:
        return False
    return True
''',
    "tests/test_session.py": '''from session_store import SessionStore

def test_valid_session():
    s = SessionStore()
    s.save_session("tok123", "user_1")
    assert s.get_user("tok123") == "user_1"
'''
}

t2026_hidden = {
    "tests/test_session_hidden.py": '''import pytest
from session_store import SessionStore
from session_validator import validate_session_expiry

def test_expired_session_raises_key_error():
    # Rule H04: Missing or expired key must raise KeyError
    now = [500.0]
    s = SessionStore(clock=lambda: now[0])
    s.save_session("tok", "user_abc", ttl_seconds=60)
    now[0] = 600.0 # Expired
    with pytest.raises(KeyError):
        s.get_user("tok")

def test_validator_direct():
    with pytest.raises(KeyError):
        validate_session_expiry("tok", 500.0, 600.0)
'''
}

t2026_ref = {
    "session_validator.py": '''"""Session expiration validator."""
def validate_session_expiry(token, exp_time, current_time):
    if current_time >= exp_time:
        raise KeyError(f"Session token '{token}' has expired.")
    return True
'''
}

t2026_m1 = {
    "session_store.py": '''"""User session token store."""
import time
from session_validator import validate_session_expiry

class SessionStore:
    def __init__(self, clock=None):
        self.clock = clock or time.monotonic
        self.sessions = {}

    def save_session(self, token, user_id, ttl_seconds=300):
        self.sessions[token] = (user_id, self.clock() + ttl_seconds)

    def get_user(self, token):
        # Mutant 1: Workaround in session_store.py without fixing session_validator.py
        if token not in self.sessions:
            raise KeyError(token)
        user_id, exp = self.sessions[token]
        if self.clock() >= exp:
            raise KeyError(f"Session token '{token}' has expired.")
        return user_id
''',
    "session_validator.py": '''"""Session expiration validator."""
def validate_session_expiry(token, exp_time, current_time):
    if current_time >= exp_time:
        return False
    return True
'''
}

t2026_m2 = {
    "session_validator.py": '''"""Session expiration validator."""
def validate_session_expiry(token, exp_time, current_time):
    # Mutant 2: Always returns True
    return True
'''
}

register_task(
    tid=2026,
    family="cache_ttl",
    name="Session Token Cache",
    class_tag="TRANSFER",
    issue="Session validator fails to raise KeyError when inspecting expired user sessions.",
    traceback_text="FAILED tests/test_session_hidden.py::test_expired_session_raises_key_error - in get_user (session_store.py:17): Failed: DID NOT RAISE <class 'KeyError'>",
    traceback_files=["session_store.py"],
    repo=t2026_repo,
    hidden=t2026_hidden,
    ref=t2026_ref,
    mutant1=t2026_m1,
    mutant2=t2026_m2,
    hidden_root_cause=True,
    visible_test_sensitive=False,
    handbook_citations=["Rule H04", "Rule H09"],
)


# Task 2027: Rate Limiting Sliding Window Cache (TRANSFER, HIDDEN ROOT CAUSE)
t2027_repo = {
    "rate_limiter.py": '''"""API rate limiter."""
from time_window import WindowTracker

class RateLimiter:
    def __init__(self, limit=5, window_sec=60, clock=None):
        self.tracker = WindowTracker(limit, window_sec, clock=clock)

    def is_allowed(self, client_id):
        return self.tracker.record_request(client_id)
''',
    "time_window.py": '''"""Sliding window request tracker."""
import time

class WindowTracker:
    def __init__(self, limit, window_sec, clock=None):
        self.limit = limit
        self.window_sec = window_sec
        self.clock = clock or time.monotonic
        self.history = {}

    def record_request(self, client_id):
        # BUG: Appends without pruning timestamps older than (now - window_sec)
        now = self.clock()
        reqs = self.history.setdefault(client_id, [])
        if len(reqs) >= self.limit:
            return False
        reqs.append(now)
        return True
''',
    "tests/test_limiter.py": '''from rate_limiter import RateLimiter

def test_initial_allow():
    limiter = RateLimiter(limit=2)
    assert limiter.is_allowed("c1") is True
'''
}

t2027_hidden = {
    "tests/test_limiter_hidden.py": '''from rate_limiter import RateLimiter

def test_sliding_window_pruning():
    now = [100.0]
    limiter = RateLimiter(limit=2, window_sec=10, clock=lambda: now[0])
    assert limiter.is_allowed("c1") is True
    assert limiter.is_allowed("c1") is True
    assert limiter.is_allowed("c1") is False # Limit reached
    
    # Advance clock past window
    now[0] = 115.0
    assert limiter.is_allowed("c1") is True # Should be allowed again
'''
}

t2027_ref = {
    "time_window.py": '''"""Sliding window request tracker."""
import time

class WindowTracker:
    def __init__(self, limit, window_sec, clock=None):
        self.limit = limit
        self.window_sec = window_sec
        self.clock = clock or time.monotonic
        self.history = {}

    def record_request(self, client_id):
        now = self.clock()
        reqs = self.history.setdefault(client_id, [])
        # Prune expired timestamps
        cutoff = now - self.window_sec
        self.history[client_id] = [t for t in reqs if t > cutoff]
        reqs = self.history[client_id]
        if len(reqs) >= self.limit:
            return False
        reqs.append(now)
        return True
'''
}

t2027_m1 = {
    "rate_limiter.py": '''"""API rate limiter."""
from time_window import WindowTracker

class RateLimiter:
    def __init__(self, limit=5, window_sec=60, clock=None):
        # Mutant 1: Patches rate_limiter.py instead of root cause in time_window.py
        self.tracker = WindowTracker(limit, window_sec, clock=clock)
    def is_allowed(self, client_id):
        return True
''',
    "time_window.py": '''"""Sliding window request tracker."""
import time
class WindowTracker:
    def __init__(self, limit, window_sec, clock=None): self.history = {}
    def record_request(self, client_id): return False
'''
}

t2027_m2 = {
    "time_window.py": '''"""Sliding window request tracker."""
class WindowTracker:
    def __init__(self, limit, window_sec, clock=None): pass
    def record_request(self, client_id):
        # Mutant 2: Always False
        return False
'''
}

register_task(
    tid=2027,
    family="cache_ttl",
    name="Rate Limiting Sliding Window Cache",
    class_tag="TRANSFER",
    issue="RateLimiter fails to prune expired timestamps from sliding window, blocking clients permanently.",
    traceback_text="FAILED tests/test_limiter_hidden.py::test_sliding_window_pruning - in is_allowed (rate_limiter.py:9): assert False is True",
    traceback_files=["rate_limiter.py"],
    repo=t2027_repo,
    hidden=t2027_hidden,
    ref=t2027_ref,
    mutant1=t2027_m1,
    mutant2=t2027_m2,
    hidden_root_cause=True,  # Root cause in time_window.py
    visible_test_sensitive=False,
    handbook_citations=["Rule H09"],
)


# Task 2028: Tiered Multi-level Cache (TRANSFER, VISIBLE-TEST SENSITIVE)
t2028_repo = {
    "tiered_cache.py": '''"""Multi-tier cache coordinator."""
class TieredCache:
    def __init__(self, l1_cache, l2_cache):
        self.l1 = l1_cache
        self.l2 = l2_cache

    def get(self, key):
        # BUG: returns None without checking l2 fallback
        val = self.l1.get(key)
        return val

    def set(self, key, value):
        self.l1.set(key, value)
        self.l2.set(key, value)
''',
    "tests/test_tiered.py": '''from tiered_cache import TieredCache

class MockCache:
    def __init__(self): self.d = {}
    def get(self, k): return self.d.get(k)
    def set(self, k, v): self.d[k] = v

def test_l2_fallback_visible():
    l1 = MockCache()
    l2 = MockCache()
    l2.set("k2", "v2")
    c = TieredCache(l1, l2)
    # Visible test checks that missing L1 falls back to L2
    assert c.get("k2") == "v2"
'''
}

t2028_hidden = {
    "tests/test_tiered_hidden.py": '''from tiered_cache import TieredCache

class MockCache:
    def __init__(self): self.d = {}
    def get(self, k): return self.d.get(k)
    def set(self, k, v): self.d[k] = v

def test_promote_l2_to_l1_on_miss():
    l1 = MockCache()
    l2 = MockCache()
    l2.set("shared", "data")
    c = TieredCache(l1, l2)
    assert c.get("shared") == "data"
    # Promotion check: L1 must now contain the entry
    assert l1.get("shared") == "data"
'''
}

t2028_ref = {
    "tiered_cache.py": '''"""Multi-tier cache coordinator."""
class TieredCache:
    def __init__(self, l1_cache, l2_cache):
        self.l1 = l1_cache
        self.l2 = l2_cache

    def get(self, key):
        val = self.l1.get(key)
        if val is not None:
            return val
        val = self.l2.get(key)
        if val is not None:
            self.l1.set(key, val)
        return val

    def set(self, key, value):
        self.l1.set(key, value)
        self.l2.set(key, value)
'''
}

t2028_m1 = {
    "tiered_cache.py": '''"""Multi-tier cache coordinator."""
class TieredCache:
    def __init__(self, l1_cache, l2_cache):
        self.l1 = l1_cache
        self.l2 = l2_cache
    def get(self, key):
        # Mutant 1: Reads from L2 on miss but fails to populate L1 (no promotion)
        val = self.l1.get(key)
        if val is not None: return val
        return self.l2.get(key)
    def set(self, key, value):
        self.l1.set(key, value)
        self.l2.set(key, value)
'''
}

t2028_m2 = {
    "tiered_cache.py": '''"""Multi-tier cache coordinator."""
class TieredCache:
    def __init__(self, l1_cache, l2_cache): pass
    def get(self, key): return None
    def set(self, key, value): pass
'''
}

register_task(
    tid=2028,
    family="cache_ttl",
    name="Tiered Multi-level Cache",
    class_tag="TRANSFER",
    issue="TieredCache fails to query L2 fallback store on L1 cache miss.",
    traceback_text="FAILED tests/test_tiered.py::test_l2_fallback_visible - assert None == 'v2'",
    traceback_files=["tiered_cache.py"],
    repo=t2028_repo,
    hidden=t2028_hidden,
    ref=t2028_ref,
    mutant1=t2028_m1,
    mutant2=t2028_m2,
    hidden_root_cause=False,
    visible_test_sensitive=True,
    handbook_citations=["Rule H09"],
)
