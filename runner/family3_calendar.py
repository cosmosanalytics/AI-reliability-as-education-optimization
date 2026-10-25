"""Family 3: calendar_recurrence (Tasks 2009 - 2012).

Governing Rule: Rule H05 (Half-open intervals [start, end): start inclusive, end exclusive).
Competing Alternatives: Fully closed [start, end] inclusive, 1-based indexing.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_3(add_task):
    # =========================================================================
    # Task 2009: Billing Period Interval Calculator (STATED, HRC=False, VTS=False)
    # =========================================================================
    t2009_repo = {
        "calendar_models.py": '''"""Models for billing period dates."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

@dataclass
class BillingWindow:
    start_dt: datetime
    end_dt: datetime
    account_id: str = "ACC-DEFAULT"
    cycle_name: str = "monthly"

    def duration(self) -> timedelta:
        return self.end_dt - self.start_dt

    def total_seconds(self) -> float:
        return self.duration().total_seconds()

    def to_iso(self) -> Dict[str, str]:
        return {
            "start": self.start_dt.isoformat(),
            "end": self.end_dt.isoformat(),
            "cycle": self.cycle_name,
        }
''',
        "formatters.py": '''"""Date interval formatters."""
from datetime import datetime

def format_window_label(start_dt: datetime, end_dt: datetime) -> str:
    return f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"

def format_short_month(dt: datetime) -> str:
    return dt.strftime("%b %Y")
''',
        "intervals.py": '''"""Billing period interval membership checker."""
from datetime import datetime
from calendar_models import BillingWindow
from formatters import format_window_label

def is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:
    """Check if target timestamp falls within the billing window.
    Interval convention: half-open interval [start, end), where start is inclusive and end is exclusive.
    """
    return window.start_dt <= target_dt <= window.end_dt

def filter_billing_events(window: BillingWindow, timestamps: list) -> list:
    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]

def get_window_summary(window: BillingWindow) -> str:
    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"
''',
        "tests/test_intervals.py": '''from datetime import datetime
from calendar_models import BillingWindow
from intervals import is_timestamp_in_billing_period

def test_strictly_inside():
    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))
    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 15)) is True
    assert is_timestamp_in_billing_period(w, datetime(2026, 2, 15)) is False

def test_start_inclusive():
    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))
    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1)) is True
'''
    }

    t2009_hidden = {
        "tests/test_intervals_cases.py": '''from datetime import datetime
from calendar_models import BillingWindow
from intervals import is_timestamp_in_billing_period

def test_interval_end_boundary():
    w = BillingWindow(datetime(2026, 1, 1), datetime(2026, 2, 1))
    assert is_timestamp_in_billing_period(w, datetime(2026, 2, 1)) is False

def test_interval_subsecond_boundary():
    w = BillingWindow(datetime(2026, 1, 1, 0, 0, 0), datetime(2026, 1, 1, 1, 0, 0))
    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1, 0, 59, 59, 999999)) is True
    assert is_timestamp_in_billing_period(w, datetime(2026, 1, 1, 1, 0, 0)) is False
'''
    }

    t2009_ref = {
        "intervals.py": '''"""Billing period interval membership checker."""
from datetime import datetime
from calendar_models import BillingWindow
from formatters import format_window_label

def is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:
    """Check if target timestamp falls within the billing window.
    Interval convention: half-open interval [start, end), where start is inclusive and end is exclusive.
    """
    return window.start_dt <= target_dt < window.end_dt

def filter_billing_events(window: BillingWindow, timestamps: list) -> list:
    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]

def get_window_summary(window: BillingWindow) -> str:
    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"
'''
    }

    t2009_m1 = {
        "intervals.py": '''"""Billing period interval membership checker."""
from datetime import datetime
from calendar_models import BillingWindow
from formatters import format_window_label

def is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:
    return window.start_dt < target_dt <= window.end_dt

def filter_billing_events(window: BillingWindow, timestamps: list) -> list:
    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]

