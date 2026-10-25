"""Expansion tasks for Round 18 (Tasks 2085-2106, K3).

Expands task suite by 22 tasks:
- 18 Held-Out TAUGHT tasks (2085-2102)
- 4 Tune TAUGHT tasks (2103-2106)
"""

import sys, os
from typing import Dict, List, Any

EXPANSION_TASKS = []

def make_task(
    tid: int,
    name: str,
    family: str,
    class_tag: str,
    split: str,
    issue: str,
    failing_excerpt: str,
    root_cause_file: str,
    repo_files: Dict[str, str],
    visible_tests: Dict[str, str],
    hidden_tests: Dict[str, str],
    gold_patch: str,
    mutant1_patch: str,
    mutant2_patch: str,
    hrc: bool = True,
    vts: bool = False,
) -> Dict[str, Any]:
    full_repo = dict(repo_files)
    for p, c in visible_tests.items():
        full_repo[p] = c
    
    vis_paths = list(visible_tests.keys())
    
    key = {
        "visible_paths": vis_paths,
        "protected": vis_paths,
        "must_touch": [root_cause_file],
        "variants": [
            {
                "name": "hidden tests",
                "expect": "pass",
                "overlay": hidden_tests,
                "paths": list(hidden_tests.keys()),
            }
        ]
    }
    
    return {
        "id": tid,
        "name": name,
        "family": family,
        "class_tag": class_tag,
        "split": split,
        "hidden_root_cause": hrc,
        "visible_test_sensitive": vts,
        "issue": issue,
        "failing_traceback_excerpt": failing_excerpt,
        "root_cause_file": root_cause_file,
        "repo": full_repo,
        "visible_tests": visible_tests,
        "hidden_tests": hidden_tests,
        "gold_patch": gold_patch,
        "mutant_1_patch": mutant1_patch,
        "mutant_2_patch": mutant2_patch,
        "key": key,
    }

# ==============================================================================
# FAMILY 8: service_errors (H04)
# Tasks 2085, 2086, 2087 (Held-Out), 2103 (Tune)
# ==============================================================================

_ERRORS_COMMON = '''"""Service exception definitions for microservice error propagation."""

class ServiceError(Exception):
    """Base domain exception carrying machine-readable error codes."""
    def __init__(self, code: str, message: str, details: dict = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

def format_error_response(exc: ServiceError) -> dict:
    """Format service exception as JSON wire dictionary."""
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        }
    }
'''

# Task 2085: Database Transaction Lock Manager
_2085_RECORD = '''"""Lock metadata and conflict tracking."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TxLockEntry:
    tx_id: str
    resource: str
    granted: bool

def inspect_lock_conflict(active_tx: Optional[str], requested_tx: str) -> bool:
    """Determine if active lock holder conflicts with incoming request."""
    if active_tx is None:
        return False
    return active_tx != requested_tx

def describe_lock_state(resource: str, tx_id: Optional[str]) -> str:
    """Generate human-readable audit string for lock registry."""
    if tx_id is None:
        return f"Resource {resource} is available"
    return f"Resource {resource} locked by {tx_id}"
'''

_2085_BASE = '''"""Transaction lock orchestrator."""
from errors import ServiceError, format_error_response
from tx_record import TxLockEntry, inspect_lock_conflict, describe_lock_state
from typing import Dict, Optional

class TxLockManager:
    """Manage in-memory transactional resource locks."""
    def __init__(self):
        self._locks: Dict[str, str] = {}

    def acquire_lock(self, resource: str, tx_id: str) -> TxLockEntry:
        active = self._locks.get(resource)
        if inspect_lock_conflict(active, tx_id):
            raise ServiceError("LOCK_CONFLICT", f"Resource '{resource}' is locked by transaction '{active}'")
        self._locks[resource] = tx_id
        return TxLockEntry(tx_id=tx_id, resource=resource, granted=True)

    def release_lock(self, resource: str, tx_id: str) -> None:
        if self._locks.get(resource) == tx_id:
            del self._locks[resource]

    def status(self, resource: str) -> str:
        return describe_lock_state(resource, self._locks.get(resource))
'''

_2085_GOLD = '''=== FILE: tx_manager.py ===
"""Transaction lock orchestrator."""
from errors import ServiceError, format_error_response
from tx_record import TxLockEntry, inspect_lock_conflict, describe_lock_state
from typing import Dict, Optional

class TxLockManager:
    """Manage in-memory transactional resource locks."""
    def __init__(self):
        self._locks: Dict[str, str] = {}

    def acquire_lock(self, resource: str, tx_id: str) -> TxLockEntry:
        active = self._locks.get(resource)
        if inspect_lock_conflict(active, tx_id):
            raise ServiceError("ERR_RESOURCE_LOCKED", f"Resource '{resource}' is locked by transaction '{active}'")
        self._locks[resource] = tx_id
        return TxLockEntry(tx_id=tx_id, resource=resource, granted=True)

    def release_lock(self, resource: str, tx_id: str) -> None:
        if self._locks.get(resource) == tx_id:
            del self._locks[resource]

    def status(self, resource: str) -> str:
        return describe_lock_state(resource, self._locks.get(resource))
=== END ==='''

_2085_M1 = _2085_GOLD.replace("ERR_RESOURCE_LOCKED", "RESOURCE_BUSY")
_2085_M2 = _2085_GOLD.replace("ERR_RESOURCE_LOCKED", "ERR_CONCURRENT_MODIFICATION")

_2085_TEST_VIS = '''"""Visible test for lock manager."""
from tx_manager import TxLockManager
from errors import ServiceError
import pytest

def test_acquire_and_release():
    mgr = TxLockManager()
    entry = mgr.acquire_lock("table_orders", "tx_101")
    assert entry.granted is True
    mgr.release_lock("table_orders", "tx_101")
    entry2 = mgr.acquire_lock("table_orders", "tx_102")
    assert entry2.granted is True
'''

_2085_TEST_HID = '''"""Hidden test for transaction lock error code."""
from tx_manager import TxLockManager
from errors import ServiceError
import pytest

def test_service_execution():
    mgr = TxLockManager()
    mgr.acquire_lock("table_users", "tx_001")
    with pytest.raises(ServiceError) as exc_info:
        mgr.acquire_lock("table_users", "tx_002")
    assert exc_info.value.code == "ERR_RESOURCE_LOCKED"
'''

