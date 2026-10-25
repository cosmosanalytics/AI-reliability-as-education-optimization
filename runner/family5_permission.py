"""Family 5: permission_prefix (Tasks 2017 - 2020).

Governing Rule: Rule H06 (Double-Colon Scopes: tenant::dept::service::action, * single segment, ** multi-segment, :: segment boundary).
Competing Alternatives: Naive startswith() which falsely matches ::sibling_extra, exact string equality ==.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_5(add_task):
    # =========================================================================
    # Task 2017: API Scope Authorization Guard (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2017_repo = {
        "policy.py": '''"""Authorization policy schemas."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RoutePolicy:
    role: str
    allowed_pattern: str
    description: str = ""
    is_active: bool = True

    def matches_role(self, candidate_role: str) -> bool:
        return self.role == candidate_role

    def is_wildcard(self) -> bool:
        return self.allowed_pattern == "**"

    def summary(self) -> str:
        return f"Policy(role={self.role}, pattern={self.allowed_pattern})"
''',
        "url_normalizer.py": '''"""Scope string sanitizers."""
def strip_protocol(url: str) -> str:
    if "://" in url:
        return url.split("://", 1)[1]
    return url

def clean_scope(scope_str: str) -> str:
    return scope_str.strip()
''',
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy
from url_normalizer import clean_scope

def is_scope_permitted(policy: RoutePolicy, request_scope: str) -> bool:
    """Check if request_scope is authorized under policy.allowed_pattern.
    Access control scopes must use the double-colon hierarchy tenant::department::service::action.
    Sibling paths must be checked against '::' segment boundaries.
    The single asterisk wildcard '*' matches exactly one segment; the double asterisk '**' matches arbitrary multi-segment prefixes.
    """
    clean_req = clean_scope(request_scope)
    return clean_req.startswith(policy.allowed_pattern)

def evaluate_request(policies: list, role: str, scope: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_scope_permitted(p, scope):
            return True
    return False

def count_permitted_scopes(policy: RoutePolicy, scopes: list) -> int:
    return sum(1 for s in scopes if is_scope_permitted(policy, s))
''',
        "tests/test_guard.py": '''from policy import RoutePolicy
from guard import is_scope_permitted

def test_nominal_match():
    p = RoutePolicy("admin", "corp::billing::*")
    assert is_scope_permitted(p, "corp::billing::invoices") is True
    assert is_scope_permitted(p, "corp::other::login") is False

def test_sibling_path_boundary():
    p = RoutePolicy("analyst", "corp::reports")
    assert is_scope_permitted(p, "corp::reports_secret") is False
'''
    }

    t2017_hidden = {
        "tests/test_guard_cases.py": '''from policy import RoutePolicy
from guard import is_scope_permitted

def test_wildcard_matching():
    p_single = RoutePolicy("auditor", "corp::billing::*")
    assert is_scope_permitted(p_single, "corp::billing::invoices") is True
    assert is_scope_permitted(p_single, "corp::billing::invoices::read") is False
    
    p_multi = RoutePolicy("admin", "corp::billing::**")
    assert is_scope_permitted(p_multi, "corp::billing::invoices") is True
    assert is_scope_permitted(p_multi, "corp::billing::invoices::read") is True
    assert is_scope_permitted(p_multi, "corp::billing::invoices::read::details") is True
    assert is_scope_permitted(p_multi, "corp::billing_other::invoices") is False
'''
    }

    t2017_ref = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy
from url_normalizer import clean_scope

def _match_scope(pattern: str, target: str) -> bool:
    pat_segs = pattern.split("::")
    tgt_segs = target.split("::")
    if "**" in pat_segs:
        idx = pat_segs.index("**")
        prefix_pats = pat_segs[:idx]
        if len(tgt_segs) < len(prefix_pats):
            return False
        for p, t in zip(prefix_pats, tgt_segs[:len(prefix_pats)]):
            if p != "*" and p != t:
                return False
        return True
    if len(pat_segs) != len(tgt_segs):
        return False
    for p, t in zip(pat_segs, tgt_segs):
        if p != "*" and p != t:
            return False
    return True

def is_scope_permitted(policy: RoutePolicy, request_scope: str) -> bool:
    """Check if request_scope is authorized under policy.allowed_pattern.
    Access control scopes must use the double-colon hierarchy tenant::department::service::action.
    Sibling paths must be checked against '::' segment boundaries.
    The single asterisk wildcard '*' matches exactly one segment; the double asterisk '**' matches arbitrary multi-segment prefixes.
    """
    clean_req = clean_scope(request_scope)
    return _match_scope(policy.allowed_pattern, clean_req)

