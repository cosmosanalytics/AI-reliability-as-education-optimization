"""Family 8: service_errors (Tasks 2029 - 2036).

Governing Rule: Rule H04 (Structured Service Exception Hierarchy: raise ServiceError(code="ERR_<CATEGORY>_<DETAIL>", message="...") defined in errors.py. Never raise generic ValueError, KeyError, or raw Exception.)
Standard Error Codes:
- "ERR_AUTH_SCOPE_DENIED"
- "ERR_PAYLOAD_SCHEMA_INVALID"
- "ERR_RESOURCE_LOCKED"
- "ERR_RATE_LIMIT_EXCEEDED"

Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_8(add_task):
    # =========================================================================
    # Task 2029: Auth Scope Access Validator (STATED)
    # =========================================================================
    t2029_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "auth_context.py": '''"""Authorization context and token records."""
from dataclasses import dataclass, field
from typing import Set, Dict, Any

@dataclass
class AuthContext:
    user_id: str
    scopes: Set[str] = field(default_factory=set)
    is_active: bool = True

    def has_scope(self, scope: str) -> bool:
        return self.is_active and scope in self.scopes

    def add_scope(self, scope: str) -> None:
        self.scopes.add(scope)

    def to_dict(self) -> Dict[str, Any]:
        return {"user_id": self.user_id, "scopes": list(self.scopes), "is_active": self.is_active}
''',
        "auth_service.py": '''"""Authentication and permission verification service."""
from errors import ServiceError
from auth_context import AuthContext

def check_permission(context: AuthContext, required_scope: str) -> bool:
    """Check if caller possesses the required scope.
    
    If required scope is missing, raise ServiceError(code='ERR_AUTH_SCOPE_DENIED', message='Access scope denied').
    """
    if not context.has_scope(required_scope):
        return False
    return True

def execute_user_action(context: AuthContext, action_scope: str) -> str:
    check_permission(context, action_scope)
    return "SUCCESS"
''',
        "tests/test_auth_service.py": '''from auth_context import AuthContext
from auth_service import check_permission, execute_user_action

def test_nominal_execution():
    ctx = AuthContext(user_id="u1", scopes={"read:users"})
    assert check_permission(ctx, "read:users") is True
    assert execute_user_action(ctx, "read:users") == "SUCCESS"
'''
    }

    t2029_hidden = {
        "tests/test_auth_cases.py": '''from errors import ServiceError
from auth_context import AuthContext
from auth_service import check_permission

def test_service_execution():
    ctx = AuthContext(user_id="u3", scopes={"read"})
    err_raised = False
    err_code = ""
    try:
        check_permission(ctx, "admin:write")
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_AUTH_SCOPE_DENIED"
'''
    }

    t2029_ref = {
        "auth_service.py": '''"""Authentication and permission verification service."""
from errors import ServiceError
from auth_context import AuthContext

def check_permission(context: AuthContext, required_scope: str) -> bool:
    """Check if caller possesses the required scope.
    
    If required scope is missing, raise ServiceError(code='ERR_AUTH_SCOPE_DENIED', message='Access scope denied').
    """
    if not context.has_scope(required_scope):
        raise ServiceError(code="ERR_AUTH_SCOPE_DENIED", message="Access scope denied")
    return True

def execute_user_action(context: AuthContext, action_scope: str) -> str:
    check_permission(context, action_scope)
    return "SUCCESS"
'''
    }

    t2029_m1 = {
        "auth_service.py": '''"""Authentication and permission verification service."""
from errors import ServiceError
from auth_context import AuthContext

def check_permission(context: AuthContext, required_scope: str) -> bool:
    if not context.has_scope(required_scope):
        raise ValueError("Access scope denied")
    return True

def execute_user_action(context: AuthContext, action_scope: str) -> str:
    check_permission(context, action_scope)
    return "SUCCESS"
'''
    }

    t2029_m2 = {
        "auth_service.py": '''"""Authentication and permission verification service."""
from errors import ServiceError
from auth_context import AuthContext

def check_permission(context: AuthContext, required_scope: str) -> bool:
    if not context.has_scope(required_scope):
        raise ServiceError(code="ERR_AUTH_FAILED", message="Access scope denied")
    return True

def execute_user_action(context: AuthContext, action_scope: str) -> str:
    check_permission(context, action_scope)
    return "SUCCESS"
'''
    }

    add_task(
        tid=2029,
        family="service_errors",
        name="Auth Scope Access Validator",
        class_tag="STATED",
        issue="Security audit SEC-901: Service returned unhandled status instead of raising required service exception on scope denial.",
        traceback_text="FAILED tests/test_auth_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["auth_service.py"],
        repo=t2029_repo,
        hidden=t2029_hidden,
        ref=t2029_ref,
        mutant1=t2029_m1,
        mutant2=t2029_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "auth_service.py docstring: 'raise ServiceError(code=\"ERR_AUTH_SCOPE_DENIED\", ...)'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2030: Tenant Scope Authorization Guard (TAUGHT)
    # =========================================================================
    t2030_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "tenant_context.py": '''"""Tenant identity and permission records."""
from dataclasses import dataclass, field
from typing import Set, Dict, Any

@dataclass
class TenantContext:
    tenant_id: str
    tenant_name: str = ""
    allowed_scopes: Set[str] = field(default_factory=set)
    is_active: bool = True

    def permits(self, scope: str) -> bool:
        return self.is_active and scope in self.allowed_scopes

    def add_scope(self, scope: str) -> None:
        self.allowed_scopes.add(scope)

    def to_dict(self) -> Dict[str, Any]:
        return {"tenant_id": self.tenant_id, "tenant_name": self.tenant_name, "is_active": self.is_active}
''',
        "tenant_guard.py": '''"""Tenant permission authorization guard."""
from errors import ServiceError
from tenant_context import TenantContext

def authorize_tenant_action(ctx: TenantContext, required_scope: str) -> bool:
    """Authorize tenant action against target resource.
    
    Raises an error if tenant lacks required scope.
    """
    if not ctx.permits(required_scope):
        raise ValueError(f"Scope {required_scope} denied for tenant {ctx.tenant_id}")
    return True

def dispatch_tenant_request(ctx: TenantContext, required_scope: str) -> str:
    authorize_tenant_action(ctx, required_scope)
    return "DISPATCHED"
''',
        "tests/test_tenant_guard.py": '''from tenant_context import TenantContext
from tenant_guard import authorize_tenant_action, dispatch_tenant_request

def test_nominal_tenant_dispatch():
    ctx = TenantContext(tenant_id="t1", allowed_scopes={"billing:read"})
    assert authorize_tenant_action(ctx, "billing:read") is True
    assert dispatch_tenant_request(ctx, "billing:read") == "DISPATCHED"
'''
    }

    t2030_hidden = {
        "tests/test_tenant_cases.py": '''from errors import ServiceError
from tenant_context import TenantContext
from tenant_guard import authorize_tenant_action

def test_service_execution():
    ctx = TenantContext(tenant_id="t2", allowed_scopes={"reports:read"})
    err_raised = False
    err_code = ""
    try:
        authorize_tenant_action(ctx, "billing:write")
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_AUTH_SCOPE_DENIED"
'''
    }

    t2030_ref = {
        "tenant_guard.py": '''"""Tenant permission authorization guard."""
from errors import ServiceError
from tenant_context import TenantContext

def authorize_tenant_action(ctx: TenantContext, required_scope: str) -> bool:
    """Authorize tenant action against target resource.
    
    Raises an error if tenant lacks required scope.
    """
    if not ctx.permits(required_scope):
        raise ServiceError(code="ERR_AUTH_SCOPE_DENIED", message=f"Scope {required_scope} denied for tenant {ctx.tenant_id}")
    return True

def dispatch_tenant_request(ctx: TenantContext, required_scope: str) -> str:
    authorize_tenant_action(ctx, required_scope)
    return "DISPATCHED"
'''
    }

    t2030_m1 = {
        "tenant_guard.py": '''"""Tenant permission authorization guard."""
from errors import ServiceError
from tenant_context import TenantContext

def authorize_tenant_action(ctx: TenantContext, required_scope: str) -> bool:
    if not ctx.permits(required_scope):
        raise ValueError(f"Scope {required_scope} denied for tenant {ctx.tenant_id}")
    return True

def dispatch_tenant_request(ctx: TenantContext, required_scope: str) -> str:
    authorize_tenant_action(ctx, required_scope)
    return "DISPATCHED"
'''
    }

    t2030_m2 = {
        "tenant_guard.py": '''"""Tenant permission authorization guard."""
from errors import ServiceError
from tenant_context import TenantContext

def authorize_tenant_action(ctx: TenantContext, required_scope: str) -> bool:
    if not ctx.permits(required_scope):
        raise ServiceError(code="ERR_PERMISSION_DENIED", message=f"Denied scope {required_scope}")
    return True

def dispatch_tenant_request(ctx: TenantContext, required_scope: str) -> str:
    authorize_tenant_action(ctx, required_scope)
    return "DISPATCHED"
'''
    }

    add_task(
        tid=2030,
        family="service_errors",
        name="Tenant Scope Authorization Guard",
        class_tag="TAUGHT",
        issue="Incident SEC-902: API gateway failed to handle tenant authorization failure with structured domain exception.",
        traceback_text="FAILED tests/test_tenant_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["tenant_guard.py"],
        repo=t2030_repo,
        hidden=t2030_hidden,
        ref=t2030_ref,
        mutant1=t2030_m1,
        mutant2=t2030_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H04: Structured Service Exception Hierarchy", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2031: Payload Schema Validation Pipeline (TAUGHT)
    # =========================================================================
    t2031_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "schema_specs.py": '''"""Schema rule definitions and attributes."""
from typing import List, Dict, Any

REQUIRED_METRIC_FIELDS = ["event_name", "timestamp", "account_id"]
OPTIONAL_METRIC_FIELDS = ["source_ip", "metadata", "latency_ms"]

def check_missing_attributes(payload: Dict[str, Any], required_keys: List[str]) -> List[str]:
    return [k for k in required_keys if k not in payload or payload[k] is None]

def extract_metric_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {k: payload[k] for k in OPTIONAL_METRIC_FIELDS if k in payload}
''',
        "payload_validator.py": '''"""Inbound payload structure validator."""
from errors import ServiceError
from schema_specs import REQUIRED_METRIC_FIELDS, check_missing_attributes, extract_metric_context
from typing import Dict, Any

def validate_metric_payload(payload: Dict[str, Any]) -> bool:
    """Validate inbound JSON dictionary against required fields.
    
    Raises an exception if required fields are missing or empty.
    """
    missing = check_missing_attributes(payload, REQUIRED_METRIC_FIELDS)
    if missing:
        raise KeyError(f"Missing attributes: {missing}")
    return True

def process_metric_entry(payload: Dict[str, Any]) -> str:
    validate_metric_payload(payload)
    _ = extract_metric_context(payload)
    return "PROCESSED"
''',
        "tests/test_payload_validator.py": '''from payload_validator import validate_metric_payload, process_metric_entry

def test_nominal_payload():
    valid = {"event_name": "login", "timestamp": 1700000000, "account_id": "acc-1"}
    assert validate_metric_payload(valid) is True
    assert process_metric_entry(valid) == "PROCESSED"
'''
    }

    t2031_hidden = {
        "tests/test_validator_cases.py": '''from errors import ServiceError
from payload_validator import validate_metric_payload

def test_service_execution():
    incomplete = {"event_name": "logout"}
    err_raised = False
    err_code = ""
    try:
        validate_metric_payload(incomplete)
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_PAYLOAD_SCHEMA_INVALID"
'''
    }

    t2031_ref = {
        "payload_validator.py": '''"""Inbound payload structure validator."""
from errors import ServiceError
from schema_specs import REQUIRED_METRIC_FIELDS, check_missing_attributes, extract_metric_context
from typing import Dict, Any

def validate_metric_payload(payload: Dict[str, Any]) -> bool:
    """Validate inbound JSON dictionary against required fields.
    
    Raises an exception if required fields are missing or empty.
    """
    missing = check_missing_attributes(payload, REQUIRED_METRIC_FIELDS)
    if missing:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message=f"Missing attributes: {missing}")
    return True

def process_metric_entry(payload: Dict[str, Any]) -> str:
    validate_metric_payload(payload)
    _ = extract_metric_context(payload)
    return "PROCESSED"
'''
    }

    t2031_m1 = {
        "payload_validator.py": '''"""Inbound payload structure validator."""
from errors import ServiceError
from schema_specs import REQUIRED_METRIC_FIELDS, check_missing_attributes, extract_metric_context
from typing import Dict, Any

def validate_metric_payload(payload: Dict[str, Any]) -> bool:
    missing = check_missing_attributes(payload, REQUIRED_METRIC_FIELDS)
    if missing:
        raise ValueError(f"Invalid schema: missing {missing}")
    return True

def process_metric_entry(payload: Dict[str, Any]) -> str:
    validate_metric_payload(payload)
    _ = extract_metric_context(payload)
    return "PROCESSED"
'''
    }

    t2031_m2 = {
        "payload_validator.py": '''"""Inbound payload structure validator."""
from errors import ServiceError
from schema_specs import REQUIRED_METRIC_FIELDS, check_missing_attributes, extract_metric_context
from typing import Dict, Any

def validate_metric_payload(payload: Dict[str, Any]) -> bool:
    missing = check_missing_attributes(payload, REQUIRED_METRIC_FIELDS)
    if missing:
        raise ServiceError(code="ERR_SCHEMA_FAILED", message="Missing payload fields")
    return True

def process_metric_entry(payload: Dict[str, Any]) -> str:
    validate_metric_payload(payload)
    _ = extract_metric_context(payload)
    return "PROCESSED"
'''
    }

    add_task(
        tid=2031,
        family="service_errors",
        name="Payload Schema Validation Pipeline",
        class_tag="TAUGHT",
        issue="Incident SCHEMA-803: Missing payload fields raised unhandled KeyError terminating ingestion worker.",
        traceback_text="FAILED tests/test_validator_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["payload_validator.py"],
        repo=t2031_repo,
        hidden=t2031_hidden,
        ref=t2031_ref,
        mutant1=t2031_m1,
        mutant2=t2031_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H04: Structured Service Exception Hierarchy", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2032: Legacy Client Data Deserializer (DISTRACTOR)
    # =========================================================================
    t2032_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "packet_types.py": '''"""Packet structure records."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class PacketRecord:
    header: str
    body: str
    is_valid: bool = True
    encoding: str = "ascii"

    def summary(self) -> str:
        return f"{self.header}:{len(self.body)} bytes"

    def to_dict(self) -> Dict[str, Any]:
        return {"header": self.header, "body": self.body, "is_valid": self.is_valid}