EXPANSION_TASKS.append(make_task(
    tid=2085,
    name="Database Transaction Lock Manager",
    family="service_errors",
    class_tag="TAUGHT",
    split="Held-Out",
    issue="Incident INC-8011: Transaction coordinator rejects concurrent lock acquisitions with non-standard error code.",
    failing_excerpt="""tests/test_lock_cases.py:12: in test_service_execution
>   assert exc_info.value.code == "ERR_RESOURCE_LOCKED"
E   AssertionError: assert 'LOCK_CONFLICT' == 'ERR_RESOURCE_LOCKED'""",
    root_cause_file="tx_manager.py",
    repo_files={
        "errors.py": _ERRORS_COMMON,
        "tx_record.py": _2085_RECORD,
        "tx_manager.py": _2085_BASE,
    },
    visible_tests={"tests/test_tx_lock.py": _2085_TEST_VIS},
    hidden_tests={"tests/test_lock_cases.py": _2085_TEST_HID},
    gold_patch=_2085_GOLD,
    mutant1_patch=_2085_M1,
    mutant2_patch=_2085_M2,
    hrc=False,
    vts=False,
))

# Task 2086: API Token Rate Limiter
_2086_COUNTER = '''"""Token bucket counter model."""
from dataclasses import dataclass
from typing import Dict

@dataclass
class BucketRecord:
    token: str
    remaining: int
    limit: int

def deduct_token_allowance(current: int, requested: int) -> int:
    """Compute new remaining token balance."""
    return current - requested

def is_allowance_exhausted(remaining: int, requested: int) -> bool:
    """Check if requested token consumption exceeds available allowance."""
    return remaining < requested
'''

_2086_BASE = '''"""Token rate limiter enforcement."""
from errors import ServiceError, format_error_response
from token_counter import BucketRecord, deduct_token_allowance, is_allowance_exhausted
from typing import Dict

class TokenRateLimiter:
    """Enforce per-client token consumption quotas."""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._tokens: Dict[str, int] = {}

    def consume(self, token: str, amount: int = 1) -> BucketRecord:
        rem = self._tokens.get(token, self.capacity)
        if is_allowance_exhausted(rem, amount):
            raise ServiceError("QUOTA_DEPLETED", f"Token '{token}' has exceeded allowance")
        new_bal = deduct_token_allowance(rem, amount)
        self._tokens[token] = new_bal
        return BucketRecord(token=token, remaining=new_bal, limit=self.capacity)

    def reset_quota(self, token: str) -> None:
        self._tokens[token] = self.capacity
'''

_2086_GOLD = '''=== FILE: rate_limiter.py ===
"""Token rate limiter enforcement."""
from errors import ServiceError, format_error_response
from token_counter import BucketRecord, deduct_token_allowance, is_allowance_exhausted
from typing import Dict

class TokenRateLimiter:
    """Enforce per-client token consumption quotas."""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._tokens: Dict[str, int] = {}

    def consume(self, token: str, amount: int = 1) -> BucketRecord:
        rem = self._tokens.get(token, self.capacity)
        if is_allowance_exhausted(rem, amount):
            raise ServiceError("ERR_RATE_LIMIT_EXCEEDED", f"Token '{token}' has exceeded allowance")
        new_bal = deduct_token_allowance(rem, amount)
        self._tokens[token] = new_bal
        return BucketRecord(token=token, remaining=new_bal, limit=self.capacity)

    def reset_quota(self, token: str) -> None:
        self._tokens[token] = self.capacity
=== END ==='''

_2086_M1 = _2086_GOLD.replace("ERR_RATE_LIMIT_EXCEEDED", "TOO_MANY_REQUESTS")
_2086_M2 = _2086_GOLD.replace("ERR_RATE_LIMIT_EXCEEDED", "ERR_QUOTA_EXCEEDED")

_2086_TEST_VIS = '''"""Visible test for token consumption."""
from rate_limiter import TokenRateLimiter
from errors import ServiceError
import pytest

def test_consume_success():
    limiter = TokenRateLimiter(50)
    rec = limiter.consume("client_alpha", 10)
    assert rec.remaining == 40
'''

_2086_TEST_HID = '''"""Hidden test for rate limit error code."""
from rate_limiter import TokenRateLimiter
from errors import ServiceError
import pytest

def test_service_execution():
    limiter = TokenRateLimiter(10)
    limiter.consume("client_beta", 10)
    with pytest.raises(ServiceError) as exc_info:
        limiter.consume("client_beta", 1)
    assert exc_info.value.code == "ERR_RATE_LIMIT_EXCEEDED"
'''

EXPANSION_TASKS.append(make_task(
    tid=2086,
    name="API Token Rate Limiter",
    family="service_errors",
    class_tag="TAUGHT",
    split="Held-Out",
    issue="Incident INC-8012: Rate limit depletion throws unrecognized error code in downstream microservices.",
    failing_excerpt="""tests/test_limiter_cases.py:12: in test_service_execution
>   assert exc_info.value.code == "ERR_RATE_LIMIT_EXCEEDED"
E   AssertionError: assert 'QUOTA_DEPLETED' == 'ERR_RATE_LIMIT_EXCEEDED'""",
    root_cause_file="rate_limiter.py",
    repo_files={
        "errors.py": _ERRORS_COMMON,
        "token_counter.py": _2086_COUNTER,
        "rate_limiter.py": _2086_BASE,
    },
    visible_tests={"tests/test_token_limiter.py": _2086_TEST_VIS},
    hidden_tests={"tests/test_limiter_cases.py": _2086_TEST_HID},
    gold_patch=_2086_GOLD,
    mutant1_patch=_2086_M1,
    mutant2_patch=_2086_M2,
    hrc=False,
    vts=False,
))

# Task 2087: Webhook Payload Validator
_2087_RULE = '''"""Payload verification rules."""
from typing import Dict, Any, List

def check_required_keys(payload: Dict[str, Any], required: List[str]) -> List[str]:
    """Verify required schema keys exist in incoming dictionary."""
    return [k for k in required if k not in payload]

def inspect_field_types(payload: Dict[str, Any], type_map: Dict[str, type]) -> List[str]:
    """Verify field values match expected python datatypes."""
    errors = []
    for k, expected_t in type_map.items():
        if k in payload and not isinstance(payload[k], expected_t):
            errors.append(k)
    return errors
'''

_2087_BASE = '''"""Webhook payload verification orchestrator."""
from errors import ServiceError, format_error_response
from schema_rules import check_required_keys, inspect_field_types
from typing import Dict, Any

class WebhookPayloadValidator:
    """Validate incoming webhook delivery payload structures."""
    REQUIRED_KEYS = ["event_id", "timestamp", "payload"]

    def validate(self, body: Dict[str, Any]) -> bool:
        missing = check_required_keys(body, self.REQUIRED_KEYS)
        if missing:
            raise ServiceError("BAD_PAYLOAD", f"Payload missing required keys: {missing}")
        return True

    def validate_schema(self, body: Dict[str, Any]) -> bool:
        return self.validate(body)
'''

