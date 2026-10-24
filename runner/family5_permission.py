"""Family 5: permission_prefix (Tasks 2017 - 2020).

Governing Rule: Rule H06 (Trailing slash and prefix normalization: /a matches /a and /a/b but NOT /ab).
Competing Alternatives: Naive startswith() which falsely matches /ab, exact string equality ==.
Target: 40-120 non-test lines across 3-4 files.
"""

def register_family_5(add_task):
    # =========================================================================
    # Task 2017: API Route Authorization Guard (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2017_repo = {
        "policy.py": '''"""Authorization policy schemas."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RoutePolicy:
    role: str
    allowed_prefix: str
    description: str = ""
    is_active: bool = True

    def matches_role(self, candidate_role: str) -> bool:
        return self.role == candidate_role

    def is_wildcard(self) -> bool:
        return self.allowed_prefix == "/"

    def summary(self) -> str:
        return f"Policy(role={self.role}, prefix={self.allowed_prefix})"
''',
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy

def is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:
    """Check if request_path is authorized under policy.allowed_prefix.
    Path matching contract:
    - Normalizes trailing slashes before matching.
    - Matches only full path segments (e.g. '/api' covers '/api' and '/api/v1', but NOT '/api-v2').
    """
    return request_path.startswith(policy.allowed_prefix)

def evaluate_request(policies: list, role: str, path: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_route_permitted(p, path):
            return True
    return False

def count_permitted_routes(policy: RoutePolicy, paths: list) -> int:
    return sum(1 for p in paths if is_route_permitted(policy, p))
''',
        "url_normalizer.py": '''"""URL string sanitizers."""
def strip_protocol(url: str) -> str:
    if "://" in url:
        return url.split("://", 1)[1]
    return url

def remove_query_string(url: str) -> str:
    return url.split("?", 1)[0]
''',
        "tests/test_guard.py": '''from policy import RoutePolicy
from guard import is_route_permitted

def test_nominal_match():
    p = RoutePolicy("admin", "/api/v1")
    assert is_route_permitted(p, "/api/v1/users") is True
    assert is_route_permitted(p, "/other") is False

def test_boundary_visible_sensitive():
    p = RoutePolicy("analyst", "/reports")
    assert is_route_permitted(p, "/reports-secret") is False
'''
    }

    t2017_hidden = {
        "tests/test_guard_hidden.py": '''from policy import RoutePolicy
from guard import is_route_permitted

def test_trailing_slash_normalization():
    p1 = RoutePolicy("user", "/docs/")
    p2 = RoutePolicy("user", "/docs")
    assert is_route_permitted(p1, "/docs") is True
    assert is_route_permitted(p2, "/docs/") is True
    assert is_route_permitted(p2, "/docs/readme.md") is True
    assert is_route_permitted(p2, "/docsextra") is False
'''
    }

    t2017_ref = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy

def is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:
    """Check if request_path is authorized under policy.allowed_prefix.
    Path matching contract:
    - Normalizes trailing slashes before matching.
    - Matches only full path segments (e.g. '/api' covers '/api' and '/api/v1', but NOT '/api-v2').
    """
    prefix = policy.allowed_prefix.rstrip("/")
    path = request_path.rstrip("/")
    if path == prefix:
        return True
    return path.startswith(prefix + "/")

def evaluate_request(policies: list, role: str, path: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_route_permitted(p, path):
            return True
    return False
'''
    }

    t2017_m1 = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy

def is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:
    return request_path.startswith(policy.allowed_prefix)