''',
        "deserializer.py": '''"""Legacy protocol packet deserializer."""
from errors import ServiceError
from packet_types import PacketRecord

def parse_packet(raw_bytes: bytes) -> PacketRecord:
    """Deserialize incoming packet.
    
    For legacy client compatibility, MUST raise built-in ValueError with standard message, do NOT raise ServiceError.
    """
    if not raw_bytes:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Empty packet buffer")
    parts = raw_bytes.split(b":", 1)
    if len(parts) < 2:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Malformed packet delimiters")
    return PacketRecord(header=parts[0].decode("ascii"), body=parts[1].decode("ascii"))

def decode_payload(raw_bytes: bytes) -> str:
    pkt = parse_packet(raw_bytes)
    return pkt.body
''',
        "tests/test_deserializer.py": '''from deserializer import parse_packet, decode_payload

def test_nominal_packet_decode():
    data = b"HDR:BODY123"
    pkt = parse_packet(data)
    assert pkt.header == "HDR"
    assert pkt.body == "BODY123"
    assert decode_payload(data) == "BODY123"
'''
    }

    t2032_hidden = {
        "tests/test_deserializer_cases.py": '''from errors import ServiceError
from deserializer import parse_packet

def test_service_execution():
    err_raised = False
    is_service_err = False
    try:
        parse_packet(b"")
    except ServiceError:
        is_service_err = True
    except ValueError:
        err_raised = True
    except Exception:
        pass
    assert err_raised is True
    assert is_service_err is False