def get_window_summary(window: BillingWindow) -> str:
    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"
'''
    }

    t2009_m2 = {
        "intervals.py": '''"""Billing period interval membership checker."""
from datetime import datetime
from calendar_models import BillingWindow
from formatters import format_window_label

def is_timestamp_in_billing_period(window: BillingWindow, target_dt: datetime) -> bool:
    return window.start_dt < target_dt < window.end_dt

def filter_billing_events(window: BillingWindow, timestamps: list) -> list:
    return [t for t in timestamps if is_timestamp_in_billing_period(window, t)]

def get_window_summary(window: BillingWindow) -> str:
    return f"BillingWindow({format_window_label(window.start_dt, window.end_dt)})"
'''
    }

    add_task(
        tid=2009,
        family="calendar_recurrence",
        name="Billing Period Interval Calculator",
        class_tag="STATED",
        issue="Subscription billing incident SUB-801: Customers double-billed on the exact boundary timestamp between consecutive monthly subscription cycles.",
        traceback_text="FAILED tests/test_intervals_cases.py::test_interval_end_boundary - AssertionError: assert True is False",
        traceback_files=["intervals.py"],
        repo=t2009_repo,
        hidden=t2009_hidden,
        ref=t2009_ref,
        mutant1=t2009_m1,
        mutant2=t2009_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H05"],
        assertions=[
            ("test_interval_end_boundary", "intervals.py docstring: 'half-open interval [start, end), where start is inclusive and end is exclusive'", "Yes", "STATED"),
            ("test_interval_subsecond_boundary", "intervals.py docstring: 'half-open interval [start, end)'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2010: Subscription Active Window Evaluator (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2010_repo = {
        "rules.py": '''"""Subscription entitlement schemas."""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Entitlement:
    user_id: int
    plan: str
    tier: int = 1
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = ["basic_access"]

    def is_premium(self) -> bool:
        return self.tier > 1

    def has_feature(self, feat: str) -> bool:
        return feat in self.features
''',
        "subscription.py": '''"""Subscription authorization service."""
from rules import Entitlement
from period_calc import check_in_window