_2087_GOLD = '''=== FILE: payload_validator.py ===
"""Webhook payload verification orchestrator."""
from errors import ServiceError, format_error_response
from schema_rules import check_required_keys, inspect_field_types
from typing import Dict, Any

class WebhookPayloadValidator:
    """Validate incoming webhook delivery payload structures."""
    REQUIRED_KEYS = ["event_id", "timestamp", "payload"]

    def validate(self, body: Dict[str, Any]) -> bool:
        missing = check_required_keys(body, self.REQUIRED_KEYS)
        if missing:
            raise ServiceError("ERR_VALIDATION_FAILED", f"Payload missing required keys: {missing}")
        return True

    def validate_schema(self, body: Dict[str, Any]) -> bool:
        return self.validate(body)
=== END ==='''

_2087_M1 = _2087_GOLD.replace("ERR_VALIDATION_FAILED", "INVALID_PAYLOAD")
_2087_M2 = _2087_GOLD.replace("ERR_VALIDATION_FAILED", "ERR_SCHEMA_MISMATCH")

_2087_TEST_VIS = '''"""Visible test for payload validation."""
from payload_validator import WebhookPayloadValidator
from errors import ServiceError
import pytest

def test_validate_success():
    v = WebhookPayloadValidator()
    assert v.validate({"event_id": "ev_1", "timestamp": 12345, "payload": {}}) is True
'''

_2087_TEST_HID = '''"""Hidden test for validation error code."""
from payload_validator import WebhookPayloadValidator
from errors import ServiceError
import pytest

def test_service_execution():
    v = WebhookPayloadValidator()
    with pytest.raises(ServiceError) as exc_info:
        v.validate({"event_id": "ev_1"})
    assert exc_info.value.code == "ERR_VALIDATION_FAILED"
'''

EXPANSION_TASKS.append(make_task(
    tid=2087,
    name="Webhook Payload Validator",
    family="service_errors",
    class_tag="TAUGHT",
    split="Held-Out",
    issue="Incident INC-8013: Webhook payload schema validation error code does not adhere to platform standard.",
    failing_excerpt="""tests/test_payload_cases.py:12: in test_service_execution
>   assert exc_info.value.code == "ERR_VALIDATION_FAILED"
E   AssertionError: assert 'BAD_PAYLOAD' == 'ERR_VALIDATION_FAILED'""",
    root_cause_file="payload_validator.py",
    repo_files={
        "errors.py": _ERRORS_COMMON,
        "schema_rules.py": _2087_RULE,
        "payload_validator.py": _2087_BASE,
    },
    visible_tests={"tests/test_validator.py": _2087_TEST_VIS},
    hidden_tests={"tests/test_payload_cases.py": _2087_TEST_HID},
    gold_patch=_2087_GOLD,
    mutant1_patch=_2087_M1,
    mutant2_patch=_2087_M2,
    hrc=False,
    vts=False,
))

# Task 2103: Resource Lease Lock Engine (Tune TAUGHT)
_2103_BASE = '''"""Distributed resource lease lock coordinator."""
from errors import ServiceError, format_error_response
from tx_record import TxLockEntry, inspect_lock_conflict, describe_lock_state
from typing import Dict

class LeaseLockEngine:
    """Manage distributed resource lease locks across nodes."""
    def __init__(self):
        self._leases: Dict[str, str] = {}

    def claim_lease(self, resource_id: str, client_id: str) -> TxLockEntry:
        cur = self._leases.get(resource_id)
        if inspect_lock_conflict(cur, client_id):
            raise ServiceError("LEASE_HELD", f"Lease for '{resource_id}' is held by '{cur}'")
        self._leases[resource_id] = client_id
        return TxLockEntry(tx_id=client_id, resource=resource_id, granted=True)

    def release_lease(self, resource_id: str, client_id: str) -> bool:
        if self._leases.get(resource_id) == client_id:
            del self._leases[resource_id]
            return True
        return False
'''

_2103_GOLD = '''=== FILE: lease_engine.py ===
"""Distributed resource lease lock coordinator."""
from errors import ServiceError, format_error_response
from tx_record import TxLockEntry, inspect_lock_conflict, describe_lock_state
from typing import Dict

class LeaseLockEngine:
    """Manage distributed resource lease locks across nodes."""
    def __init__(self):
        self._leases: Dict[str, str] = {}

    def claim_lease(self, resource_id: str, client_id: str) -> TxLockEntry:
        cur = self._leases.get(resource_id)
        if inspect_lock_conflict(cur, client_id):
            raise ServiceError("ERR_RESOURCE_LOCKED", f"Lease for '{resource_id}' is held by '{cur}'")
        self._leases[resource_id] = client_id
        return TxLockEntry(tx_id=client_id, resource=resource_id, granted=True)

    def release_lease(self, resource_id: str, client_id: str) -> bool:
        if self._leases.get(resource_id) == client_id:
            del self._leases[resource_id]
            return True
        return False
=== END ==='''

_2103_M1 = _2103_GOLD.replace("ERR_RESOURCE_LOCKED", "RESOURCE_LOCKED")
_2103_M2 = _2103_GOLD.replace("ERR_RESOURCE_LOCKED", "ERR_LOCK_CONFLICT")

_2103_TEST_VIS = '''"""Visible test for lease claiming."""
from lease_engine import LeaseLockEngine
from errors import ServiceError
import pytest

def test_claim_lease_ok():
    eng = LeaseLockEngine()
    entry = eng.claim_lease("res_disk_1", "node_a")
    assert entry.granted is True
'''

_2103_TEST_HID = '''"""Hidden test for lease error code."""
from lease_engine import LeaseLockEngine
from errors import ServiceError
import pytest

def test_service_execution():
    eng = LeaseLockEngine()
    eng.claim_lease("res_disk_2", "node_a")
    with pytest.raises(ServiceError) as exc_info:
        eng.claim_lease("res_disk_2", "node_b")
    assert exc_info.value.code == "ERR_RESOURCE_LOCKED"
'''