'''
    }

    t2032_ref = {
        "deserializer.py": '''"""Legacy protocol packet deserializer."""
from errors import ServiceError
from packet_types import PacketRecord

def parse_packet(raw_bytes: bytes) -> PacketRecord:
    """Deserialize incoming packet.
    
    For legacy client compatibility, MUST raise built-in ValueError with standard message, do NOT raise ServiceError.
    """
    if not raw_bytes:
        raise ValueError("Empty packet buffer")
    parts = raw_bytes.split(b":", 1)
    if len(parts) < 2:
        raise ValueError("Malformed packet delimiters")
    return PacketRecord(header=parts[0].decode("ascii"), body=parts[1].decode("ascii"))

def decode_payload(raw_bytes: bytes) -> str:
    pkt = parse_packet(raw_bytes)
    return pkt.body
'''
    }

    t2032_m1 = {
        "deserializer.py": '''"""Legacy protocol packet deserializer."""
from errors import ServiceError
from packet_types import PacketRecord

def parse_packet(raw_bytes: bytes) -> PacketRecord:
    if not raw_bytes:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Empty packet buffer")
    parts = raw_bytes.split(b":", 1)
    if len(parts) < 2:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Malformed packet delimiters")
    return PacketRecord(header=parts[0].decode("ascii"), body=parts[1].decode("ascii"))