def is_entitled_at(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> bool:
    """Evaluate whether user plan entitlement is active at current_epoch timestamp."""
    return check_in_window(start_epoch, end_epoch, current_epoch)

def get_entitlement_status(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> dict:
    active = is_entitled_at(user_id, plan, start_epoch, end_epoch, current_epoch)
    return {"user_id": user_id, "plan": plan, "active": active}

def describe_window(start_epoch: int, end_epoch: int) -> str:
    return f"Window(from={start_epoch}, to={end_epoch})"
''',
        "period_calc.py": '''"""Low-level timestamp window evaluator."""
def check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:
    return start_ts <= probe_ts <= end_ts

def get_window_duration(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)

def is_valid_epoch_range(start_ts: int, end_ts: int) -> bool:
    return end_ts >= start_ts >= 0
''',
        "tests/test_subscription.py": '''from subscription import is_entitled_at, get_entitlement_status

def test_nominal_active():
    assert is_entitled_at(101, "pro", 1000, 2000, 1500) is True
    assert is_entitled_at(101, "pro", 1000, 2000, 500) is False
    assert is_entitled_at(101, "pro", 1000, 2000, 1000) is True
'''
    }

    t2010_hidden = {
        "tests/test_subscription_cases.py": '''from subscription import is_entitled_at
from period_calc import check_in_window

def test_window_expiration():
    assert is_entitled_at(101, "pro", 1000, 2000, 2000) is False
    assert is_entitled_at(101, "pro", 1000, 2000, 1999) is True

def test_period_calc_contract():
    assert check_in_window(100, 200, 200) is False
    assert check_in_window(100, 200, 100) is True
'''
    }

    t2010_ref = {
        "period_calc.py": '''"""Low-level timestamp window evaluator."""
def check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:
    return start_ts <= probe_ts < end_ts

def get_window_duration(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)
'''
    }

    t2010_m1 = {
        "subscription.py": '''"""Subscription authorization service."""
from rules import Entitlement
from period_calc import check_in_window

def is_entitled_at(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> bool:
    if current_epoch >= end_epoch:
        return False
    return check_in_window(start_epoch, end_epoch, current_epoch)

def get_entitlement_status(user_id: int, plan: str, start_epoch: int, end_epoch: int, current_epoch: int) -> dict:
    active = is_entitled_at(user_id, plan, start_epoch, end_epoch, current_epoch)
    return {"user_id": user_id, "plan": plan, "active": active}
'''
    }

    t2010_m2 = {
        "period_calc.py": '''"""Low-level timestamp window evaluator."""
def check_in_window(start_ts: int, end_ts: int, probe_ts: int) -> bool:
    return start_ts <= probe_ts <= end_ts

def get_window_duration(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)
'''
    }

    add_task(
        tid=2010,
        family="calendar_recurrence",
        name="Subscription Active Window Evaluator",
        class_tag="TAUGHT",
        issue="Access control report ACC-404: Expired user account retained active entitlement access for one second after subscription window lapsed.",
        traceback_text="FAILED tests/test_subscription_cases.py::test_window_expiration - AssertionError: assert True is False",
        traceback_files=["subscription.py"],
        repo=t2010_repo,
        hidden=t2010_hidden,
        ref=t2010_ref,
        mutant1=t2010_m1,
        mutant2=t2010_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H05"],
        assertions=[
            ("test_window_expiration", "HANDBOOK.md Rule H05: Half-open intervals [start, end)", "No", "TAUGHT"),
            ("test_period_calc_contract", "HANDBOOK.md Rule H05: Half-open intervals [start, end)", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2011: Maintenance Window Scheduler (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2011_repo = {
        "slots.py": '''"""Maintenance slot reservation schemas."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class MaintenanceSlot:
    slot_id: str
    start_hour: int
    end_hour: int
    approved: bool = True
    cluster_id: str = "cluster-01"

    def duration(self) -> int:
        return self.end_hour - self.start_hour

    def to_record(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "span": f"[{self.start_hour}, {self.end_hour})",
            "cluster": self.cluster_id,
        }
''',
        "audit.py": '''"""Maintenance schedule auditor."""
from typing import List
from slots import MaintenanceSlot

def total_scheduled_hours(slots: List[MaintenanceSlot]) -> int:
    return sum(s.duration() for s in slots)

def validate_all_approved(slots: List[MaintenanceSlot]) -> bool:
    return all(s.approved for s in slots)
''',
        "maintenance.py": '''"""Cluster maintenance scheduler."""
from typing import List
from slots import MaintenanceSlot
from audit import validate_all_approved

def has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:
    """Detect if two maintenance slots overlap.
    Interval contract: slots are half-open intervals [start, end). Adjacent slots sharing
    a boundary (e.g. [2, 4) and [4, 6)) do NOT overlap.
    """
    return not (slot_a.end_hour < slot_b.start_hour or slot_b.end_hour < slot_a.start_hour)

def can_schedule_slot(existing_slots: List[MaintenanceSlot], candidate: MaintenanceSlot) -> bool:
    if not validate_all_approved(existing_slots):
        raise ValueError("Existing slots contain unapproved reservations")
    return not any(has_window_overlap(s, candidate) for s in existing_slots)

def get_slot_bounds(slots: List[MaintenanceSlot]) -> tuple:
    if not slots:
        return (0, 0)
    return (min(s.start_hour for s in slots), max(s.end_hour for s in slots))
''',
        "tests/test_maintenance.py": '''from slots import MaintenanceSlot
from maintenance import has_window_overlap

def test_disjoint_slots():
    a = MaintenanceSlot("s1", 1, 3)
    b = MaintenanceSlot("s2", 5, 7)
    assert has_window_overlap(a, b) is False

def test_adjacent_slots():
    a = MaintenanceSlot("s1", 2, 4)
    b = MaintenanceSlot("s2", 4, 6)
    assert has_window_overlap(a, b) is False
'''
    }

    t2011_hidden = {
        "tests/test_maintenance_cases.py": '''from slots import MaintenanceSlot
from maintenance import has_window_overlap

def test_touching_slot_boundaries():
    a = MaintenanceSlot("s1", 2, 4)
    b = MaintenanceSlot("s2", 4, 6)
    assert has_window_overlap(a, b) is False

def test_nested_slot():
    a = MaintenanceSlot("s1", 1, 10)
    b = MaintenanceSlot("s2", 3, 5)
    assert has_window_overlap(a, b) is True
'''
    }

    t2011_ref = {
        "maintenance.py": '''"""Cluster maintenance scheduler."""
from typing import List
from slots import MaintenanceSlot
from audit import validate_all_approved

def has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:
    """Detect if two maintenance slots overlap.
    Interval contract: slots are half-open intervals [start, end). Adjacent slots sharing
    a boundary (e.g. [2, 4) and [4, 6)) do NOT overlap.
    """
    return not (slot_a.end_hour <= slot_b.start_hour or slot_b.end_hour <= slot_a.start_hour)

def can_schedule_slot(existing_slots: List[MaintenanceSlot], candidate: MaintenanceSlot) -> bool:
    if not validate_all_approved(existing_slots):
        raise ValueError("Existing slots contain unapproved reservations")
    return not any(has_window_overlap(s, candidate) for s in existing_slots)

def get_slot_bounds(slots: List[MaintenanceSlot]) -> tuple:
    if not slots:
        return (0, 0)
    return (min(s.start_hour for s in slots), max(s.end_hour for s in slots))
'''
    }

    t2011_m1 = {
        "maintenance.py": '''"""Cluster maintenance scheduler."""
from slots import MaintenanceSlot
from audit import validate_all_approved

def has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:
    return max(slot_a.start_hour, slot_b.start_hour) <= min(slot_a.end_hour, slot_b.end_hour)

def can_schedule_slot(existing_slots: list, candidate: MaintenanceSlot) -> bool:
    return not any(has_window_overlap(s, candidate) for s in existing_slots)
'''
    }

    t2011_m2 = {
        "maintenance.py": '''"""Cluster maintenance scheduler."""
from slots import MaintenanceSlot
from audit import validate_all_approved

def has_window_overlap(slot_a: MaintenanceSlot, slot_b: MaintenanceSlot) -> bool:
    return False

def can_schedule_slot(existing_slots: list, candidate: MaintenanceSlot) -> bool:
    return True
'''
    }

    add_task(
        tid=2011,
        family="calendar_recurrence",
        name="Maintenance Window Scheduler",
        class_tag="STATED",
        issue="Operations incident OPS-202: Maintenance scheduling system rejected valid contiguous deployment windows as conflicting collisions.",
        traceback_text="FAILED tests/test_maintenance.py::test_adjacent_slots - AssertionError: assert True is False",
        traceback_files=["maintenance.py"],
        repo=t2011_repo,
        hidden=t2011_hidden,
        ref=t2011_ref,
        mutant1=t2011_m1,
        mutant2=t2011_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H05"],
        assertions=[
            ("test_touching_slot_boundaries", "maintenance.py docstring: 'slots are half-open intervals [start, end)'", "Yes", "STATED"),
            ("test_nested_slot", "maintenance.py docstring: 'slots are half-open intervals [start, end)'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2012: Audit Log Retention Window (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2012_repo = {
        "log_store.py": '''"""Log storage models."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class LogEntry:
    entry_id: str
    timestamp: int
    source: str = "app"
    severity: str = "INFO"

    def is_system(self) -> bool:
        return self.source == "system"

    def is_error(self) -> bool:
        return self.severity in ("ERROR", "FATAL")

    def to_record(self) -> Dict[str, Any]:
        return {"id": self.entry_id, "ts": self.timestamp, "sev": self.severity}
''',
        "window_evaluator.py": '''"""Retention window evaluator."""
def is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:
    return start_ts <= ts <= end_ts

def get_window_span(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)

def is_valid_cutoff(start_ts: int, end_ts: int) -> bool:
    return start_ts <= end_ts
''',
        "retention.py": '''"""Audit log retention manager."""
from typing import List
from window_evaluator import is_within_retention
from log_store import LogEntry

def filter_retained_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> List[LogEntry]:
    """Filter logs that fall into the active retention period."""
    return [l for l in logs if is_within_retention(l.timestamp, cutoff_start, cutoff_end)]

def count_purged_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> int:
    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)
    return len(logs) - len(retained)

def group_retained_by_source(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> dict:
    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)
    res = {}
    for l in retained:
        res.setdefault(l.source, []).append(l)
    return res
''',
        "tests/test_retention.py": '''from log_store import LogEntry
from retention import filter_retained_logs

def test_nominal_filtering():
    logs = [LogEntry("l1", 100), LogEntry("l2", 500)]
    retained = filter_retained_logs(logs, 50, 200)
    assert len(retained) == 1
    assert retained[0].entry_id == "l1"
'''
    }

    t2012_hidden = {
        "tests/test_retention_cases.py": '''from log_store import LogEntry
from retention import filter_retained_logs
from window_evaluator import is_within_retention

def test_retention_window_cutoff():
    logs = [LogEntry("start", 100), LogEntry("end", 200)]
    retained = filter_retained_logs(logs, 100, 200)
    assert len(retained) == 1
    assert retained[0].entry_id == "start"

def test_window_evaluator_contract():
    assert is_within_retention(100, 100, 200) is True
    assert is_within_retention(200, 100, 200) is False
'''
    }

    t2012_ref = {
        "window_evaluator.py": '''"""Retention window evaluator."""
def is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:
    return start_ts <= ts < end_ts

def get_window_span(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)
'''
    }

    t2012_m1 = {
        "retention.py": '''"""Audit log retention manager."""
from typing import List
from window_evaluator import is_within_retention
from log_store import LogEntry

def filter_retained_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> List[LogEntry]:
    return [l for l in logs if l.timestamp < cutoff_end and is_within_retention(l.timestamp, cutoff_start, cutoff_end)]

def count_purged_logs(logs: List[LogEntry], cutoff_start: int, cutoff_end: int) -> int:
    retained = filter_retained_logs(logs, cutoff_start, cutoff_end)
    return len(logs) - len(retained)
'''
    }

    t2012_m2 = {
        "window_evaluator.py": '''"""Retention window evaluator."""
def is_within_retention(ts: int, start_ts: int, end_ts: int) -> bool:
    return start_ts < ts < end_ts

def get_window_span(start_ts: int, end_ts: int) -> int:
    return max(0, end_ts - start_ts)
'''
    }

    add_task(
        tid=2012,
        family="calendar_recurrence",
        name="Audit Log Retention Window",
        class_tag="TAUGHT",
        issue="Compliance audit AUD-601: Expired audit log records on the exact daily archive cutoff timestamp were retained past required purge window.",
        traceback_text="FAILED tests/test_retention_cases.py::test_retention_window_cutoff - AssertionError: assert 2 == 1",
        traceback_files=["retention.py"],
        repo=t2012_repo,
        hidden=t2012_hidden,
        ref=t2012_ref,
        mutant1=t2012_m1,
        mutant2=t2012_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H05"],
        assertions=[
            ("test_retention_window_cutoff", "HANDBOOK.md Rule H05: Half-open intervals [start, end)", "No", "TAUGHT"),
            ("test_window_evaluator_contract", "HANDBOOK.md Rule H05: Half-open intervals [start, end)", "No", "TAUGHT")
        ]
    )

    print("Family 3 registered (Tasks 2009-2012).")