def evaluate_request(policies: list, role: str, path: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_route_permitted(p, path):
            return True
    return False
'''
    }

    t2017_m2 = {
        "guard.py": '''"""API gateway authorization guard."""
from policy import RoutePolicy

def is_route_permitted(policy: RoutePolicy, request_path: str) -> bool:
    return policy.allowed_prefix.rstrip("/") == request_path.rstrip("/")

def evaluate_request(policies: list, role: str, path: str) -> bool:
    for p in policies:
        if p.matches_role(role) and is_route_permitted(p, path):
            return True
    return False
'''
    }

    add_task(
        tid=2017,
        family="permission_prefix",
        name="API Route Authorization Guard",
        class_tag="STATED",
        issue="Security vulnerability SEC-810: Gateway allowed unauthorized access to /reports-confidential under standard /reports policy.",
        traceback_text="FAILED tests/test_guard.py::test_boundary_visible_sensitive - AssertionError: Authorization leak at guard.py:12: unpermitted sibling path allowed by naive prefix match",
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
            ("test_trailing_slash_normalization", "guard.py docstring: 'Normalizes trailing slashes ... Matches only full path segments'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2018: Document Store RBAC Filter (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2018_repo = {
        "path_resolver.py": '''"""Path resolver utilities."""
from typing import List, Optional

def clean_path(path_str: str) -> str:
    return "/" + path_str.strip("/")

def get_parent_directory(path_str: str) -> str:
    cleaned = clean_path(path_str)
    if "/" in cleaned:
        return cleaned.rsplit("/", 1)[0] or "/"
    return "/"

def split_path_segments(path_str: str) -> List[str]:
    cleaned = clean_path(path_str)
    return [seg for seg in cleaned.split("/") if seg]

def is_root_path(path_str: str) -> bool:
    return clean_path(path_str) == "/"

def count_segments(path_str: str) -> int:
    return len(split_path_segments(path_str))
''',
        "rbac.py": '''"""Document access RBAC filter."""
from path_resolver import clean_path, split_path_segments

def check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:
    """Verify if document path is permitted within the designated folder scope."""
    return clean_path(requested_doc_path).startswith(clean_path(allowed_folder))

def filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:
    return [p for p in doc_paths if check_document_access(allowed_folder, p)]

def can_access_all_docs(allowed_folder: str, doc_paths: list) -> bool:
    return all(check_document_access(allowed_folder, p) for p in doc_paths)
''',
        "audit_logger.py": '''"""Access attempt logger."""
def format_access_attempt(folder: str, path: str, allowed: bool) -> str:
    status = "ALLOWED" if allowed else "DENIED"
    return f"[{status}] scope={folder} path={path}"

def is_security_audit_enabled() -> bool:
    return True

def get_audit_channel() -> str:
    return "security-audit-stream"
''',
        "tests/test_rbac.py": '''from rbac import check_document_access

def test_nominal_folder_access():
    assert check_document_access("/public", "/public/index.html") is True
    assert check_document_access("/public", "/private/index.html") is False

def test_boundary_visible_sensitive():
    assert check_document_access("/public", "/public-internal/secret.pdf") is False
'''
    }

    t2018_hidden = {
        "tests/test_rbac_hidden.py": '''from rbac import check_document_access

def test_taught_segment_and_slash():
    assert check_document_access("/docs/", "/docs") is True
    assert check_document_access("/docs", "/docs/") is True
    assert check_document_access("/docs", "/docs/report.pdf") is True
    assert check_document_access("/docs", "/docsextra/hack.pdf") is False
'''
    }

    t2018_ref = {
        "rbac.py": '''"""Document access RBAC filter."""
from path_resolver import clean_path

def check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:
    """Verify if document path is permitted within the designated folder scope."""
    folder = clean_path(allowed_folder)
    target = clean_path(requested_doc_path)
    if target == folder:
        return True
    return target.startswith(folder + "/")

def filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:
    return [p for p in doc_paths if check_document_access(allowed_folder, p)]
'''
    }

    t2018_m1 = {
        "rbac.py": '''"""Document access RBAC filter."""
from path_resolver import clean_path

def check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:
    return clean_path(requested_doc_path).startswith(clean_path(allowed_folder))

def filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:
    return [p for p in doc_paths if check_document_access(allowed_folder, p)]
'''
    }

    t2018_m2 = {
        "rbac.py": '''"""Document access RBAC filter."""
from path_resolver import clean_path

def check_document_access(allowed_folder: str, requested_doc_path: str) -> bool:
    return clean_path(allowed_folder) == clean_path(requested_doc_path)

def filter_accessible_docs(allowed_folder: str, doc_paths: list) -> list:
    return [p for p in doc_paths if check_document_access(allowed_folder, p)]
'''
    }

    add_task(
        tid=2018,
        family="permission_prefix",
        name="Document Store RBAC Filter",
        class_tag="TAUGHT",
        issue="Audit finding SEC-903: File storage permissions granted access to unauthorized sibling directory /docsextra under /docs permission.",
        traceback_text="FAILED tests/test_rbac.py::test_boundary_visible_sensitive - AssertionError: Access leak at rbac.py:8: sibling path permitted by unsegmented prefix match",
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
            ("test_taught_segment_and_slash", "HANDBOOK.md Rule H06: Trailing slash and path prefix normalization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2019: Asset Storage Prefix Validator (STATED, HRC=True, VTS=False)
    # =========================================================================
    t2019_repo = {
        "models.py": '''"""Storage bucket asset records."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class StorageAsset:
    asset_id: str
    path: str
    bucket: str = "default-assets"
    content_type: str = "application/octet-stream"

    def extension(self) -> str:
        if "." in self.path:
            return self.path.rsplit(".", 1)[1]
        return ""

    def is_image(self) -> bool:
        return self.extension().lower() in ("png", "jpg", "jpeg", "gif", "webp")

    def to_descriptor(self) -> Dict[str, Any]:
        return {
            "id": self.asset_id,
            "path": self.path,
            "bucket": self.bucket,
            "ext": self.extension(),
        }
''',
        "asset_service.py": '''"""Asset bucket retrieval service."""
from path_normalizer import validate_prefix_match, get_scope_depth
from models import StorageAsset

def can_access_asset(asset: StorageAsset, required_scope: str) -> bool:
    """Check if asset path matches the required storage bucket scope.
    Path matching contract: matches full directory segment boundaries and normalizes trailing slashes.
    """
    return validate_prefix_match(required_scope, asset.path)

def filter_accessible_assets(assets: list, required_scope: str) -> list:
    return [a for a in assets if can_access_asset(a, required_scope)]

def get_asset_hierarchy_level(asset: StorageAsset) -> int:
    return get_scope_depth(asset.path)
''',
        "path_normalizer.py": '''"""Storage path normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:
    return asset_path.startswith(scope_prefix)

def get_scope_depth(path: str) -> int:
    return len([seg for seg in path.split("/") if seg])

def normalize_bucket_path(path: str) -> str:
    return "/" + path.strip("/")
''',
        "tests/test_asset.py": '''from models import StorageAsset
from asset_service import can_access_asset

def test_nominal_asset():
    a = StorageAsset("A1", "/assets/images/logo.png")
    assert can_access_asset(a, "/assets") is True
    assert can_access_asset(a, "/data") is False
'''
    }

    t2019_hidden = {
        "tests/test_asset_hidden.py": '''from models import StorageAsset
from asset_service import can_access_asset
from path_normalizer import validate_prefix_match

def test_segment_boundary_stated():
    a1 = StorageAsset("A2", "/assets-private/secret.key")
    assert can_access_asset(a1, "/assets") is False
    
    a2 = StorageAsset("A3", "/assets")
    assert can_access_asset(a2, "/assets/") is True

def test_path_normalizer_direct():
    assert validate_prefix_match("/assets", "/assets-private") is False
    assert validate_prefix_match("/assets/", "/assets") is True
'''
    }

    t2019_ref = {
        "path_normalizer.py": '''"""Storage path normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:
    scope = "/" + scope_prefix.strip("/")
    target = "/" + asset_path.strip("/")
    if target == scope:
        return True
    return target.startswith(scope + "/")

def get_scope_depth(path: str) -> int:
    return len([seg for seg in path.split("/") if seg])
'''
    }

    t2019_m1 = {
        "asset_service.py": '''"""Asset bucket retrieval service."""
from path_normalizer import validate_prefix_match
from models import StorageAsset

def can_access_asset(asset: StorageAsset, required_scope: str) -> bool:
    s = "/" + required_scope.strip("/")
    p = "/" + asset.path.strip("/")
    if p != s and not p.startswith(s + "/"):
        return False
    return validate_prefix_match(required_scope, asset.path)

def filter_accessible_assets(assets: list, required_scope: str) -> list:
    return [a for a in assets if can_access_asset(a, required_scope)]
'''
    }

    t2019_m2 = {
        "path_normalizer.py": '''"""Storage path normalization engine."""
def validate_prefix_match(scope_prefix: str, asset_path: str) -> bool:
    return asset_path.startswith(scope_prefix)

def get_scope_depth(path: str) -> int:
    return len([seg for seg in path.split("/") if seg])
'''
    }

    add_task(
        tid=2019,
        family="permission_prefix",
        name="Asset Storage Prefix Validator",
        class_tag="STATED",
        issue="Cloud storage incident CLD-512: Private asset directory /assets-private was exposed to users granted standard /assets access.",
        traceback_text="FAILED tests/test_asset_hidden.py::test_segment_boundary_stated - AssertionError: Access boundary violation at asset_service.py:10: unsegmented prefix match allowed private sibling bucket",
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
            ("test_segment_boundary_stated", "asset_service.py docstring: 'matches full directory segment boundaries and normalizes trailing slashes'", "Yes", "STATED"),
            ("test_path_normalizer_direct", "path_normalizer.py module contract", "Yes", "STATED")
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
        return self.topic_path.split("/")[0]

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "id": self.event_id,
            "topic": self.topic_path,
            "payload": self.payload,
            "retries": self.retry_count,
        }
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
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    return event_topic.startswith(subscribed_pattern)

def clean_topic_segment(topic: str) -> str:
    return topic.strip().lower()

def is_wildcard_subscription(pattern: str) -> bool:
    return pattern.strip() in ("*", "#", "/")
''',
        "tests/test_scope.py": '''from webhook import WebhookEvent
from scope_checker import should_dispatch_webhook

def test_nominal_topic():
    evt = WebhookEvent("orders/created", "{'id': 1}")
    assert should_dispatch_webhook("orders", evt) is True
    assert should_dispatch_webhook("billing", evt) is False
'''
    }

    t2020_hidden = {
        "tests/test_scope_hidden.py": '''from webhook import WebhookEvent
from scope_checker import should_dispatch_webhook
from prefix_validator import is_topic_subscribed

def test_scope_taught_boundaries():
    evt_sibling = WebhookEvent("orders_admin/reindex", "{}")
    assert should_dispatch_webhook("orders", evt_sibling) is False
    
    evt_exact = WebhookEvent("orders", "{}")
    assert should_dispatch_webhook("orders/", evt_exact) is True

def test_prefix_validator_direct():
    assert is_topic_subscribed("orders", "orders_admin") is False
    assert is_topic_subscribed("orders/", "orders") is True
'''
    }

    t2020_ref = {
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    pat = "/" + subscribed_pattern.strip("/")
    topic = "/" + event_topic.strip("/")
    if topic == pat:
        return True
    return topic.startswith(pat + "/")

def clean_topic_segment(topic: str) -> str:
    return topic.strip().lower()
'''
    }

    t2020_m1 = {
        "scope_checker.py": '''"""Webhook scope dispatch checker."""
from prefix_validator import is_topic_subscribed
from webhook import WebhookEvent

def should_dispatch_webhook(subscribed_topic: str, event: WebhookEvent) -> bool:
    p = "/" + subscribed_topic.strip("/")
    t = "/" + event.topic_path.strip("/")
    if t != p and not t.startswith(p + "/"):
        return False
    return is_topic_subscribed(subscribed_topic, event.topic_path)

def filter_dispatch_queue(subscribed_topic: str, events: list) -> list:
    return [e for e in events if should_dispatch_webhook(subscribed_topic, e)]
'''
    }

    t2020_m2 = {
        "prefix_validator.py": '''"""Topic path subscription matcher."""
def is_topic_subscribed(subscribed_pattern: str, event_topic: str) -> bool:
    return subscribed_pattern.strip("/") == event_topic.strip("/")

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
        traceback_text="FAILED tests/test_scope_hidden.py::test_scope_taught_boundaries - AssertionError: Topic leak at scope_checker.py:9: unsegmented prefix match dispatched unauthorized administrative topic",
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
            ("test_scope_taught_boundaries", "HANDBOOK.md Rule H06: Trailing slash and path prefix normalization", "No", "TAUGHT"),
            ("test_prefix_validator_direct", "HANDBOOK.md Rule H06: Trailing slash and path prefix normalization", "No", "TAUGHT")
        ]
    )

    print("Family 5 registered (Tasks 2017-2020).")