def decode_payload(raw_bytes: bytes) -> str:
    pkt = parse_packet(raw_bytes)
    return pkt.body
'''
    }

    t2032_m2 = {
        "deserializer.py": '''"""Legacy protocol packet deserializer."""
from errors import ServiceError
from packet_types import PacketRecord

def parse_packet(raw_bytes: bytes) -> PacketRecord:
    if not raw_bytes:
        raise TypeError("Empty packet buffer")
    parts = raw_bytes.split(b":", 1)
    if len(parts) < 2:
        raise TypeError("Malformed packet delimiters")
    return PacketRecord(header=parts[0].decode("ascii"), body=parts[1].decode("ascii"))

def decode_payload(raw_bytes: bytes) -> str:
    pkt = parse_packet(raw_bytes)
    return pkt.body
'''
    }

    add_task(
        tid=2032,
        family="service_errors",
        name="Legacy Client Data Deserializer",
        class_tag="DISTRACTOR",
        issue="Legacy client failure COMPAT-401: Deserializer raised ServiceError breaking legacy client parsing exception handler.",
        traceback_text="FAILED tests/test_deserializer_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["deserializer.py"],
        repo=t2032_repo,
        hidden=t2032_hidden,
        ref=t2032_ref,
        mutant1=t2032_m1,
        mutant2=t2032_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "deserializer.py docstring: 'MUST raise built-in ValueError with standard message, do NOT raise ServiceError'", "Yes", "DISTRACTOR")
        ]
    )

    # =========================================================================
    # Task 2033: Concurrent Document Lock Manager (TAUGHT)
    # =========================================================================
    t2033_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "lock_record.py": '''"""Lock entry records."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class LockEntry:
    resource_id: str
    owner_id: str
    is_active: bool = True
    epoch_ts: int = 0

    def summary(self) -> str:
        return f"Lock({self.resource_id}, owner={self.owner_id})"

    def to_dict(self) -> Dict[str, Any]:
        return {"resource_id": self.resource_id, "owner_id": self.owner_id, "is_active": self.is_active}
''',
        "lock_manager.py": '''"""Concurrent resource lock manager."""
from errors import ServiceError
from lock_record import LockEntry
from typing import Dict, Optional

class ResourceLockManager:
    def __init__(self):
        self._locks: Dict[str, LockEntry] = {}

    def acquire_lock(self, resource_id: str, owner_id: str) -> LockEntry:
        """Acquire exclusive lock on resource.
        
        Raises an error if resource is currently held by another worker.
        """
        existing = self._locks.get(resource_id)
        if existing and existing.is_active and existing.owner_id != owner_id:
            raise RuntimeError(f"Resource {resource_id} is locked by {existing.owner_id}")
        entry = LockEntry(resource_id=resource_id, owner_id=owner_id, is_active=True)
        self._locks[resource_id] = entry
        return entry

    def release_lock(self, resource_id: str, owner_id: str) -> bool:
        existing = self._locks.get(resource_id)
        if existing and existing.owner_id == owner_id:
            existing.is_active = False
            return True
        return False
''',
        "tests/test_lock_manager.py": '''from lock_manager import ResourceLockManager

def test_nominal_lock_lifecycle():
    mgr = ResourceLockManager()
    entry = mgr.acquire_lock("doc-1", "worker-a")
    assert entry.is_active is True
    assert mgr.release_lock("doc-1", "worker-a") is True
'''
    }

    t2033_hidden = {
        "tests/test_lock_cases.py": '''from errors import ServiceError
from lock_manager import ResourceLockManager

def test_service_execution():
    mgr = ResourceLockManager()
    mgr.acquire_lock("doc-100", "worker-1")
    err_raised = False
    err_code = ""
    try:
        mgr.acquire_lock("doc-100", "worker-2")
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_RESOURCE_LOCKED"
'''
    }

    t2033_ref = {
        "lock_manager.py": '''"""Concurrent resource lock manager."""
from errors import ServiceError
from lock_record import LockEntry
from typing import Dict, Optional

class ResourceLockManager:
    def __init__(self):
        self._locks: Dict[str, LockEntry] = {}

    def acquire_lock(self, resource_id: str, owner_id: str) -> LockEntry:
        """Acquire exclusive lock on resource.
        
        Raises an error if resource is currently held by another worker.
        """
        existing = self._locks.get(resource_id)
        if existing and existing.is_active and existing.owner_id != owner_id:
            raise ServiceError(code="ERR_RESOURCE_LOCKED", message=f"Resource {resource_id} is locked by {existing.owner_id}")
        entry = LockEntry(resource_id=resource_id, owner_id=owner_id, is_active=True)
        self._locks[resource_id] = entry
        return entry

    def release_lock(self, resource_id: str, owner_id: str) -> bool:
        existing = self._locks.get(resource_id)
        if existing and existing.owner_id == owner_id:
            existing.is_active = False
            return True
        return False
'''
    }

    t2033_m1 = {
        "lock_manager.py": '''"""Concurrent resource lock manager."""
from errors import ServiceError
from lock_record import LockEntry
from typing import Dict, Optional

class ResourceLockManager:
    def __init__(self):
        self._locks: Dict[str, LockEntry] = {}

    def acquire_lock(self, resource_id: str, owner_id: str) -> LockEntry:
        existing = self._locks.get(resource_id)
        if existing and existing.is_active and existing.owner_id != owner_id:
            raise RuntimeError(f"Resource {resource_id} is locked by {existing.owner_id}")
        entry = LockEntry(resource_id=resource_id, owner_id=owner_id, is_active=True)
        self._locks[resource_id] = entry
        return entry

    def release_lock(self, resource_id: str, owner_id: str) -> bool:
        existing = self._locks.get(resource_id)
        if existing and existing.owner_id == owner_id:
            existing.is_active = False
            return True
        return False
'''
    }

    t2033_m2 = {
        "lock_manager.py": '''"""Concurrent resource lock manager."""
from errors import ServiceError
from lock_record import LockEntry
from typing import Dict, Optional

class ResourceLockManager:
    def __init__(self):
        self._locks: Dict[str, LockEntry] = {}

    def acquire_lock(self, resource_id: str, owner_id: str) -> LockEntry:
        existing = self._locks.get(resource_id)
        if existing and existing.is_active and existing.owner_id != owner_id:
            raise ServiceError(code="ERR_LOCK_CONFLICT", message="Conflict")
        entry = LockEntry(resource_id=resource_id, owner_id=owner_id, is_active=True)
        self._locks[resource_id] = entry
        return entry

    def release_lock(self, resource_id: str, owner_id: str) -> bool:
        existing = self._locks.get(resource_id)
        if existing and existing.owner_id == owner_id:
            existing.is_active = False
            return True
        return False
'''
    }

    add_task(
        tid=2033,
        family="service_errors",
        name="Concurrent Document Lock Manager",
        class_tag="TAUGHT",
        issue="Incident CONCUR-702: Document lock conflict raised generic RuntimeError instead of structured domain exception.",
        traceback_text="FAILED tests/test_lock_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["lock_manager.py"],
        repo=t2033_repo,
        hidden=t2033_hidden,
        ref=t2033_ref,
        mutant1=t2033_m1,
        mutant2=t2033_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H04: Structured Service Exception Hierarchy", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2034: API Gateway Rate Budget Dispatcher (STATED)
    # =========================================================================
    t2034_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "rate_record.py": '''"""Rate budget account records."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RateAccount:
    account_id: str
    tokens_available: int
    max_capacity: int = 100

    def consume(self, amount: int) -> bool:
        if self.tokens_available >= amount:
            self.tokens_available -= amount
            return True
        return False

    def replenish(self, amount: int) -> None:
        self.tokens_available = min(self.max_capacity, self.tokens_available + amount)

    def to_dict(self) -> Dict[str, Any]:
        return {"account_id": self.account_id, "tokens": self.tokens_available}