EXPANSION_TASKS.append(make_task(
    tid=2103,
    name="Resource Lease Lock Engine",
    family="service_errors",
    class_tag="TAUGHT",
    split="Tune",
    issue="Incident INC-8014: Lease manager emits non-compliant error string on concurrent claim contention.",
    failing_excerpt="""tests/test_lease_cases.py:12: in test_service_execution
>   assert exc_info.value.code == "ERR_RESOURCE_LOCKED"
E   AssertionError: assert 'LEASE_HELD' == 'ERR_RESOURCE_LOCKED'""",
    root_cause_file="lease_engine.py",
    repo_files={
        "errors.py": _ERRORS_COMMON,
        "tx_record.py": _2085_RECORD,
        "lease_engine.py": _2103_BASE,
    },
    visible_tests={"tests/test_lease.py": _2103_TEST_VIS},
    hidden_tests={"tests/test_lease_cases.py": _2103_TEST_HID},
    gold_patch=_2103_GOLD,
    mutant1_patch=_2103_M1,
    mutant2_patch=_2103_M2,
    hrc=False,
    vts=False,
))

# ==============================================================================
# FAMILY 9: wire_envelope (H08)
# Tasks 2088, 2089, 2090 (Held-Out), 2104 (Tune)
# ==============================================================================

_WIRE_HELPER = '''"""Shared wire envelope serializer and validator."""
from typing import Dict, Any

def build_envelope(src: str, ts: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap payload into standardized house wire envelope."""
    return {
        "_v": 2,
        "_ts": ts,
        "_src": src,
        "payload": payload,
    }

def is_valid_envelope(d: Dict[str, Any]) -> bool:
    """Verify message carries correct version 2 schema properties."""
    return d.get("_v") == 2 and "_ts" in d and "_src" in d and "payload" in d

def extract_envelope_version(d: Dict[str, Any]) -> int:
    return d.get("_v", 0)
'''

_NORMALIZER_HELPER = '''"""Key normalization helper."""
from typing import Dict, Any
import re

def normalize_dict_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert camelCase keys to snake_case dictionary keys."""
    res = {}
    for k, v in d.items():
        s = re.sub(r"(?<!^)(?=[A-Z])", "_", k).lower()
        res[s] = v
    return res

def count_keys(d: Dict[str, Any]) -> int:
    return len(d)
'''

def make_wire_task(tid: int, name: str, split: str, service_src: str, file_name: str, fn_name: str, vis_key: str, vis_val: Any, hid_in: dict, hid_out: dict):
    base_code = f'''"""{name} wire constructor."""
from key_normalizer import normalize_dict_keys, count_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_envelope_version
from typing import Dict, Any

def {fn_name}(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm_payload = normalize_dict_keys(data)
    return {{
        "_v": 1,
        "_ts": epoch_ms,
        "_src": "{service_src}",
        "payload": norm_payload,
    }}

def validate_and_emit(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    res = {fn_name}(data, epoch_ms)
    _ = count_keys(data)
    return res
'''
    gold_code = f'''=== FILE: {file_name} ===
"""{name} wire constructor."""
from key_normalizer import normalize_dict_keys, count_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_envelope_version
from typing import Dict, Any

def {fn_name}(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm_payload = normalize_dict_keys(data)
    return build_envelope("{service_src}", epoch_ms, norm_payload)

def validate_and_emit(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    res = {fn_name}(data, epoch_ms)
    _ = count_keys(data)
    return res
=== END ==='''

    m1_code = gold_code.replace(f'build_envelope("{service_src}", epoch_ms, norm_payload)', f'{{"_v": 1, "_ts": epoch_ms, "_src": "{service_src}", "payload": norm_payload}}')
    m2_code = gold_code.replace(f'build_envelope("{service_src}", epoch_ms, norm_payload)', f'build_envelope("{service_src}", epoch_ms, data)')

    vis_test = f'''"""Visible test for {name}."""
from {file_name[:-3]} import {fn_name}

def test_envelope_payload():
    res = {fn_name}({{"{vis_key}": "{vis_val}"}}, 1000)
    assert "payload" in res
'''

    hid_test = f'''"""Hidden test for {name} wire envelope."""
from {file_name[:-3]} import {fn_name}

def test_service_execution():
    res = {fn_name}({hid_in}, 1700000050)
    assert res.get("_v") == 2
    assert res.get("_src") == "{service_src}"
    assert res.get("_ts") == 1700000050
    assert res.get("payload") == {hid_out}
'''

    return make_task(
        tid=tid,
        name=name,
        family="wire_envelope",
        class_tag="TAUGHT",
        split=split,
        issue=f"Incident INC-{tid}: Service event stream rejected {name} message due to outdated wire envelope version.",
        failing_excerpt="""tests/test_wire_cases.py:6: in test_service_execution
>   assert res.get("_v") == 2
E   AssertionError: assert 1 == 2""",
        root_cause_file=file_name,
        repo_files={
            "wire_envelope.py": _WIRE_HELPER,
            "key_normalizer.py": _NORMALIZER_HELPER,
            file_name: base_code,
        },
        visible_tests={"tests/test_wire.py": vis_test},
        hidden_tests={"tests/test_wire_cases.py": hid_test},
        gold_patch=gold_code,
        mutant1_patch=m1_code,
        mutant2_patch=m2_code,
        hrc=False,
        vts=False,
    )

EXPANSION_TASKS.append(make_wire_task(2088, "Customer Notification Dispatcher", "Held-Out", "customer_service", "customer_dispatcher.py", "dispatch_customer_notice", "userId", "c1", {"customerId": "c99", "emailVerified": True}, {"customer_id": "c99", "email_verified": True}))
EXPANSION_TASKS.append(make_wire_task(2089, "Payment Confirmation Broadcaster", "Held-Out", "payment_service", "payment_broadcaster.py", "broadcast_payment_confirmation", "txId", "t1", {"chargeAmount": 500, "currencyCode": "USD"}, {"charge_amount": 500, "currency_code": "USD"}))
EXPANSION_TASKS.append(make_wire_task(2090, "Shipment Tracking Event Emitter", "Held-Out", "shipment_service", "shipment_emitter.py", "emit_shipment_event", "carrierId", "ups", {"trackingNumber": "1Z999", "deliveryStatus": "IN_TRANSIT"}, {"tracking_number": "1Z999", "delivery_status": "IN_TRANSIT"}))
EXPANSION_TASKS.append(make_wire_task(2104, "Invoice Notification Event Emitter", "Tune", "invoice_service", "invoice_emitter.py", "emit_invoice_event", "invoiceId", "inv_1", {"invoiceTotal": 9900, "taxDue": 800}, {"invoice_total": 9900, "tax_due": 800}))

