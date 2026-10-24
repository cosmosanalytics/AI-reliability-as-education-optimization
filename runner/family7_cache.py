"""Family 7: cache_ttl (Tasks 2025 - 2028, all TRANSFER).

Governing Rule: Rule H09 (Injectable clocks & TTL expiration: clock=time.monotonic, expired when t >= expires_at).
Competing Alternatives: Hardcoded time.time(), time.sleep(), strict inequality t > expires_at.
Target: 40-120 non-test lines across 3-4 files.
"""

def register_family_7(add_task):
    # =========================================================================
    # Task 2025: In-Memory Token Cache (TRANSFER, HRC=False, VTS=False)
    # =========================================================================
    t2025_repo = {
        "token_record.py": '''"""Token metadata schemas."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CachedToken:
    token_str: str
    expires_at: float
    scope: str = "read_write"

    def is_expired_at(self, current_time: float) -> bool:
        return current_time >= self.expires_at
''',
        "cache.py": '''"""In-memory security token cache."""
import time
from typing import Dict, Optional, Callable
from token_record import CachedToken

class TokenCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        """In-memory token cache with injectable clock."""
        self._clock = clock or time.time
        self._store: Dict[str, CachedToken] = {}

    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:
        now = self._clock()
        self._store[key] = CachedToken(token_str=token_str, expires_at=now + ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry:
            return None
        now = self._clock()
        if now > entry.expires_at:
            del self._store[key]
            return None
        return entry.token_str

    def size(self) -> int:
        return len(self._store)
''',
        "cache_utils.py": '''"""Cache key hashing and diagnostics."""
def format_cache_key(prefix: str, identifier: str) -> str:
    return f"{prefix}::{identifier}"
''',
        "tests/test_cache.py": '''from cache import TokenCache

def test_cache_set_get():
    c = TokenCache()
    c.set("k1", "tok-1", 100.0)
    assert c.get("k1") == "tok-1"
'''
    }

    t2025_hidden = {
        "tests/test_cache_hidden.py": '''from cache import TokenCache

def test_injectable_clock_monotonic_taught():
    t = [100.0]
    c = TokenCache(clock=lambda: t[0])
    c.set("k1", "val1", 5.0)
    assert c.get("k1") == "val1"
    
    t[0] = 105.0
    assert c.get("k1") is None
'''
    }

    t2025_ref = {
        "cache.py": '''"""In-memory security token cache."""
import time
from typing import Dict, Optional, Callable
from token_record import CachedToken

class TokenCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        """In-memory token cache with injectable clock."""
        self._clock = clock if clock is not None else time.monotonic
        self._store: Dict[str, CachedToken] = {}

    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:
        now = self._clock()
        self._store[key] = CachedToken(token_str=str(token_str), expires_at=now + ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry:
            return None
        now = self._clock()
        if now >= entry.expires_at:
            del self._store[key]
            return None
        return entry.token_str

    def size(self) -> int:
        return len(self._store)
'''
    }

    t2025_m1 = {
        "cache.py": '''"""In-memory security token cache."""
import time
from typing import Dict, Optional, Callable
from token_record import CachedToken

class TokenCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock if clock is not None else time.monotonic
        self._store: Dict[str, CachedToken] = {}

    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:
        now = self._clock()
        self._store[key] = CachedToken(token_str=token_str, expires_at=now + ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry:
            return None
        now = self._clock()
        if now > entry.expires_at:
            del self._store[key]
            return None
        return entry.token_str

    def size(self) -> int:
        return len(self._store)
'''
    }

    t2025_m2 = {
        "cache.py": '''"""In-memory security token cache."""
import time
from typing import Dict, Optional, Callable
from token_record import CachedToken

class TokenCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = time.time
        self._store: Dict[str, CachedToken] = {}

    def set(self, key: str, token_str: str, ttl_seconds: float) -> None:
        self._store[key] = CachedToken(token_str=token_str, expires_at=time.time() + ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry or time.time() >= entry.expires_at:
            return None
        return entry.token_str

    def size(self) -> int:
        return len(self._store)
'''
    }

    add_task(
        tid=2025,
        family="cache_ttl",
        name="In-Memory Token Cache",
        class_tag="TRANSFER",
        issue="Auth service failure AUTH-901: Stale bearer tokens remained valid at the exact expiration second due to loose inequality check.",
        traceback_text="FAILED tests/test_cache_hidden.py::test_injectable_clock_monotonic_taught - AssertionError: Expiration boundary failure at cache.py:22: token remained active at exact expires_at timestamp",
        traceback_files=["cache.py"],
        repo=t2025_repo,
        hidden=t2025_hidden,
        ref=t2025_ref,
        mutant1=t2025_m1,
        mutant2=t2025_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_injectable_clock_monotonic_taught", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2026: API Rate Limit Session Store (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2026_repo = {
        "session_data.py": '''"""Rate limit session records."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RateLimitSession:
    client_ip: str
    request_count: int
    expires_at: float
    max_requests: int = 60

    def has_exceeded_quota(self) -> bool:
        return self.request_count >= self.max_requests
''',
        "session_store.py": '''"""Rate limit session storage."""
from typing import Optional, Callable
from session_validator import is_session_expired
from session_data import RateLimitSession

class SessionStore:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock
        self._sessions = {}

    def register(self, ip: str, ttl: float) -> None:
        import time
        now = self._clock() if self._clock else time.monotonic()
        self._sessions[ip] = RateLimitSession(ip, 1, now + ttl)

    def is_active(self, ip: str) -> bool:
        sess = self._sessions.get(ip)
        if not sess:
            return False
        import time
        now = self._clock() if self._clock else time.monotonic()
        return not is_session_expired(sess.expires_at, now)

    def active_count(self) -> int:
        return len(self._sessions)
''',
        "session_validator.py": '''"""Session expiration validation logic."""
def is_session_expired(expires_at: float, current_ts: float) -> bool:
    return current_ts > expires_at

def time_remaining(expires_at: float, current_ts: float) -> float:
    return max(0.0, expires_at - current_ts)
''',
        "tests/test_session_store.py": '''from session_store import SessionStore

def test_nominal_registration():
    s = SessionStore()
    s.register("192.168.1.1", 60.0)
    assert s.is_active("192.168.1.1") is True
'''
    }

    t2026_hidden = {
        "tests/test_session_store_hidden.py": '''from session_store import SessionStore
from session_validator import is_session_expired

def test_session_boundary_taught():
    t = [500.0]
    s = SessionStore(clock=lambda: t[0])
    s.register("10.0.0.1", 10.0)
    assert s.is_active("10.0.0.1") is True
    
    t[0] = 510.0
    assert s.is_active("10.0.0.1") is False

def test_session_validator_direct():
    assert is_session_expired(100.0, 100.0) is True
    assert is_session_expired(100.0, 99.9) is False
'''
    }

    t2026_ref = {
        "session_validator.py": '''"""Session expiration validation logic."""
def is_session_expired(expires_at: float, current_ts: float) -> bool:
    return current_ts >= expires_at

def time_remaining(expires_at: float, current_ts: float) -> float:
    return max(0.0, expires_at - current_ts)
'''
    }

    t2026_m1 = {
        "session_store.py": '''"""Rate limit session storage."""
from typing import Optional, Callable
from session_validator import is_session_expired
from session_data import RateLimitSession

class SessionStore:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock
        self._sessions = {}

    def register(self, ip: str, ttl: float) -> None:
        import time
        now = self._clock() if self._clock else time.monotonic()
        self._sessions[ip] = RateLimitSession(ip, 1, now + ttl)

    def is_active(self, ip: str) -> bool:
        sess = self._sessions.get(ip)
        if not sess:
            return False
        import time
        now = self._clock() if self._clock else time.monotonic()
        if now >= sess.expires_at:
            return False
        return not is_session_expired(sess.expires_at, now)

    def active_count(self) -> int:
        return len(self._sessions)
'''
    }

    t2026_m2 = {
        "session_validator.py": '''"""Session expiration validation logic."""
def is_session_expired(expires_at: float, current_ts: float) -> bool:
    return current_ts > expires_at

def time_remaining(expires_at: float, current_ts: float) -> float:
    return max(0.0, expires_at - current_ts)
'''
    }

    add_task(
        tid=2026,
        family="cache_ttl",
        name="API Rate Limit Session Store",
        class_tag="TRANSFER",
        issue="Rate limiter bypass RL-103: API client requests allowed through after session limit expired due to boundary condition error.",
        traceback_text="FAILED tests/test_session_store_hidden.py::test_session_boundary_taught - AssertionError: Session boundary error at session_store.py:22: rate limit session active at exact expiration second",
        traceback_files=["session_store.py"],
        repo=t2026_repo,
        hidden=t2026_hidden,
        ref=t2026_ref,
        mutant1=t2026_m1,
        mutant2=t2026_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_session_boundary_taught", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER"),
            ("test_session_validator_direct", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2027: Distributed Lease Expiry Guard (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2027_repo = {
        "lease_entry.py": '''"""Lease entry metadata."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class LeaseRecord:
    lease_key: str
    owner: str
    valid_until: float
    fencing_token: int = 100

    def matches_owner(self, candidate: str) -> bool:
        return self.owner == candidate
''',
        "lease_guard.py": '''"""Distributed cluster lease manager."""
from typing import Optional, Callable
from clock_source import is_lease_valid
from lease_entry import LeaseRecord

class LeaseGuard:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock
        self._leases = {}

    def acquire(self, key: str, owner: str, lease_duration: float) -> None:
        import time
        now = self._clock() if self._clock else time.monotonic()
        self._leases[key] = LeaseRecord(key, owner, now + lease_duration)

    def holds_lease(self, key: str, owner: str) -> bool:
        lease = self._leases.get(key)
        if not lease or lease.owner != owner:
            return False
        import time
        now = self._clock() if self._clock else time.monotonic()
        return is_lease_valid(lease.valid_until, now)

    def lease_count(self) -> int:
        return len(self._leases)
''',
        "clock_source.py": '''"""Lease validity checker."""
def is_lease_valid(valid_until: float, current_time: float) -> bool:
    return current_time <= valid_until

def remaining_lease_time(valid_until: float, current_time: float) -> float:
    return max(0.0, valid_until - current_time)
''',
        "tests/test_lease.py": '''from lease_guard import LeaseGuard

def test_nominal_lease():
    lg = LeaseGuard()
    lg.acquire("lock1", "nodeA", 30.0)
    assert lg.holds_lease("lock1", "nodeA") is True
'''
    }

    t2027_hidden = {
        "tests/test_lease_hidden.py": '''from lease_guard import LeaseGuard
from clock_source import is_lease_valid

def test_lease_expiry_taught():
    t = [1000.0]
    lg = LeaseGuard(clock=lambda: t[0])
    lg.acquire("resource_db", "node1", 5.0)
    assert lg.holds_lease("resource_db", "node1") is True
    
    t[0] = 1005.0
    assert lg.holds_lease("resource_db", "node1") is False

def test_clock_source_direct():
    assert is_lease_valid(100.0, 100.0) is False
    assert is_lease_valid(100.0, 99.0) is True
'''
    }

    t2027_ref = {
        "clock_source.py": '''"""Lease validity checker."""
def is_lease_valid(valid_until: float, current_time: float) -> bool:
    return current_time < valid_until

def remaining_lease_time(valid_until: float, current_time: float) -> float:
    return max(0.0, valid_until - current_time)
'''
    }

    t2027_m1 = {
        "lease_guard.py": '''"""Distributed cluster lease manager."""
from typing import Optional, Callable
from clock_source import is_lease_valid
from lease_entry import LeaseRecord

class LeaseGuard:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock
        self._leases = {}

    def acquire(self, key: str, owner: str, lease_duration: float) -> None:
        import time
        now = self._clock() if self._clock else time.monotonic()
        self._leases[key] = LeaseRecord(key, owner, now + lease_duration)

    def holds_lease(self, key: str, owner: str) -> bool:
        lease = self._leases.get(key)
        if not lease or lease.owner != owner:
            return False
        import time
        now = self._clock() if self._clock else time.monotonic()
        if now >= lease.valid_until:
            return False
        return is_lease_valid(lease.valid_until, now)

    def lease_count(self) -> int:
        return len(self._leases)
'''
    }

    t2027_m2 = {
        "clock_source.py": '''"""Lease validity checker."""
def is_lease_valid(valid_until: float, current_time: float) -> bool:
    return current_time <= valid_until

def remaining_lease_time(valid_until: float, current_time: float) -> float:
    return max(0.0, valid_until - current_time)
'''
    }

    add_task(
        tid=2027,
        family="cache_ttl",
        name="Distributed Lease Expiry Guard",
        class_tag="TRANSFER",
        issue="Distributed lock split-brain LOCK-881: Two nodes simultaneously held master lock when lease was retained at exact expiration second.",
        traceback_text="FAILED tests/test_lease_hidden.py::test_lease_expiry_taught - AssertionError: Split-brain lease detected at lease_guard.py:23: node retained master lease at exact valid_until boundary",
        traceback_files=["lease_guard.py"],
        repo=t2027_repo,
        hidden=t2027_hidden,
        ref=t2027_ref,
        mutant1=t2027_m1,
        mutant2=t2027_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_lease_expiry_taught", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER"),
            ("test_clock_source_direct", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2028: DNS Cache TTL Resolver (TRANSFER, HRC=False, VTS=True)
    # =========================================================================
    t2028_repo = {
        "dns_record.py": '''"""DNS record entry model."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class DnsEntry:
    domain: str
    ip_addr: str
    expires_at: float
    record_type: str = "A"

    def is_valid_format(self) -> bool:
        return "." in self.ip_addr
''',
        "dns_resolver.py": '''"""DNS cache resolver client."""
import time
from typing import Dict, Optional, Callable
from dns_record import DnsEntry

class DnsCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock or time.time
        self._entries: Dict[str, DnsEntry] = {}

    def put_record(self, domain: str, ip: str, ttl: float) -> None:
        now = self._clock()
        self._entries[domain] = DnsEntry(domain, ip, now + ttl)

    def lookup(self, domain: str) -> Optional[str]:
        entry = self._entries.get(domain)
        if not entry:
            return None
        now = self._clock()
        if now > entry.expires_at:
            del self._entries[domain]
            return None
        return entry.ip_addr

    def count(self) -> int:
        return len(self._entries)
''',
        "dns_utils.py": '''"""DNS domain utilities."""
def normalize_domain_name(name: str) -> str:
    return name.strip().lower().rstrip(".")
''',
        "tests/test_dns.py": '''from dns_resolver import DnsCache

def test_dns_lookup():
    cache = DnsCache()
    cache.put_record("example.com", "93.184.216.34", 10.0)
    assert cache.lookup("example.com") == "93.184.216.34"

def test_injected_clock_visible_sensitive():
    clock_calls = [0]
    def fake_clock():
        clock_calls[0] += 1
        return 1000.0
    cache = DnsCache(clock=fake_clock)
    cache.put_record("test.org", "1.1.1.1", 5.0)
    assert clock_calls[0] > 0
'''
    }

    t2028_hidden = {
        "tests/test_dns_hidden.py": '''from dns_resolver import DnsCache

def test_dns_exact_expiry_taught():
    t = [100.0]
    cache = DnsCache(clock=lambda: t[0])
    cache.put_record("service.internal", "10.0.0.5", 3.0)
    assert cache.lookup("service.internal") == "10.0.0.5"
    
    t[0] = 103.0
    assert cache.lookup("service.internal") is None
'''
    }

    t2028_ref = {
        "dns_resolver.py": '''"""DNS cache resolver client."""
import time
from typing import Dict, Optional, Callable
from dns_record import DnsEntry

class DnsCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock if clock is not None else time.monotonic
        self._entries: Dict[str, DnsEntry] = {}

    def put_record(self, domain: str, ip: str, ttl: float) -> None:
        now = self._clock()
        self._entries[domain] = DnsEntry(domain, ip, now + ttl)

    def lookup(self, domain: str) -> Optional[str]:
        entry = self._entries.get(domain)
        if not entry:
            return None
        now = self._clock()
        if now >= entry.expires_at:
            del self._entries[domain]
            return None
        return entry.ip_addr

    def count(self) -> int:
        return len(self._entries)
'''
    }

    t2028_m1 = {
        "dns_resolver.py": '''"""DNS cache resolver client."""
import time
from typing import Dict, Optional, Callable
from dns_record import DnsEntry

class DnsCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = clock if clock is not None else time.monotonic
        self._entries: Dict[str, DnsEntry] = {}

    def put_record(self, domain: str, ip: str, ttl: float) -> None:
        now = self._clock()
        self._entries[domain] = DnsEntry(domain, ip, now + ttl)

    def lookup(self, domain: str) -> Optional[str]:
        entry = self._entries.get(domain)
        if not entry:
            return None
        now = self._clock()
        if now > entry.expires_at:
            del self._entries[domain]
            return None
        return entry.ip_addr

    def count(self) -> int:
        return len(self._entries)
'''
    }

    t2028_m2 = {
        "dns_resolver.py": '''"""DNS cache resolver client."""
import time
from typing import Dict, Optional, Callable
from dns_record import DnsEntry

class DnsCache:
    def __init__(self, clock: Optional[Callable[[], float]] = None):
        self._clock = time.time
        self._entries: Dict[str, DnsEntry] = {}

    def put_record(self, domain: str, ip: str, ttl: float) -> None:
        self._entries[domain] = DnsEntry(domain, ip, time.time() + ttl)

    def lookup(self, domain: str) -> Optional[str]:
        entry = self._entries.get(domain)
        if not entry or time.time() >= entry.expires_at:
            return None
        return entry.ip_addr

    def count(self) -> int:
        return len(self._entries)
'''
    }

    add_task(
        tid=2028,
        family="cache_ttl",
        name="DNS Cache TTL Resolver",
        class_tag="TRANSFER",
        issue="Network resolution failure NET-505: Expired upstream DNS record routed traffic to decommissioned server IP address at exact TTL deadline.",
        traceback_text="FAILED tests/test_dns_hidden.py::test_dns_exact_expiry_taught - AssertionError: DNS TTL failure at dns_resolver.py:22: stale DNS entry returned at exact TTL expiration second",
        traceback_files=["dns_resolver.py"],
        repo=t2028_repo,
        hidden=t2028_hidden,
        ref=t2028_ref,
        mutant1=t2028_m1,
        mutant2=t2028_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_dns_exact_expiry_taught", "HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration", "No", "TRANSFER")
        ]
    )

    print("Family 7 registered (Tasks 2025-2028).")