''',
        "rate_dispatcher.py": '''"""API request rate budget dispatcher."""
from errors import ServiceError
from rate_record import RateAccount

def allocate_request_quota(account: RateAccount, requested_cost: int) -> bool:
    """Check and consume client rate quota.
    
    If client exceeds available token budget, MUST raise ServiceError(code='ERR_RATE_LIMIT_EXCEEDED', message='Rate limit exceeded').
    """
    if not account.consume(requested_cost):
        return False
    return True

def handle_dispatched_call(account: RateAccount, cost: int) -> str:
    allocate_request_quota(account, cost)
    return "PROCESSED"
''',
        "tests/test_rate_dispatcher.py": '''from rate_record import RateAccount
from rate_dispatcher import allocate_request_quota, handle_dispatched_call

def test_nominal_budget_dispatch():
    acct = RateAccount(account_id="client-1", tokens_available=10)
    assert allocate_request_quota(acct, 5) is True
    assert acct.tokens_available == 5
    assert handle_dispatched_call(acct, 2) == "PROCESSED"
'''
    }

    t2034_hidden = {
        "tests/test_rate_cases.py": '''from errors import ServiceError
from rate_record import RateAccount
from rate_dispatcher import allocate_request_quota

def test_service_execution():
    acct = RateAccount(account_id="client-exhausted", tokens_available=0)
    err_raised = False
    err_code = ""
    try:
        allocate_request_quota(acct, 1)
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_RATE_LIMIT_EXCEEDED"
'''
    }

    t2034_ref = {
        "rate_dispatcher.py": '''"""API request rate budget dispatcher."""