_TIMESTAMP_MODEL = '''"""Data model for temporal event records."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TimestampRecord:
    event_name: str
    epoch_ms: int

def create_event_record(name: str, epoch_ms: int) -> TimestampRecord:
    """Instantiate event record with epoch millisecond timestamp."""
    return TimestampRecord(event_name=name, epoch_ms=epoch_ms)
'''

_IDEMP_MODEL = '''"""Idempotency token request wrapper."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class IdempotencyRequest:
    action: str
    amount: int

def wrap_request(action: str, amount: int) -> IdempotencyRequest:
    """Create structured request context for outbound RPC."""
    return IdempotencyRequest(action=action, amount=amount)
'''

_METRIC_MODEL = '''"""Telemetry sample measurement container."""
from dataclasses import dataclass
from typing import List

@dataclass
class MetricSampleWindow:
    series_name: str
    values: List[float]

def create_sample_window(name: str, values: List[float]) -> MetricSampleWindow:
    """Create named metric observation sample window."""
    return MetricSampleWindow(series_name=name, values=values)
'''

_TSV_MODEL = '''"""Structured record container for TSV exports."""
from dataclasses import dataclass

@dataclass
class AuditRecord:
    level: str
    message: str
    target: str

def create_record(level: str, msg: str, target: str) -> AuditRecord:
    """Construct audit record tuple for serialization."""
    return AuditRecord(level=level, message=msg, target=target)
'''

_SETTLEMENT_MODEL = '''"""Settlement rate specification."""
from dataclasses import dataclass

@dataclass
class SettlementParams:
    amount: str
    rate: str

def parse_params(amount: str, rate: str) -> SettlementParams:
    """Parse settlement computation inputs."""
    return SettlementParams(amount=amount, rate=rate)
'''



# ==============================================================================
# FAMILY 10: timestamp_iso (H09)
# Tasks 2091, 2092, 2093 (Held-Out)
# ==============================================================================

_ISO_HELPER = '''"""Timestamp format utility and validation."""
from datetime import datetime, timezone
import re
from typing import Optional

def parse_epoch_seconds(epoch_s: float) -> datetime:
    """Convert float seconds since epoch into timezone-aware UTC datetime."""
    return datetime.fromtimestamp(epoch_s, tz=timezone.utc)

def is_valid_iso_format(ts_str: str) -> bool:
    """Verify string adheres to YYYY-MM-DDTHH:MM:SS.mmmZ schema."""
    pat = r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$"
    return bool(re.match(pat, ts_str))

def extract_year_component(ts_str: str) -> int:
    """Extract 4-digit calendar year from formatted ISO string."""
    return int(ts_str[:4])

def extract_millis_component(ts_str: str) -> int:
    """Extract 3-digit millisecond fraction from formatted string."""
    try:
        parts = ts_str.split(".")
        if len(parts) > 1:
            return int(parts[1][:3])
        return 0
    except Exception:
        return 0

def format_epoch_millis(epoch_ms: int) -> str:
    """Format integer epoch milliseconds to UTC ISO string."""
    s = epoch_ms / 1000.0
    dt = parse_epoch_seconds(s)
    ms = int(dt.microsecond / 1000)
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{ms:03d}Z")
'''

def make_timestamp_task(tid: int, name: str, file_name: str, fn_name: str):
    base_code = f'''"""{name} utility."""
from datetime import datetime, timezone
from iso_helper import parse_epoch_seconds, is_valid_iso_format, extract_year_component
from timestamp_model import TimestampRecord, create_event_record

def {fn_name}(epoch_s: float) -> str:
    rec = create_event_record("{fn_name}", int(epoch_s))
    dt = parse_epoch_seconds(epoch_s)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def format_sequence(timestamps: list) -> list:
    return [{fn_name}(t) for t in timestamps]
'''
    gold_code = f'''=== FILE: {file_name} ===
"""{name} utility."""
from datetime import datetime, timezone
from iso_helper import parse_epoch_seconds, is_valid_iso_format, extract_year_component
from timestamp_model import TimestampRecord, create_event_record

def {fn_name}(epoch_s: float) -> str:
    rec = create_event_record("{fn_name}", int(epoch_s))
    dt = parse_epoch_seconds(epoch_s)
    ms = int(dt.microsecond / 1000)
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{{ms:03d}}Z")

def format_sequence(timestamps: list) -> list:
    return [{fn_name}(t) for t in timestamps]
=== END ==='''

    m1_code = gold_code.replace('dt.strftime(f"%Y-%m-%dT%H:%M:%S.{ms:03d}Z")', 'dt.isoformat()')
    m2_code = gold_code.replace('dt.strftime(f"%Y-%m-%dT%H:%M:%S.{ms:03d}Z")', 'dt.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")')

    vis_test = f'''"""Visible test for {name}."""
from {file_name[:-3]} import {fn_name}

def test_ts_basic():
    res = {fn_name}(1700000000.0)
    assert res.startswith("2023-11-14")
'''

    hid_test = f'''"""Hidden test for {name} millisecond ISO 8601."""
from {file_name[:-3]} import {fn_name}
from iso_helper import is_valid_iso_format

def test_service_execution():
    res = {fn_name}(1700000000.123456)
    assert res == "2023-11-14T22:13:20.123Z"
    assert is_valid_iso_format(res) is True
'''

    return make_task(
        tid=tid,
        name=name,
        family="timestamp_iso",
        class_tag="TAUGHT",
        split="Held-Out",
        issue=f"Incident INC-{tid}: Journal timestamps lack millisecond precision required by house ingestion standard.",
        failing_excerpt="""tests/test_ts_cases.py:8: in test_service_execution
>   assert res == "2023-11-14T22:13:20.123Z"
E   AssertionError: assert '2023-11-14T22:13:20Z' == '2023-11-14T22:13:20.123Z'""",
        root_cause_file=file_name,
        repo_files={
            "iso_helper.py": _ISO_HELPER,
            "timestamp_model.py": _TIMESTAMP_MODEL,
            file_name: base_code,
        },
        visible_tests={"tests/test_ts.py": vis_test},
        hidden_tests={"tests/test_ts_cases.py": hid_test},
        gold_patch=gold_code,
        mutant1_patch=m1_code,
        mutant2_patch=m2_code,
        hrc=False,
        vts=False,
    )

EXPANSION_TASKS.append(make_timestamp_task(2091, "Session Activity Timestamp Formatter", "session_formatter.py", "format_session_timestamp"))
EXPANSION_TASKS.append(make_timestamp_task(2092, "Audit Trail Event Time Normalizer", "audit_normalizer.py", "normalize_audit_timestamp"))
EXPANSION_TASKS.append(make_timestamp_task(2093, "Telemetry Metric Ingest Formatter", "metric_formatter.py", "format_metric_timestamp"))