def evaluate_request(policies: list, role: str, scope: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_scope_permitted(p, scope):
            return True
    return False
'''
    }

    t2017_m1 = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy
from url_normalizer import clean_scope

def is_scope_permitted(policy: RoutePolicy, request_scope: str) -> bool:
    clean_req = clean_scope(request_scope)
    return clean_req.startswith(policy.allowed_pattern)

def evaluate_request(policies: list, role: str, scope: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_scope_permitted(p, scope):
            return True
    return False
'''
    }

    t2017_m2 = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy
from url_normalizer import clean_scope

def is_scope_permitted(policy: RoutePolicy, request_scope: str) -> bool:
    clean_req = clean_scope(request_scope)
    return policy.allowed_pattern == clean_req

def evaluate_request(policies: list, role: str, scope: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_scope_permitted(p, scope):
            return True
    return False
'''
    }

    add_task(
        tid=2017,
        family="permission_prefix",
        name="API Scope Authorization Guard",
        class_tag="STATED",
        issue="Security vulnerability SEC-810: Gateway allowed unauthorized access to corp::reports_secret under standard corp::reports policy.",
        traceback_text="FAILED tests/test_guard.py::test_sibling_path_boundary - AssertionError: assert True is False",
        traceback_files=["guard.py"],
        repo=t2017_repo,
        hidden=t2017_hidden,
        ref=t2017_ref,
        mutant1=t2017_m1,
        mutant2=t2017_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H06"],
        assertions=[
            ("test_wildcard_matching", "guard.py docstring: 'The single asterisk wildcard * matches exactly one segment; the double asterisk ** matches arbitrary multi-segment prefixes'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2018: Document Store Scope RBAC Filter (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2018_repo = {
        "path_resolver.py": '''"""Scope resolver utilities."""
from typing import List, Optional

def clean_scope(scope_str: str) -> str:
    """Strips whitespace and normalizes scope string."""
    return scope_str.strip() if scope_str else ""

def split_scope_segments(scope_str: str) -> List[str]:
    """Splits hierarchy by double-colon delimiter."""
    return [seg for seg in clean_scope(scope_str).split("::") if seg]

def count_scope_segments(scope_str: str) -> int:
    """Returns number of segments in scope string."""
    return len(split_scope_segments(scope_str))

def validate_scope_syntax(scope_str: str) -> bool:
    """Validates scope string has non-empty segments."""
    segs = split_scope_segments(scope_str)
    return len(segs) > 0 and all(len(s) > 0 for s in segs)
''',
        "audit_logger.py": '''"""Access attempt logger."""
from typing import Dict, Any

def format_access_attempt(folder: str, path: str, allowed: bool) -> str:
    """Formats human-readable access attempt entry."""
    status = "ALLOWED" if allowed else "DENIED"
    return f"[{status}] scope={folder} path={path}"

def is_security_audit_enabled() -> bool:
    """Returns True if access logging is active."""
    return True

def get_audit_channel() -> str:
    """Default audit log channel."""
    return "security-audit-stream"

def record_audit_entry(folder: str, path: str, allowed: bool) -> Dict[str, Any]:
    """Returns structured telemetry dict for audit stream."""
    return {
        "scope": folder,
        "path": path,
        "allowed": allowed,
        "channel": get_audit_channel(),
    }
''',
        "rbac.py": '''"""Document scope RBAC filter."""
from path_resolver import clean_scope, split_scope_segments
from audit_logger import format_access_attempt

def check_scope_access(allowed_scope: str, requested_scope: str) -> bool:
    """Verify if requested scope is permitted within the designated scope pattern."""
    allowed = clean_scope(requested_scope).startswith(clean_scope(allowed_scope))
    _ = format_access_attempt(allowed_scope, requested_scope, allowed)
    return allowed

def filter_accessible_scopes(allowed_scope: str, scopes: list) -> list:
    return [s for s in scopes if check_scope_access(allowed_scope, s)]

def can_access_all_scopes(allowed_scope: str, scopes: list) -> bool:
    return all(check_scope_access(allowed_scope, s) for s in scopes)
''',
        "tests/test_rbac.py": '''from rbac import check_scope_access

def test_nominal_scope_access():
    assert check_scope_access("corp::public::*", "corp::public::readme") is True
    assert check_scope_access("corp::public", "corp::private::secret") is False

def test_scope_prefix_boundary():
    assert check_scope_access("corp::public", "corp::public_internal::secret") is False
'''
    }

    t2018_hidden = {
        "tests/test_rbac_cases.py": '''from rbac import check_scope_access

def test_wildcard_hierarchy():
    assert check_scope_access("corp::docs::*", "corp::docs::report") is True
    assert check_scope_access("corp::docs::*", "corp::docs::archive::file") is False
    assert check_scope_access("corp::docs::**", "corp::docs::archive::file") is True
    assert check_scope_access("corp::docs::**", "corp::docs_extra::file") is False
'''
    }

    t2018_ref = {
        "rbac.py": '''"""Document scope RBAC filter."""
from path_resolver import clean_scope
from audit_logger import format_access_attempt

def _match_scope(pattern: str, target: str) -> bool:
    pat_segs = pattern.split("::")
    tgt_segs = target.split("::")
    if "**" in pat_segs:
        idx = pat_segs.index("**")
        prefix_pats = pat_segs[:idx]
        if len(tgt_segs) < len(prefix_pats):
            return False
        for p, t in zip(prefix_pats, tgt_segs[:len(prefix_pats)]):
            if p != "*" and p != t:
                return False
        return True
    if len(pat_segs) != len(tgt_segs):
        return False
    for p, t in zip(pat_segs, tgt_segs):
        if p != "*" and p != t:
            return False
    return True

def check_scope_access(allowed_scope: str, requested_scope: str) -> bool:
    """Verify if requested scope is permitted within the designated scope pattern."""
    target = clean_scope(requested_scope)
    pat = clean_scope(allowed_scope)
    allowed = _match_scope(pat, target)
    _ = format_access_attempt(allowed_scope, requested_scope, allowed)
    return allowed

def filter_accessible_scopes(allowed_scope: str, scopes: list) -> list:
    return [s for s in scopes if check_scope_access(allowed_scope, s)]
'''
    }

    t2018_m1 = {
        "rbac.py": '''"""Document scope RBAC filter."""
from path_resolver import clean_scope
from audit_logger import format_access_attempt

def check_scope_access(allowed_scope: str, requested_scope: str) -> bool:
    allowed = clean_scope(requested_scope).startswith(clean_scope(allowed_scope))
    _ = format_access_attempt(allowed_scope, requested_scope, allowed)
    return allowed

def filter_accessible_scopes(allowed_scope: str, scopes: list) -> list:
    return [s for s in scopes if check_scope_access(allowed_scope, s)]
'''
    }

    t2018_m2 = {
        "rbac.py": '''"""Document scope RBAC filter."""
from path_resolver import clean_scope
from audit_logger import format_access_attempt

def check_scope_access(allowed_scope: str, requested_scope: str) -> bool:
    allowed = (clean_scope(allowed_scope) == clean_scope(requested_scope))
    _ = format_access_attempt(allowed_scope, requested_scope, allowed)
    return allowed

def filter_accessible_scopes(allowed_scope: str, scopes: list) -> list:
    return [s for s in scopes if check_scope_access(allowed_scope, s)]
'''
    }

    add_task(
        tid=2018,
        family="permission_prefix",
        name="Document Store Scope RBAC Filter",
        class_tag="TAUGHT",
        issue="Audit finding SEC-903: File storage permissions granted access to unauthorized sibling scope corp::public_internal under corp::public permission.",
        traceback_text="FAILED tests/test_rbac.py::test_scope_prefix_boundary - AssertionError: assert True is False",
        traceback_files=["rbac.py"],
        repo=t2018_repo,
        hidden=t2018_hidden,
        ref=t2018_ref,
        mutant1=t2018_m1,
        mutant2=t2018_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H06"],
        assertions=[
            ("test_wildcard_hierarchy", "HANDBOOK.md Rule H06: Double-colon scopes and wildcard hierarchy", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2019: Asset Storage Scope Validator (STATED, HRC=True, VTS=False)
    # =========================================================================
    t2019_repo = {
        "models.py": '''"""Storage bucket asset records."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class StorageAsset:
    asset_id: str
    scope_path: str
    bucket: str = "default-assets"
    content_type: str = "application/octet-stream"

    def extension(self) -> str:
        if "." in self.scope_path:
            return self.scope_path.rsplit(".", 1)[1]
        return ""

    def is_image(self) -> bool:
        return self.extension().lower() in ("png", "jpg", "jpeg", "gif", "webp")

    def to_descriptor(self) -> Dict[str, Any]:
        return {
            "id": self.asset_id,
            "scope": self.scope_path,
            "bucket": self.bucket,
            "ext": self.extension(),
        }
''',
        "path_normalizer.py": '''"""Storage scope normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_scope: str) -> bool:
    return asset_scope.startswith(scope_prefix)