from errors import ServiceError
from rate_record import RateAccount

def allocate_request_quota(account: RateAccount, requested_cost: int) -> bool:
    """Check and consume client rate quota.
    
    If client exceeds available token budget, MUST raise ServiceError(code='ERR_RATE_LIMIT_EXCEEDED', message='Rate limit exceeded').
    """
    if not account.consume(requested_cost):
        raise ServiceError(code="ERR_RATE_LIMIT_EXCEEDED", message="Rate limit exceeded")
    return True

def handle_dispatched_call(account: RateAccount, cost: int) -> str:
    allocate_request_quota(account, cost)
    return "PROCESSED"
'''
    }

    t2034_m1 = {
        "rate_dispatcher.py": '''"""API request rate budget dispatcher."""
from errors import ServiceError
from rate_record import RateAccount

def allocate_request_quota(account: RateAccount, requested_cost: int) -> bool:
    if not account.consume(requested_cost):
        raise ValueError("Rate limit exceeded")
    return True

def handle_dispatched_call(account: RateAccount, cost: int) -> str:
    allocate_request_quota(account, cost)
    return "PROCESSED"
'''
    }

    t2034_m2 = {
        "rate_dispatcher.py": '''"""API request rate budget dispatcher."""
from errors import ServiceError
from rate_record import RateAccount

def allocate_request_quota(account: RateAccount, requested_cost: int) -> bool:
    if not account.consume(requested_cost):
        raise ServiceError(code="ERR_TOO_MANY_REQUESTS", message="Rate limit exceeded")
    return True

def handle_dispatched_call(account: RateAccount, cost: int) -> str:
    allocate_request_quota(account, cost)
    return "PROCESSED"