# ==============================================================================
# FAMILY 12: idempotency_keys (H13)
# Tasks 2094, 2095, 2096 (Held-Out), 2105 (Tune)
# ==============================================================================

_IDEMP_HELPER = '''"""Idempotency header validation helper."""
import uuid
from typing import Optional, Dict

def is_valid_uuid4(val: str) -> bool:
    """Verify string is valid UUID version 4."""
    try:
        u = uuid.UUID(val, version=4)
        return str(u) == val
    except Exception:
        return False

def sanitize_header_value(val: str) -> str:
    """Strip extraneous whitespace from incoming header values."""
    return val.strip()

def extract_idempotency_key(headers: Dict[str, str]) -> Optional[str]:
    """Retrieve idempotency header value supporting case-insensitive lookup."""
    for k, v in headers.items():
        if k.lower() == "idempotency-key":
            return sanitize_header_value(v)
    return None

def build_auth_bearer(token: str) -> str:
    """Format bearer authentication header string."""
    return f"Bearer {token.strip()}"

def extract_trace_context(headers: Dict[str, str]) -> Optional[str]:
    """Retrieve trace parent identifier from request headers."""
    for k, v in headers.items():
        if k.lower() in ("x-trace-id", "traceparent"):
            return sanitize_header_value(v)
    return None
'''

def make_idemp_task(tid: int, name: str, split: str, file_name: str, fn_name: str, extra_header_k: str, extra_header_v: str):
    base_code = f'''"""{name} RPC client header constructor."""
from typing import Dict
from idemp_helper import is_valid_uuid4, sanitize_header_value
from idemp_model import wrap_request

def {fn_name}(entity_id: str) -> Dict[str, str]:
    req = wrap_request("{fn_name}", 1)
    return {{
        "Content-Type": "application/json",
        "{extra_header_k}": sanitize_header_value(entity_id),
    }}

def build_client_request(entity_id: str) -> Dict[str, str]:
    return {fn_name}(entity_id)
'''

    gold_code = f'''=== FILE: {file_name} ===
"""{name} RPC client header constructor."""
from typing import Dict
from idemp_helper import is_valid_uuid4, sanitize_header_value
from idemp_model import wrap_request
import uuid

def {fn_name}(entity_id: str) -> Dict[str, str]:
    req = wrap_request("{fn_name}", 1)
    return {{
        "Content-Type": "application/json",
        "{extra_header_k}": sanitize_header_value(entity_id),
        "Idempotency-Key": str(uuid.uuid4()),
    }}

def build_client_request(entity_id: str) -> Dict[str, str]:
    return {fn_name}(entity_id)
=== END ==='''

    m1_code = gold_code.replace('"Idempotency-Key": str(uuid.uuid4())', '"X-Idempotency-Key": "fixed_token"')
    m2_code = gold_code.replace('str(uuid.uuid4())', '"not_a_valid_uuid"')

    vis_test = f'''"""Visible test for {name}."""
from {file_name[:-3]} import {fn_name}

def test_headers():
    h = {fn_name}("ent_1")
    assert h["Content-Type"] == "application/json"
'''

    hid_test = f'''"""Hidden test for {name} idempotency key."""
from {file_name[:-3]} import {fn_name}
from idemp_helper import is_valid_uuid4

def test_service_execution():
    h = {fn_name}("ent_2")
    assert "Idempotency-Key" in h
    assert is_valid_uuid4(h["Idempotency-Key"]) is True
'''

    return make_task(
        tid=tid,
        name=name,
        family="idempotency_keys",
        class_tag="TAUGHT",
        split=split,
        issue=f"Incident INC-{tid}: RPC request dropped by gateway due to missing standard idempotency header.",
        failing_excerpt="""tests/test_idemp_cases.py:8: in test_service_execution
>   assert "Idempotency-Key" in h
E   AssertionError: assert 'Idempotency-Key' in {'Content-Type': 'application/json'}""",
        root_cause_file=file_name,
        repo_files={
            "idemp_helper.py": _IDEMP_HELPER,
            "idemp_model.py": _IDEMP_MODEL,
            file_name: base_code,
        },
        visible_tests={"tests/test_idemp.py": vis_test},
        hidden_tests={"tests/test_idemp_cases.py": hid_test},
        gold_patch=gold_code,
        mutant1_patch=m1_code,
        mutant2_patch=m2_code,
        hrc=False,
        vts=False,
    )

EXPANSION_TASKS.append(make_idemp_task(2094, "Subscription Renewal Payment RPC", "Held-Out", "renewal_client.py", "build_renewal_headers", "X-Account-Id", "acc_101"))
EXPANSION_TASKS.append(make_idemp_task(2095, "Account Balance Settlement Client", "Held-Out", "balance_client.py", "build_balance_headers", "X-Account-Id", "acc_202"))
EXPANSION_TASKS.append(make_idemp_task(2096, "Order Cancellation Dispatcher", "Held-Out", "cancel_dispatcher.py", "build_cancel_headers", "X-Order-Id", "ord_303"))
EXPANSION_TASKS.append(make_idemp_task(2105, "Fund Disbursement RPC Client", "Tune", "disbursement_client.py", "build_disbursement_headers", "X-Batch-Id", "batch_404"))

# ==============================================================================
# FAMILY 13: metric_percentiles (H14)
# Tasks 2097, 2098, 2099 (Held-Out), 2106 (Tune)
# ==============================================================================

_PERCENTILE_HELPER = '''"""Percentile calculation validation helper."""
import math
from typing import List

def validate_metric_samples(samples: List[float]) -> List[float]:
    """Validate and sort numeric telemetry samples."""
    if not samples:
        raise ValueError("Samples list cannot be empty")
    return sorted(samples)

def sample_range(samples: List[float]) -> float:
    """Calculate absolute difference between maximum and minimum sample."""
    s = validate_metric_samples(samples)
    return s[-1] - s[0]

def sample_median(samples: List[float]) -> float:
    """Calculate sample median value for sorted series."""
    s = validate_metric_samples(samples)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0

def filter_non_finite(samples: List[float]) -> List[float]:
    """Filter out infinite or NaN values from telemetry stream."""
    return [x for x in samples if math.isfinite(x)]

def calculate_dispersion_ratio(samples: List[float]) -> float:
    """Calculate ratio of sample range to sample median."""
    m = sample_median(samples)
    if abs(m) < 1e-9:
        return 0.0
    return sample_range(samples) / m
'''