def get_scope_depth(scope_str: str) -> int:
    return len([seg for seg in scope_str.split("::") if seg])

def normalize_scope(scope_str: str) -> str:
    return scope_str.strip()
''',
        "asset_service.py": '''"""Asset bucket retrieval service."""
from path_normalizer import validate_prefix_match, get_scope_depth
from models import StorageAsset

def can_access_asset(asset: StorageAsset, required_scope: str) -> bool:
    """Check if asset scope matches the required storage scope.
    Access control scopes must use the double-colon hierarchy tenant::department::service::action.
    Sibling paths must be checked against '::' segment boundaries.
    """
    return validate_prefix_match(required_scope, asset.scope_path)

def filter_accessible_assets(assets: list, required_scope: str) -> list:
    return [a for a in assets if can_access_asset(a, required_scope)]

def get_asset_hierarchy_level(asset: StorageAsset) -> int:
    return get_scope_depth(asset.scope_path)
''',
        "tests/test_asset.py": '''from models import StorageAsset
from asset_service import can_access_asset

def test_nominal_asset():
    a = StorageAsset("A1", "assets::images::logo")
    assert can_access_asset(a, "assets::images") is True
    assert can_access_asset(a, "data") is False
'''
    }

    t2019_hidden = {
        "tests/test_asset_cases.py": '''from models import StorageAsset