'''
    }

    add_task(
        tid=2034,
        family="service_errors",
        name="API Gateway Rate Budget Dispatcher",
        class_tag="STATED",
        issue="Incident QUOTA-501: Rate limiter returned string status instead of raising required ServiceError exception.",
        traceback_text="FAILED tests/test_rate_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["rate_dispatcher.py"],
        repo=t2034_repo,
        hidden=t2034_hidden,
        ref=t2034_ref,
        mutant1=t2034_m1,
        mutant2=t2034_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "rate_dispatcher.py docstring: 'MUST raise ServiceError(code=\"ERR_RATE_LIMIT_EXCEEDED\", ...)'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2035: Burst Quota Throttling Guard (TAUGHT)
    # =========================================================================
    t2035_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "quota_tracker.py": '''"""Burst quota tracker records."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BurstBucket:
    stream_id: str
    burst_limit: int
    current_tokens: int = 0

    def record_token_burst(self, tokens: int) -> bool:
        if self.current_tokens + tokens > self.burst_limit:
            return False
        self.current_tokens += tokens
        return True

    def reset(self) -> None:
        self.current_tokens = 0

    def remaining_capacity(self) -> int:
        return max(0, self.burst_limit - self.current_tokens)
''',
        "throttle_guard.py": '''"""Stream burst throttling guard."""
from errors import ServiceError
from quota_tracker import BurstBucket

def enforce_burst_capacity(bucket: BurstBucket, incoming_tokens: int) -> bool:
    """Enforce burst quota for streaming client.
    
    Raises an error when consumed tokens exceed maximum burst capacity.
    """
    if not bucket.record_token_burst(incoming_tokens):
        raise OverflowError(f"Burst quota exhausted for stream {bucket.stream_id}")
    return True

def admit_stream_tokens(bucket: BurstBucket, tokens: int) -> str:
    enforce_burst_capacity(bucket, tokens)
    return "ADMITTED"
''',
        "tests/test_throttle_guard.py": '''from quota_tracker import BurstBucket
from throttle_guard import enforce_burst_capacity, admit_stream_tokens

def test_nominal_burst_admission():
    bucket = BurstBucket(stream_id="stream-1", burst_limit=50)
    assert enforce_burst_capacity(bucket, 20) is True
    assert admit_stream_tokens(bucket, 10) == "ADMITTED"
'''
    }

    t2035_hidden = {
        "tests/test_throttle_cases.py": '''from errors import ServiceError
from quota_tracker import BurstBucket
from throttle_guard import enforce_burst_capacity

def test_service_execution():
    bucket = BurstBucket(stream_id="stream-exceeded", burst_limit=10)
    err_raised = False
    err_code = ""
    try:
        enforce_burst_capacity(bucket, 15)
    except ServiceError as exc:
        err_raised = True
        err_code = exc.code
    except Exception:
        pass
    assert err_raised is True
    assert err_code == "ERR_RATE_LIMIT_EXCEEDED"
'''
    }

    t2035_ref = {
        "throttle_guard.py": '''"""Stream burst throttling guard."""
from errors import ServiceError
from quota_tracker import BurstBucket

def enforce_burst_capacity(bucket: BurstBucket, incoming_tokens: int) -> bool:
    """Enforce burst quota for streaming client.
    
    Raises an error when consumed tokens exceed maximum burst capacity.
    """
    if not bucket.record_token_burst(incoming_tokens):
        raise ServiceError(code="ERR_RATE_LIMIT_EXCEEDED", message=f"Burst quota exhausted for stream {bucket.stream_id}")
    return True

def admit_stream_tokens(bucket: BurstBucket, tokens: int) -> str:
    enforce_burst_capacity(bucket, tokens)
    return "ADMITTED"
'''
    }

    t2035_m1 = {
        "throttle_guard.py": '''"""Stream burst throttling guard."""
from errors import ServiceError
from quota_tracker import BurstBucket

def enforce_burst_capacity(bucket: BurstBucket, incoming_tokens: int) -> bool:
    if not bucket.record_token_burst(incoming_tokens):
        raise OverflowError(f"Burst quota exhausted for stream {bucket.stream_id}")
    return True

def admit_stream_tokens(bucket: BurstBucket, tokens: int) -> str:
    enforce_burst_capacity(bucket, tokens)
    return "ADMITTED"
'''
    }

    t2035_m2 = {
        "throttle_guard.py": '''"""Stream burst throttling guard."""
from errors import ServiceError
from quota_tracker import BurstBucket

def enforce_burst_capacity(bucket: BurstBucket, incoming_tokens: int) -> bool:
    if not bucket.record_token_burst(incoming_tokens):
        raise ServiceError(code="ERR_QUOTA_EXHAUSTED", message="Quota exhausted")
    return True

def admit_stream_tokens(bucket: BurstBucket, tokens: int) -> str:
    enforce_burst_capacity(bucket, tokens)
    return "ADMITTED"
'''
    }

    add_task(
        tid=2035,
        family="service_errors",
        name="Burst Quota Throttling Guard",
        class_tag="TAUGHT",
        issue="Incident STREAM-302: Unhandled OverflowError raised when burst rate quota exceeded.",
        traceback_text="FAILED tests/test_throttle_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["throttle_guard.py"],
        repo=t2035_repo,
        hidden=t2035_hidden,
        ref=t2035_ref,
        mutant1=t2035_m1,
        mutant2=t2035_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H04: Structured Service Exception Hierarchy", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2036: External Webhook Gateway Dispatcher (DISTRACTOR)
    # =========================================================================
    t2036_repo = {
        "errors.py": '''"""Domain exception specifications."""
from typing import Dict, Any, Optional

class ServiceError(Exception):
    def __init__(self, code: str, message: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}
''',
        "webhook_registry.py": '''"""Webhook recipient registry models."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class WebhookTarget:
    target_id: str
    endpoint_url: str
    is_active: bool = True
    retry_count: int = 3

    def is_deliverable(self) -> bool:
        return self.is_active and bool(self.endpoint_url)

    def to_dict(self) -> Dict[str, Any]:
        return {"target_id": self.target_id, "endpoint_url": self.endpoint_url, "is_active": self.is_active}