def make_percentile_task(tid: int, name: str, split: str, file_name: str, fn_name: str):
    base_code = f'''"""{name} percentile calculator."""
from typing import List
from percentile_helper import validate_metric_samples, sample_range
from metric_model import create_sample_window
import math

def {fn_name}(samples: List[float], p: float) -> float:
    win = create_sample_window("{fn_name}", samples)
    s = validate_metric_samples(win.values)
    idx = (p / 100.0) * (len(s) - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    if low == high:
        return s[low]
    return s[low] + (idx - low) * (s[high] - s[low])

def compute_summary_range(samples: List[float]) -> float:
    return sample_range(samples)
'''

    gold_code = f'''=== FILE: {file_name} ===
"""{name} percentile calculator."""
from typing import List
from percentile_helper import validate_metric_samples, sample_range
from metric_model import create_sample_window
import math

def {fn_name}(samples: List[float], p: float) -> float:
    win = create_sample_window("{fn_name}", samples)
    s = validate_metric_samples(win.values)
    idx = math.ceil((p / 100.0) * len(s)) - 1
    return s[idx]

def compute_summary_range(samples: List[float]) -> float:
    return sample_range(samples)
=== END ==='''

    m1_code = gold_code.replace('math.ceil((p / 100.0) * len(s)) - 1', 'int((p / 100.0) * len(s))')
    m2_code = gold_code.replace('math.ceil((p / 100.0) * len(s)) - 1', 'int((p / 100.0) * (len(s) - 1))')

    vis_test = f'''"""Visible test for {name}."""
from {file_name[:-3]} import {fn_name}

def test_perc():
    res = {fn_name}([10.0, 20.0, 30.0], 100.0)
    assert res == 30.0
'''

    hid_test = f'''"""Hidden test for {name} calculation."""
from {file_name[:-3]} import {fn_name}

def test_service_execution():
    d1 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    assert {fn_name}(d1, 50.0) == 40.0
    d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    assert {fn_name}(d2, 70.0) == 50.0
'''

    return make_task(
        tid=tid,
        name=name,
        family="metric_percentiles",
        class_tag="TAUGHT",
        split=split,
        issue=f"Incident INC-{tid}: Metric calculation discrepancy against nearest-rank house standard.",
        failing_excerpt=f"""tests/test_perc_cases.py:6: in test_service_execution
>   assert {fn_name}(d1, 50.0) == 40.0
E   AssertionError: assert 45.0 == 40.0""",
        root_cause_file=file_name,
        repo_files={
            "percentile_helper.py": _PERCENTILE_HELPER,
            "metric_model.py": _METRIC_MODEL,
            file_name: base_code,
        },
        visible_tests={"tests/test_perc.py": vis_test},
        hidden_tests={"tests/test_perc_cases.py": hid_test},
        gold_patch=gold_code,
        mutant1_patch=m1_code,
        mutant2_patch=m2_code,
        hrc=False,
        vts=False,
    )

EXPANSION_TASKS.append(make_percentile_task(2097, "API Endpoint Response Time Evaluator", "Held-Out", "endpoint_evaluator.py", "calculate_endpoint_percentile"))
EXPANSION_TASKS.append(make_percentile_task(2098, "Worker Job Execution Duration Analyzer", "Held-Out", "duration_analyzer.py", "compute_duration_percentile"))
EXPANSION_TASKS.append(make_percentile_task(2099, "Database Write Latency Calculator", "Held-Out", "write_latency.py", "calculate_write_percentile"))
EXPANSION_TASKS.append(make_percentile_task(2106, "Cache Hit Latency Percentile Monitor", "Tune", "cache_monitor.py", "calculate_cache_percentile"))

# ==============================================================================
# FAMILY 4: csv_roundtrip (H10)
# Tasks 2100, 2101 (Held-Out)
# ==============================================================================

_TSV_HELPER = '''"""TSV serialization validation utility."""
from typing import List, Dict

def parse_tsv_line(line: str) -> List[str]:
    """Split raw tab-delimited record into field tokens."""
    return line.split("\\t")

def count_tsv_fields(line: str) -> int:
    """Count number of tab-delimited columns in row."""
    return len(parse_tsv_line(line))

def join_tsv_fields(fields: List[str]) -> str:
    """Join list of string fields using single tab delimiter."""
    return "\\t".join(fields)

def validate_tsv_columns(line: str, expected_cols: int) -> bool:
    """Verify line conforms to expected column count."""
    return count_tsv_fields(line) == expected_cols

def escape_tsv_cell(val: str) -> str:
    """Escape control characters for safe single-cell embedding."""
    return val.replace("\\r", "\\\\r")

def sanitize_tsv_record(line: str) -> str:
    """Trim trailing newline or carriage return from line."""
    return line.rstrip("\\r\\n")

def is_comment_line(line: str) -> bool:
    """Check if row begins with comment prefix hash."""
    return line.startswith("#")
'''