from asset_service import can_access_asset
from path_normalizer import validate_prefix_match

def test_resource_isolation():
    a1 = StorageAsset("A2", "assets::images_private::secret")
    assert can_access_asset(a1, "assets::images") is False
    
    a2 = StorageAsset("A3", "assets::images::sub")
    assert can_access_asset(a2, "assets::images") is True

def test_path_normalizer_contract():
    assert validate_prefix_match("assets::images", "assets::images_private") is False
    assert validate_prefix_match("assets::images", "assets::images") is True
'''
    }

    t2019_ref = {
        "path_normalizer.py": '''"""Storage scope normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_scope: str) -> bool:
    scope = scope_prefix.strip()
    target = asset_scope.strip()
    if target == scope:
        return True
    return target.startswith(scope + "::")

def get_scope_depth(scope_str: str) -> int:
    return len([seg for seg in scope_str.split("::") if seg])

def normalize_scope(scope_str: str) -> str:
    return scope_str.strip()
'''
    }

    t2019_m1 = {
        "asset_service.py": '''"""Asset bucket retrieval service."""
from path_normalizer import validate_prefix_match
from models import StorageAsset

def can_access_asset(asset: StorageAsset, required_scope: str) -> bool:
    s = required_scope.strip()
    p = asset.scope_path.strip()
    if p != s and not p.startswith(s + "::"):
        return False
    return validate_prefix_match(required_scope, asset.scope_path)

def filter_accessible_assets(assets: list, required_scope: str) -> list:
    return [a for a in assets if can_access_asset(a, required_scope)]
'''
    }

    t2019_m2 = {
        "path_normalizer.py": '''"""Storage scope normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_scope: str) -> bool:
    return asset_scope.startswith(scope_prefix)

def get_scope_depth(scope_str: str) -> int:
    return len([seg for seg in scope_str.split("::") if seg])