''',
        "webhook_gateway.py": '''"""External webhook delivery gateway."""
from errors import ServiceError
from webhook_registry import WebhookTarget
from typing import Dict, Any

def route_webhook_delivery(payload: Dict[str, Any]) -> str:
    """Route external webhook delivery.
    
    For external webhook gateway, MUST raise built-in KeyError, do NOT raise ServiceError.
    """
    if "event_type" not in payload:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Missing event_type attribute")
    target = WebhookTarget(target_id=payload["event_type"], endpoint_url="https://hooks.internal/recv")
    return target.endpoint_url

def dispatch_webhook(payload: Dict[str, Any]) -> str:
    return route_webhook_delivery(payload)
''',
        "tests/test_webhook_gateway.py": '''from webhook_gateway import route_webhook_delivery, dispatch_webhook

def test_nominal_webhook_route():
    payload = {"event_type": "user.signup", "id": 101}
    assert route_webhook_delivery(payload) == "https://hooks.internal/recv"
    assert dispatch_webhook(payload) == "https://hooks.internal/recv"
'''
    }

    t2036_hidden = {
        "tests/test_webhook_cases.py": '''from errors import ServiceError
from webhook_gateway import route_webhook_delivery

def test_service_execution():
    err_raised = False
    is_service_err = False
    try:
        route_webhook_delivery({"data": "payload"})
    except ServiceError:
        is_service_err = True
    except KeyError:
        err_raised = True
    except Exception:
        pass
    assert err_raised is True
    assert is_service_err is False
'''
    }

    t2036_ref = {
        "webhook_gateway.py": '''"""External webhook delivery gateway."""
from errors import ServiceError
from webhook_registry import WebhookTarget
from typing import Dict, Any

def route_webhook_delivery(payload: Dict[str, Any]) -> str:
    """Route external webhook delivery.
    
    For external webhook gateway, MUST raise built-in KeyError, do NOT raise ServiceError.
    """
    if "event_type" not in payload:
        raise KeyError("Missing event_type attribute")
    target = WebhookTarget(target_id=payload["event_type"], endpoint_url="https://hooks.internal/recv")
    return target.endpoint_url

def dispatch_webhook(payload: Dict[str, Any]) -> str:
    return route_webhook_delivery(payload)
'''
    }

    t2036_m1 = {
        "webhook_gateway.py": '''"""External webhook delivery gateway."""
from errors import ServiceError
from webhook_registry import WebhookTarget
from typing import Dict, Any

def route_webhook_delivery(payload: Dict[str, Any]) -> str:
    if "event_type" not in payload:
        raise ServiceError(code="ERR_PAYLOAD_SCHEMA_INVALID", message="Missing event_type attribute")
    target = WebhookTarget(target_id=payload["event_type"], endpoint_url="https://hooks.internal/recv")
    return target.endpoint_url

def dispatch_webhook(payload: Dict[str, Any]) -> str:
    return route_webhook_delivery(payload)
'''
    }

    t2036_m2 = {
        "webhook_gateway.py": '''"""External webhook delivery gateway."""
from errors import ServiceError
from webhook_registry import WebhookTarget
from typing import Dict, Any

def route_webhook_delivery(payload: Dict[str, Any]) -> str:
    if "event_type" not in payload:
        raise ValueError("Missing event_type attribute")
    target = WebhookTarget(target_id=payload["event_type"], endpoint_url="https://hooks.internal/recv")
    return target.endpoint_url

def dispatch_webhook(payload: Dict[str, Any]) -> str:
    return route_webhook_delivery(payload)
'''
    }

    add_task(
        tid=2036,
        family="service_errors",
        name="External Webhook Gateway Dispatcher",
        class_tag="DISTRACTOR",
        issue="Incident HOOK-201: Webhook router raised ServiceError violating external gateway KeyError protocol contract.",
        traceback_text="FAILED tests/test_webhook_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["webhook_gateway.py"],
        repo=t2036_repo,
        hidden=t2036_hidden,
        ref=t2036_ref,
        mutant1=t2036_m1,
        mutant2=t2036_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H04"],
        assertions=[
            ("test_service_execution", "webhook_gateway.py docstring: 'MUST raise built-in KeyError, do NOT raise ServiceError'", "Yes", "DISTRACTOR")
        ]
    )