def make_tsv_task(tid: int, name: str, file_name: str, fn_name: str):
    base_code = f'''"""{name} TSV line serializer."""
from typing import List
from tsv_helper import parse_tsv_line, count_tsv_fields
from tsv_model import create_record

def {fn_name}(level: str, msg: str, target: str) -> str:
    rec = create_record(level, msg, target)
    doubled = rec.message.replace('"', '""')
    if '"' in rec.message or '\\t' in rec.message:
        esc_msg = '"' + doubled + '"'
    else:
        esc_msg = rec.message
    return f"{{rec.level}}\\t{{esc_msg}}\\t{{rec.target}}"

def validate_line(line: str) -> bool:
    return count_tsv_fields(line) == 3
'''

    gold_code = f'''=== FILE: {file_name} ===
"""{name} TSV line serializer."""
from typing import List
from tsv_helper import parse_tsv_line, count_tsv_fields
from tsv_model import create_record

def {fn_name}(level: str, msg: str, target: str) -> str:
    rec = create_record(level, msg, target)
    esc_msg = str(rec.message).replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34)).replace(chr(9), chr(92)+'t')
    return f"{{rec.level}}\\t{{esc_msg}}\\t{{rec.target}}"

def validate_line(line: str) -> bool:
    return count_tsv_fields(line) == 3
=== END ==='''

    m1_code = gold_code.replace(".replace(chr(34), chr(92)+chr(34))", "")
    m2_code = gold_code.replace("replace(chr(9), chr(92)+'t')", "replace(chr(9), ' ')")

    vis_test = f'''"""Visible test for {name}."""
from {file_name[:-3]} import {fn_name}

def test_tsv():
    res = {fn_name}("OK", "regular message", "mod1")
    assert res == "OK\\tregular message\\tmod1"
'''

    hid_test = f'''"""Hidden test for {name} TSV backslash escaping."""
from {file_name[:-3]} import {fn_name}

def test_service_execution():
    res = {fn_name}("ALERT", 'msg with "quotes" and \\t tabs', "sys")
    expected = "ALERT\\tmsg with " + chr(92) + '"quotes' + chr(92) + '" and ' + chr(92) + 't tabs\\tsys'
    assert res == expected
'''

    return make_task(
        tid=tid,
        name=name,
        family="csv_roundtrip",
        class_tag="TAUGHT",
        split="Held-Out",
        issue=f"Incident INC-{tid}: TSV ingestion failed due to unexpected RFC 4180 quote wrapping.",
        failing_excerpt="""tests/test_tsv_cases.py:8: in test_service_execution
>   assert res == expected
E   AssertionError: assert 'ALERT\\t"msg with ""quotes"" and \\t tabs"\\tsys' == 'ALERT\\tmsg with \\"quotes\\" and \\\\t tabs\\tsys'""",
        root_cause_file=file_name,
        repo_files={
            "tsv_helper.py": _TSV_HELPER,
            "tsv_model.py": _TSV_MODEL,
            file_name: base_code,
        },
        visible_tests={"tests/test_tsv.py": vis_test},
        hidden_tests={"tests/test_tsv_cases.py": hid_test},
        gold_patch=gold_code,
        mutant1_patch=m1_code,
        mutant2_patch=m2_code,
        hrc=False,
        vts=False,
    )

EXPANSION_TASKS.append(make_tsv_task(2100, "Transaction Ledger TSV Exporter", "ledger_exporter.py", "serialize_ledger_record"))
EXPANSION_TASKS.append(make_tsv_task(2101, "System Log TSV Serializer", "log_serializer.py", "serialize_log_line"))

# ==============================================================================
# FAMILY 1: money_rounding (H02)
# Task 2102 (Held-Out TAUGHT)
# ==============================================================================

_MONEY_HELPER = '''"""Currency fee validation and rounding support."""
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from typing import Tuple

def to_cents(d: Decimal) -> Decimal:
    """Quantize decimal value to 2 fractional digits."""
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def is_positive_amount(d: Decimal) -> bool:
    """Verify monetary quantity is non-negative."""
    return d >= Decimal("0.00")

def split_dollars_cents(d: Decimal) -> Tuple[int, int]:
    """Decompose decimal amount into whole dollars and remaining cents."""
    cents_total = int(to_cents(d) * 100)
    dollars = cents_total // 100
    cents = cents_total % 100
    return dollars, cents

def format_cents_display(d: Decimal) -> str:
    """Format decimal amount with leading dollar currency sign."""
    return f"${to_cents(d):.2f}"

def is_valid_currency_iso(code: str) -> bool:
    """Check if 3-letter currency code is valid uppercase ISO 4217."""
    return len(code) == 3 and code.isalpha() and code.isupper()
'''

_2102_BASE = '''"""Merchant settlement fee calculator."""
from decimal import Decimal, ROUND_HALF_EVEN
from money_helper import to_cents, is_positive_amount
from settlement_model import parse_params

def calculate_settlement_fee(amount_str: str, rate_str: str) -> str:
    params = parse_params(amount_str, rate_str)
    amt = Decimal(params.amount)
    rate = Decimal(params.rate)
    raw_fee = amt * rate
    fee_cents = raw_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    return str(fee_cents)

def validate_and_compute(amount_str: str, rate_str: str) -> str:
    amt = Decimal(amount_str)
    if not is_positive_amount(amt):
        raise ValueError("Amount must be positive")
    return calculate_settlement_fee(amount_str, rate_str)
'''

_2102_GOLD = '''=== FILE: settlement_calculator.py ===
"""Merchant settlement fee calculator."""
from decimal import Decimal, ROUND_HALF_UP
from money_helper import to_cents, is_positive_amount
from settlement_model import parse_params

def calculate_settlement_fee(amount_str: str, rate_str: str) -> str:
    params = parse_params(amount_str, rate_str)
    amt = Decimal(params.amount)
    rate = Decimal(params.rate)
    raw_fee = amt * rate
    fee_cents = raw_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(fee_cents)

def validate_and_compute(amount_str: str, rate_str: str) -> str:
    amt = Decimal(amount_str)
    if not is_positive_amount(amt):
        raise ValueError("Amount must be positive")
    return calculate_settlement_fee(amount_str, rate_str)
=== END ==='''

_2102_M1 = _2102_GOLD.replace("ROUND_HALF_UP", "ROUND_DOWN")
_2102_M2 = _2102_GOLD.replace("ROUND_HALF_UP", "ROUND_CEILING")

_2102_TEST_VIS = '''"""Visible test for settlement fee calculator."""
from settlement_calculator import calculate_settlement_fee

def test_settlement_fee_basic():
    res = calculate_settlement_fee("100.00", "0.02")
    assert res == "2.00"
'''

_2102_TEST_HID = '''"""Hidden test for settlement rounding."""
from settlement_calculator import calculate_settlement_fee

def test_service_execution():
    res1 = calculate_settlement_fee("2.50", "0.05")
    assert res1 == "0.13"
    res2 = calculate_settlement_fee("2.42", "0.05")
    assert res2 == "0.12"
'''

EXPANSION_TASKS.append(make_task(
    tid=2102,
    name="Merchant Settlement Fee Calculator",
    family="money_rounding",
    class_tag="TAUGHT",
    split="Held-Out",
    issue="Incident INC-8071: Merchant settlement ledger mismatch due to fractional cent calculation discrepancy.",
    failing_excerpt="""tests/test_settle_cases.py:8: in test_service_execution
>   assert res == "0.13"
E   AssertionError: assert '0.12' == '0.13'""",
    root_cause_file="settlement_calculator.py",
    repo_files={
        "money_helper.py": _MONEY_HELPER,
        "settlement_model.py": _SETTLEMENT_MODEL,
        "settlement_calculator.py": _2102_BASE,
    },
    visible_tests={"tests/test_settle.py": _2102_TEST_VIS},
    hidden_tests={"tests/test_settle_cases.py": _2102_TEST_HID},
    gold_patch=_2102_GOLD,
    mutant1_patch=_2102_M1,
    mutant2_patch=_2102_M2,
    hrc=False,
    vts=False,
))