'''
    }

    add_task(
        tid=2019,
        family="permission_prefix",
        name="Asset Storage Scope Validator",
        class_tag="STATED",
        issue="Cloud storage incident CLD-512: Private asset scope assets::images_private was exposed to users granted standard assets::images access.",
        traceback_text="FAILED tests/test_asset_cases.py::test_resource_isolation - AssertionError: assert True is False",
        traceback_files=["asset_service.py"],
        repo=t2019_repo,
        hidden=t2019_hidden,
        ref=t2019_ref,
        mutant1=t2019_m1,
        mutant2=t2019_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H06"],
        assertions=[
            ("test_resource_isolation", "asset_service.py docstring: 'matches full segment boundaries under :: delimiter'", "Yes", "STATED"),
            ("test_path_normalizer_contract", "path_normalizer.py module contract", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2020: Webhook Subscription Scope Enforcer (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2020_repo = {
        "webhook.py": '''"""Webhook event payload models."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class WebhookEvent:
    topic_path: str
    payload: str
    event_id: str = "EVT-DEFAULT"
    retry_count: int = 0

    def is_empty(self) -> bool:
        return not bool(self.payload)

    def topic_root(self) -> str:
        return self.topic_path.split("::")[0]

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "id": self.event_id,
            "topic": self.topic_path,
            "payload": self.payload,
            "retries": self.retry_count,
        }
''',
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    return event_topic.startswith(subscribed_pattern)

def clean_topic_segment(topic: str) -> str:
    return topic.strip().lower()

def is_wildcard_subscription(pattern: str) -> bool:
    return pattern.strip() in ("*", "**")
''',
        "scope_checker.py": '''"""Webhook scope dispatch checker."""
from prefix_validator import is_topic_subscribed, clean_topic_segment
from webhook import WebhookEvent

def should_dispatch_webhook(subscribed_topic: str, event: WebhookEvent) -> bool:
    """Determine if webhook event topic is permitted under the subscription filter."""
    return is_topic_subscribed(subscribed_topic, event.topic_path)

def filter_dispatch_queue(subscribed_topic: str, events: list) -> list:
    return [e for e in events if should_dispatch_webhook(subscribed_topic, e)]

def batch_topic_summary(events: list) -> dict:
    summary = {}
    for e in events:
        summary[e.topic_path] = summary.get(e.topic_path, 0) + 1
    return summary
''',
        "tests/test_scope.py": '''from webhook import WebhookEvent
from scope_checker import should_dispatch_webhook

def test_nominal_topic():
    evt = WebhookEvent("orders::created", "{'id': 1}")
    assert should_dispatch_webhook("orders", evt) is True
    assert should_dispatch_webhook("billing", evt) is False
'''
    }

    t2020_hidden = {
        "tests/test_scope_cases.py": '''from webhook import WebhookEvent
from scope_checker import should_dispatch_webhook
from prefix_validator import is_topic_subscribed

def test_channel_routing():
    evt_sibling = WebhookEvent("orders_admin::reindex", "{}")
    assert should_dispatch_webhook("orders", evt_sibling) is False
    
    evt_child = WebhookEvent("orders::reindex", "{}")
    assert should_dispatch_webhook("orders", evt_child) is True

def test_prefix_validator_contract():
    assert is_topic_subscribed("orders", "orders_admin") is False
    assert is_topic_subscribed("orders", "orders::created") is True
'''
    }

    t2020_ref = {
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    pat = subscribed_pattern.strip()
    topic = event_topic.strip()
    if topic == pat:
        return True
    return topic.startswith(pat + "::")

def clean_topic_segment(topic: str) -> str:
    return topic.strip().lower()

def is_wildcard_subscription(pattern: str) -> bool:
    return pattern.strip() in ("*", "**")
'''
    }

    t2020_m1 = {
        "scope_checker.py": '''"""Webhook scope dispatch checker."""
from prefix_validator import is_topic_subscribed
from webhook import WebhookEvent

def should_dispatch_webhook(subscribed_topic: str, event: WebhookEvent) -> bool:
    p = subscribed_topic.strip()
    t = event.topic_path.strip()
    if t != p and not t.startswith(p + "::"):
        return False
    return is_topic_subscribed(subscribed_topic, event.topic_path)

def filter_dispatch_queue(subscribed_topic: str, events: list) -> list:
    return [e for e in events if should_dispatch_webhook(subscribed_topic, e)]
'''
    }

    t2020_m2 = {
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    return subscribed_pattern.strip() == event_topic.strip()

def clean_topic_segment(topic: str) -> str:
    return topic.strip().lower()
'''
    }

    add_task(
        tid=2020,
        family="permission_prefix",
        name="Webhook Subscription Scope Enforcer",
        class_tag="TAUGHT",
        issue="Event bus leak EVT-918: Consumer subscribed to 'orders' topic received internal administrative events from 'orders_admin'.",
        traceback_text="FAILED tests/test_scope_cases.py::test_channel_routing - AssertionError: assert True is False",
        traceback_files=["scope_checker.py"],
        repo=t2020_repo,
        hidden=t2020_hidden,
        ref=t2020_ref,
        mutant1=t2020_m1,
        mutant2=t2020_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H06"],
        assertions=[
            ("test_channel_routing", "HANDBOOK.md Rule H06: Double-colon scope hierarchy and segment boundaries", "No", "TAUGHT"),
            ("test_prefix_validator_contract", "HANDBOOK.md Rule H06: Double-colon scope hierarchy and segment boundaries", "No", "TAUGHT")
        ]
    )

    print("Family 5 registered (Tasks 2017-2020).")
