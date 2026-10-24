"""suite_e4.py: Multi-module repository benchmark suite for E4 evaluation (12 tasks).

Meets all requirements of REAL_TEST_REQUIREMENTS.md:
- 3 to 7 files per repository task (coupling callers, configuration, tests, multiple modules).
- Explicit, discoverable contracts (docstrings, visible tests, issue descriptions). Zero unstated conventions.
- Gold reference solutions pass 100% of visible and hidden tests.
- Unpatched baseline code fails 100% of hidden tests.
"""

import sys
import os

# Add harness and benchmarks directories to path
_cur = os.path.dirname(os.path.abspath(__file__))
_harness = os.path.abspath(os.path.join(_cur, "..", "harness"))
if _cur not in sys.path:
    sys.path.insert(0, _cur)
if _harness not in sys.path:
    sys.path.insert(0, _harness)

import hard2_tasks
import hard3_tasks

T = []


def register_task(
    tid,
    name,
    issue,
    repo,
    hidden,
    ref,
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
        "group": "E4",
        "name": name,
        "rules": "W01,W02,W03,W05,W08,W10,W14",
        "issue": issue,
        "repo": repo,
        "key": key,
        "ref": ref,
    }
    T.append(task_dict)
    return task_dict


# ==============================================================================
# Tasks 1001-1006: Derived from validated multi-module Hard2 tasks
# ==============================================================================
for old_t in hard2_tasks.T:
    new_id = old_t["id"] + 800  # 201 -> 1001, ..., 206 -> 1006
    # Ensure docstrings and stated contracts are fully intact
    hidden_overlay = old_t["key"]["variants"][0]["overlay"]
    register_task(
        tid=new_id,
        name=old_t["name"],
        issue=old_t["issue"],
        repo=dict(old_t["repo"]),
        hidden=dict(hidden_overlay),
        ref=dict(old_t["ref"]),
        visible=old_t["key"].get("visible_paths"),
        protected=old_t["key"].get("protected"),
    )

# ==============================================================================
# Task 1007: Derived from validated multi-module Shop pipeline (Hard3)
# ==============================================================================
for old_t in hard3_tasks.T:
    new_id = 1007  # 301 -> 1007
    hidden_overlay = old_t["key"]["variants"][0]["overlay"]
    register_task(
        tid=new_id,
        name=old_t["name"],
        issue=old_t["issue"],
        repo=dict(old_t["repo"]),
        hidden=dict(hidden_overlay),
        ref=dict(old_t["ref"]),
        visible=old_t["key"].get("visible_paths"),
        protected=old_t["key"].get("protected"),
    )


# ==============================================================================
# Task 1008: Middleware Pipeline Onion Architecture (5 files)
# ==============================================================================
t1008_issue = (
    "Bug report: In the middleware pipeline, when an authentication middleware or validation layer aborts a request "
    "(by calling context.abort(status, body)), the outer middleware cleanup/response hooks are never called, leaking "
    "open spans and audit logs. Furthermore, when middleware executes normally, response hooks must run in reverse "
    "(onion) order, but currently run forwards. Fix pipeline.py and middleware.py so aborting still executes response hooks "
    "in reverse order with the aborted response status and body, and ensure context.state is preserved across all layers. "
    "Do not change the tests."
)

t1008_repo = {
    "context.py": """class RequestContext:
    \"\"\"Request context holding metadata, shared state, and response details.\"\"\"

    def __init__(self, path, method="GET", headers=None):
        self.path = path
        self.method = method
        self.headers = dict(headers or {})
        self.state = {}
        self.response_status = None
        self.response_body = None
        self.aborted = False

    def abort(self, status, body):
        \"\"\"Abort the request with an immediate error response.\"\"\"
        self.response_status = status
        self.response_body = body
        self.aborted = True
""",
    "middleware.py": """class Middleware:
    def process_request(self, ctx):
        pass

    def process_response(self, ctx):
        pass


class AuthMiddleware(Middleware):
    def __init__(self, valid_tokens):
        self.valid_tokens = set(valid_tokens)

    def process_request(self, ctx):
        token = ctx.headers.get("Authorization")
        if token not in self.valid_tokens:
            ctx.abort(401, "Unauthorized")


class AuditMiddleware(Middleware):
    def __init__(self, audit_log):
        self.audit_log = audit_log

    def process_request(self, ctx):
        self.audit_log.append(f"REQ:{ctx.method}:{ctx.path}")

    def process_response(self, ctx):
        self.audit_log.append(f"RES:{ctx.response_status}")
""",
    "pipeline.py": """class MiddlewarePipeline:
    \"\"\"Executes middleware in onion order: process_request forwards, process_response in reverse.\"\"\"

    def __init__(self, middlewares=None):
        self.middlewares = list(middlewares or [])

    def add(self, mw):
        self.middlewares.append(mw)

    def execute(self, ctx, handler):
        \"\"\"Run request phases forwards, invoke handler, then run response phases in reverse.
        If ctx.abort() is called during request phase, stop calling subsequent request hooks,
        but DO execute process_response on all middleware that already processed the request, in reverse order.\"\"\"
        for mw in self.middlewares:
            mw.process_request(ctx)
            if ctx.aborted:
                # Buggy: returns immediately without running response hooks of outer layers
                return ctx

        if not ctx.aborted:
            handler(ctx)

        # Buggy: runs response hooks forwards instead of reverse
        for mw in self.middlewares:
            mw.process_response(ctx)

        return ctx
""",
    "app.py": """from pipeline import MiddlewarePipeline


class App:
    def __init__(self):
        self.pipeline = MiddlewarePipeline()
        self.routes = {}

    def route(self, path):
        def decorator(fn):
            self.routes[path] = fn
            return fn
        return decorator

    def handle(self, ctx):
        def default_handler(c):
            if c.path in self.routes:
                c.response_status = 200
                c.response_body = self.routes[c.path](c)
            else:
                c.abort(404, "Not Found")
        return self.pipeline.execute(ctx, default_handler)
""",
    "tests/test_pipeline.py": """from context import RequestContext
from middleware import AuthMiddleware, AuditMiddleware
from pipeline import MiddlewarePipeline


def test_normal_flow():
    audit = []
    p = MiddlewarePipeline([AuditMiddleware(audit), AuthMiddleware(["secret"])])
    ctx = RequestContext("/items", "GET", {"Authorization": "secret"})

    def handler(c):
        c.response_status = 200
        c.response_body = "ok"

    p.execute(ctx, handler)
    assert ctx.response_status == 200
    assert audit == ["REQ:GET:/items", "RES:200"]
""",
}

t1008_hidden = {
    "tests/test_hidden_pipeline.py": """import pytest
from context import RequestContext
from middleware import Middleware, AuthMiddleware, AuditMiddleware
from pipeline import MiddlewarePipeline
from app import App


class StateMiddleware(Middleware):
    def __init__(self, key, val):
        self.key = key
        self.val = val

    def process_request(self, ctx):
        ctx.state[self.key] = self.val

    def process_response(self, ctx):
        ctx.state[self.key + "_ended"] = True


class OrderTrackingMiddleware(Middleware):
    def __init__(self, name, tracker):
        self.name = name
        self.tracker = tracker

    def process_request(self, ctx):
        self.tracker.append(f"enter_{self.name}")

    def process_response(self, ctx):
        self.tracker.append(f"exit_{self.name}")


def test_abort_calls_cleanup_in_reverse():
    tracker = []
    m1 = OrderTrackingMiddleware("outer", tracker)
    m2 = AuthMiddleware(["token-abc"])
    m3 = OrderTrackingMiddleware("inner", tracker)
    p = MiddlewarePipeline([m1, m2, m3])

    ctx = RequestContext("/secret", "GET", {"Authorization": "wrong"})
    p.execute(ctx, lambda c: c.abort(500, "Should not run"))

    assert ctx.aborted is True
    assert ctx.response_status == 401
    assert ctx.response_body == "Unauthorized"
    # m1 entered, m2 aborted, m3 never entered. Outer m1 must exit!
    assert tracker == ["enter_outer", "exit_outer"]


def test_reverse_onion_order():
    tracker = []
    m1 = OrderTrackingMiddleware("m1", tracker)
    m2 = OrderTrackingMiddleware("m2", tracker)
    m3 = OrderTrackingMiddleware("m3", tracker)
    p = MiddlewarePipeline([m1, m2, m3])

    ctx = RequestContext("/test")
    p.execute(ctx, lambda c: setattr(c, 'response_status', 200))
    assert tracker == ["enter_m1", "enter_m2", "enter_m3", "exit_m3", "exit_m2", "exit_m1"]


def test_state_and_app_integration():
    audit = []
    app = App()
    app.pipeline.add(AuditMiddleware(audit))
    app.pipeline.add(StateMiddleware("user", "alice"))

    @app.route("/hello")
    def hello(ctx):
        return f"Hello {ctx.state.get('user')}"

    ctx = RequestContext("/hello")
    app.handle(ctx)
    assert ctx.response_status == 200
    assert ctx.response_body == "Hello alice"
    assert ctx.state.get("user_ended") is True
    assert audit == ["REQ:GET:/hello", "RES:200"]

    # 404 route
    ctx404 = RequestContext("/missing")
    app.handle(ctx404)
    assert ctx404.response_status == 404
    assert ctx404.aborted is True
"""
}

t1008_ref = {
    "pipeline.py": """class MiddlewarePipeline:
    \"\"\"Executes middleware in onion order: process_request forwards, process_response in reverse.\"\"\"

    def __init__(self, middlewares=None):
        self.middlewares = list(middlewares or [])

    def add(self, mw):
        self.middlewares.append(mw)

    def execute(self, ctx, handler):
        \"\"\"Run request phases forwards, invoke handler, then run response phases in reverse.
        If ctx.abort() is called during request phase, stop calling subsequent request hooks,
        but DO execute process_response on all middleware that already processed the request, in reverse order.\"\"\"
        entered = []
        for mw in self.middlewares:
            entered.append(mw)
            mw.process_request(ctx)
            if ctx.aborted:
                break

        if not ctx.aborted:
            handler(ctx)

        for mw in reversed(entered):
            mw.process_response(ctx)

        return ctx
"""
}

register_task(
    tid=1008,
    name="Middleware Pipeline Onion Architecture",
    issue=t1008_issue,
    repo=t1008_repo,
    hidden=t1008_hidden,
    ref=t1008_ref,
)


# ==============================================================================
# Task 1009: Token Bucket Rate Limiter with Monotonic Clock (4 files)
# ==============================================================================
t1009_issue = (
    "Bug report: In the rate limiter, high-frequency consumers are being starved because fractional token refills "
    "are truncated to whole integers upon each acquisition check. When a caller requests more tokens than the bucket's "
    "total capacity, it returns False instead of raising ValueError as specified in the docstring. Also, pruning stale keys "
    "deletes active keys when timestamps roll over. Fix bucket.py and limiter.py. Do not change the tests."
)

t1009_repo = {
    "storage.py": """class MemoryStore:
    \"\"\"In-memory store for bucket states: key -> (tokens, last_updated).\"\"\"

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)

    def keys(self):
        return list(self._data.keys())
""",
    "bucket.py": """class TokenBucket:
    \"\"\"Token bucket rate limiter with continuous replenishment.\"\"\"

    def __init__(self, capacity, refill_rate, tokens=None, last_updated=0.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity if tokens is None else tokens)
        self.last_updated = float(last_updated)

    def refill(self, now):
        elapsed = max(0.0, now - self.last_updated)
        self.last_updated = now
        # Buggy: int truncation loses fractional refills on frequent calls
        added = int(elapsed * self.refill_rate)
        self.tokens = min(self.capacity, self.tokens + added)

    def acquire(self, tokens, now):
        \"\"\"Attempts to consume tokens at time `now`.
        Returns (allowed: bool, wait_time: float).
        Raises ValueError if `tokens` <= 0 or `tokens` > self.capacity.\"\"\"
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        # Buggy: fails to raise ValueError if tokens > capacity
        self.refill(now)
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, 0.0
        missing = tokens - self.tokens
        wait_time = missing / self.refill_rate
        return False, wait_time
""",
    "limiter.py": """from bucket import TokenBucket
from storage import MemoryStore


class RateLimiter:
    def __init__(self, default_capacity=10, default_refill_rate=1.0, ttl=3600, store=None):
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate
        self.ttl = ttl
        self.store = store or MemoryStore()

    def allow(self, key, tokens=1, now=0.0):
        entry = self.store.get(key)
        if entry is None:
            bucket = TokenBucket(self.default_capacity, self.default_refill_rate, last_updated=now)
        else:
            tok, last_t = entry
            bucket = TokenBucket(self.default_capacity, self.default_refill_rate, tokens=tok, last_updated=last_t)

        allowed, wait_time = bucket.acquire(tokens, now)
        self.store.set(key, (bucket.tokens, bucket.last_updated))
        return allowed, wait_time

    def prune_stale(self, now):
        \"\"\"Prune buckets that have been inactive for more than self.ttl.\"\"\"
        for k in self.store.keys():
            entry = self.store.get(k)
            if entry and (now - entry[1]) > self.ttl:
                self.store.delete(k)
""",
    "tests/test_limiter.py": """from limiter import RateLimiter


def test_basic_limit():
    limiter = RateLimiter(default_capacity=2, default_refill_rate=1.0)
    ok1, _ = limiter.allow("user1", 1, now=100.0)
    ok2, _ = limiter.allow("user1", 1, now=100.0)
    ok3, wait = limiter.allow("user1", 1, now=100.0)
    assert ok1 is True and ok2 is True and ok3 is False
    assert wait == 1.0
""",
}

t1009_hidden = {
    "tests/test_hidden_limiter.py": """import pytest
from bucket import TokenBucket
from limiter import RateLimiter
from storage import MemoryStore


def test_fractional_refill_preservation():
    bucket = TokenBucket(capacity=10.0, refill_rate=1.0, tokens=0.0, last_updated=0.0)
    # 10 calls with 0.1s step should accumulate 1.0 token total, not 0.0
    for i in range(1, 11):
        bucket.refill(now=i * 0.1)
    assert bucket.tokens == pytest.approx(1.0, 1e-5)


def test_cost_exceeds_capacity_raises():
    bucket = TokenBucket(capacity=5.0, refill_rate=1.0)
    with pytest.raises(ValueError, match="capacity"):
        bucket.acquire(6.0, now=0.0)
    with pytest.raises(ValueError):
        bucket.acquire(0, now=0.0)
    with pytest.raises(ValueError):
        bucket.acquire(-1.0, now=0.0)


def test_limiter_prune_and_ttl():
    limiter = RateLimiter(default_capacity=5, default_refill_rate=1.0, ttl=60.0)
    limiter.allow("active", 1, now=100.0)
    limiter.allow("stale", 1, now=10.0)

    limiter.prune_stale(now=100.0)
    assert limiter.store.get("active") is not None
    assert limiter.store.get("stale") is None


def test_wait_time_calculation():
    limiter = RateLimiter(default_capacity=10, default_refill_rate=2.0)
    ok, _ = limiter.allow("u1", 10, now=0.0)
    assert ok is True
    # Needs 4 tokens, refill rate is 2 tok/s -> wait 2.0s
    ok, wait = limiter.allow("u1", 4, now=0.0)
    assert ok is False
    assert wait == pytest.approx(2.0, 1e-5)
    # After 1.5s, 3 tokens generated. 1 token missing -> wait 0.5s
    ok, wait2 = limiter.allow("u1", 4, now=1.5)
    assert ok is False
    assert wait2 == pytest.approx(0.5, 1e-5)
"""
}

t1009_ref = {
    "bucket.py": """class TokenBucket:
    \"\"\"Token bucket rate limiter with continuous replenishment.\"\"\"

    def __init__(self, capacity, refill_rate, tokens=None, last_updated=0.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity if tokens is None else tokens)
        self.last_updated = float(last_updated)

    def refill(self, now):
        elapsed = max(0.0, now - self.last_updated)
        self.last_updated = now
        added = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added)

    def acquire(self, tokens, now):
        \"\"\"Attempts to consume tokens at time `now`.
        Returns (allowed: bool, wait_time: float).
        Raises ValueError if `tokens` <= 0 or `tokens` > self.capacity.\"\"\"
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"tokens {tokens} exceeds capacity {self.capacity}")
        self.refill(now)
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, 0.0
        missing = tokens - self.tokens
        wait_time = missing / self.refill_rate
        return False, wait_time
"""
}

register_task(
    tid=1009,
    name="Token Bucket Rate Limiter with Monotonic Clock",
    issue=t1009_issue,
    repo=t1009_repo,
    hidden=t1009_hidden,
    ref=t1009_ref,
)


# ==============================================================================
# Task 1010: Prioritized Event Dispatcher with Cancellation (4 files)
# ==============================================================================
t1010_issue = (
    "Bug report: In event_dispatcher, calling event.stop_propagation() stops lower priority listeners, but fails to stop "
    "subsequent listeners registered at the same priority level. Additionally, unsubscribing a listener inside a handler "
    "during dispatch raises RuntimeError: dictionary changed size during iteration or skips listeners. Equal-priority "
    "listeners also reverse execution order. Fix dispatcher.py and event.py. Do not change the tests."
)

t1010_repo = {
    "event.py": """class Event:
    \"\"\"Event object passed to subscribers.\"\"\"

    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}
        self.cancelled = False

    def stop_propagation(self):
        \"\"\"Halt dispatching to all subsequent subscribers immediately.\"\"\"
        self.cancelled = True
""",
    "subscriber.py": """class Subscriber:
    def __init__(self, handler, priority=0, once=False):
        self.handler = handler
        self.priority = int(priority)
        self.once = bool(once)
""",
    "dispatcher.py": """from subscriber import Subscriber


class EventDispatcher:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, name, handler, priority=0, once=False):
        sub = Subscriber(handler, priority, once)
        self._subscribers.setdefault(name, []).append(sub)
        return sub

    def unsubscribe(self, name, handler):
        if name in self._subscribers:
            self._subscribers[name] = [
                s for s in self._subscribers[name] if s.handler != handler
            ]

    def dispatch(self, event):
        \"\"\"Dispatch event to subscribers sorted by priority (descending).
        Equal priority subscribers must execute in FIFO order.
        If event.cancelled is set, halt execution immediately.\"\"\"
        subs = self._subscribers.get(event.name, [])
        # Buggy: sorts descending by priority but does not ensure stable FIFO tie-breaking
        sorted_subs = sorted(subs, key=lambda s: s.priority, reverse=True)

        for s in sorted_subs:
            # Buggy: only checks cancelled between priority levels instead of before each handler
            s.handler(event)
            if s.once:
                self.unsubscribe(event.name, s.handler)
            if event.cancelled:
                break
""",
    "tests/test_dispatcher.py": """from event import Event
from dispatcher import EventDispatcher


def test_basic_dispatch():
    d = EventDispatcher()
    calls = []
    d.subscribe("ping", lambda e: calls.append(e.data.get("v")))
    d.dispatch(Event("ping", {"v": 42}))
    assert calls == [42]
""",
}

t1010_hidden = {
    "tests/test_hidden_dispatcher.py": """import pytest
from event import Event
from dispatcher import EventDispatcher


def test_stop_propagation_halts_same_priority():
    d = EventDispatcher()
    calls = []

    def h1(e):
        calls.append("h1")
        e.stop_propagation()

    def h2(e):
        calls.append("h2")

    d.subscribe("order", h1, priority=10)
    d.subscribe("order", h2, priority=10)

    ev = Event("order")
    d.dispatch(ev)
    assert calls == ["h1"]
    assert ev.cancelled is True


def test_stable_fifo_for_equal_priorities():
    d = EventDispatcher()
    calls = []
    d.subscribe("ev", lambda e: calls.append(1), priority=5)
    d.subscribe("ev", lambda e: calls.append(2), priority=10)
    d.subscribe("ev", lambda e: calls.append(3), priority=5)
    d.subscribe("ev", lambda e: calls.append(4), priority=5)

    d.dispatch(Event("ev"))
    # Priority 10 first, then priority 5 in order 1, 3, 4
    assert calls == [2, 1, 3, 4]


def test_unsubscribe_during_dispatch():
    d = EventDispatcher()
    calls = []

    def h_remover(e):
        calls.append("remover")
        d.unsubscribe("test", h_target)

    def h_target(e):
        calls.append("target")

    def h_after(e):
        calls.append("after")

    d.subscribe("test", h_remover, priority=10)
    d.subscribe("test", h_target, priority=5)
    d.subscribe("test", h_after, priority=1)

    # h_target should not be called because it was unsubscribed before its turn
    d.dispatch(Event("test"))
    assert calls == ["remover", "after"]


def test_once_listener():
    d = EventDispatcher()
    calls = []
    d.subscribe("init", lambda e: calls.append(1), once=True)

    d.dispatch(Event("init"))
    d.dispatch(Event("init"))
    assert calls == [1]
"""
}

t1010_ref = {
    "dispatcher.py": """from subscriber import Subscriber


class EventDispatcher:
    def __init__(self):
        self._subscribers = {}
        self._counter = 0

    def subscribe(self, name, handler, priority=0, once=False):
        self._counter += 1
        sub = Subscriber(handler, priority, once)
        sub._seq = self._counter
        self._subscribers.setdefault(name, []).append(sub)
        return sub

    def unsubscribe(self, name, handler):
        if name in self._subscribers:
            self._subscribers[name] = [
                s for s in self._subscribers[name] if s.handler != handler
            ]

    def dispatch(self, event):
        \"\"\"Dispatch event to subscribers sorted by priority (descending).
        Equal priority subscribers must execute in FIFO order.
        If event.cancelled is set, halt execution immediately.\"\"\"
        subs = list(self._subscribers.get(event.name, []))
        # Stable sort: priority descending (-priority), insertion sequence ascending (_seq)
        sorted_subs = sorted(subs, key=lambda s: (-s.priority, getattr(s, "_seq", 0)))

        for s in sorted_subs:
            if event.cancelled:
                break
            # Check if subscriber was removed during earlier handlers
            current_active = self._subscribers.get(event.name, [])
            if s not in current_active:
                continue

            s.handler(event)
            if s.once:
                self.unsubscribe(event.name, s.handler)
            if event.cancelled:
                break
"""
}

register_task(
    tid=1010,
    name="Prioritized Event Dispatcher with Cancellation",
    issue=t1010_issue,
    repo=t1010_repo,
    hidden=t1010_hidden,
    ref=t1010_ref,
)


# ==============================================================================
# Task 1011: KV Storage Engine with Write-Ahead Log (WAL) & Compaction (5 files)
# ==============================================================================
t1011_issue = (
    "Bug report: In the KV storage engine, replaying the write-ahead log during recovery ignores tombstone (DEL) "
    "records, causing deleted keys to reappear after recovery. Furthermore, compaction crashes when tombstones are "
    "encountered, and calling delete on a key that does not exist raises KeyError instead of being a no-op. Fix "
    "wal.py and engine.py. Do not change the tests."
)

t1011_repo = {
    "wal.py": """def serialize_entry(op, key, val=""):
    \"\"\"Serialize WAL entry: OP KEY [VAL]\\n\"\"\"
    if op == "DEL":
        return f"DEL {key}\\n"
    return f"SET {key} {val}\\n"


def parse_entry(line):
    \"\"\"Parse a WAL line into (op, key, val).\"\"\"
    parts = line.rstrip("\\r\\n").split(" ", 2)
    if not parts or parts[0] == "":
        return None
    op = parts[0]
    key = parts[1]
    val = parts[2] if len(parts) > 2 else ""
    return op, key, val
""",
    "memtable.py": """class MemTable:
    \"\"\"In-memory active key-value store.\"\"\"

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, val):
        self._data[key] = val

    def delete(self, key):
        self._data.pop(key, None)

    def items(self):
        return dict(self._data).items()

    def clear(self):
        self._data.clear()
""",
    "snapshot.py": """class Snapshot:
    def __init__(self, data):
        self._data = dict(data)

    def get(self, key):
        return self._data.get(key)
""",
    "engine.py": """import os
from memtable import MemTable
from snapshot import Snapshot
from wal import serialize_entry, parse_entry


class KVEngine:
    \"\"\"Key-Value engine backed by append-only Write-Ahead Log.\"\"\"

    def __init__(self, wal_path):
        self.wal_path = wal_path
        self.memtable = MemTable()
        self._recover()

    def _recover(self):
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                res = parse_entry(line)
                if not res:
                    continue
                op, k, v = res
                if op == "SET":
                    self.memtable.set(k, v)
                # Buggy: fails to handle op == 'DEL', so deleted keys resurrect!

    def get(self, key):
        return self.memtable.get(key)

    def set(self, key, val):
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(serialize_entry("SET", key, str(val)))
        self.memtable.set(key, str(val))

    def delete(self, key):
        # Buggy: raises KeyError if key not in memtable
        if self.memtable.get(key) is None:
            raise KeyError(key)
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(serialize_entry("DEL", key))
        self.memtable.delete(key)

    def snapshot(self):
        return Snapshot(dict(self.memtable.items()))

    def compact(self):
        \"\"\"Compacts WAL by rewriting only live keys to a new log file.\"\"\"
        tmp_path = self.wal_path + ".compact"
        with open(tmp_path, "w", encoding="utf-8") as f:
            for k, v in self.memtable.items():
                f.write(serialize_entry("SET", k, v))
        os.replace(tmp_path, self.wal_path)
""",
    "tests/test_engine.py": """import tempfile, os
from engine import KVEngine


def test_basic_crud():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        wal_path = tf.name
    try:
        engine = KVEngine(wal_path)
        engine.set("k1", "v1")
        assert engine.get("k1") == "v1"
        engine.delete("k1")
        assert engine.get("k1") is None
    finally:
        if os.path.exists(wal_path):
            os.remove(wal_path)
""",
}

t1011_hidden = {
    "tests/test_hidden_engine.py": """import tempfile, os
import pytest
from engine import KVEngine


def test_recovery_applies_tombstones():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        wal = tf.name
    try:
        e1 = KVEngine(wal)
        e1.set("alive", "yes")
        e1.set("dead", "no")
        e1.delete("dead")
        assert e1.get("dead") is None

        # Reopen from disk (recovery replay)
        e2 = KVEngine(wal)
        assert e2.get("alive") == "yes"
        assert e2.get("dead") is None, "Tombstone was not applied during recovery!"
    finally:
        if os.path.exists(wal):
            os.remove(wal)


def test_delete_missing_key_is_noop():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        wal = tf.name
    try:
        e = KVEngine(wal)
        # Should not raise KeyError
        e.delete("nonexistent_key")
        assert e.get("nonexistent_key") is None
    finally:
        if os.path.exists(wal):
            os.remove(wal)


def test_snapshot_isolation_and_compaction():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        wal = tf.name
    try:
        e = KVEngine(wal)
        e.set("a", "1")
        e.set("b", "2")
        snap = e.snapshot()

        e.set("a", "100")
        e.delete("b")

        # Snapshot retains point-in-time view
        assert snap.get("a") == "1"
        assert snap.get("b") == "2"
        assert e.get("a") == "100"
        assert e.get("b") is None

        # Compaction
        e.compact()
        e_after = KVEngine(wal)
        assert e_after.get("a") == "100"
        assert e_after.get("b") is None
    finally:
        if os.path.exists(wal):
            os.remove(wal)
"""
}

t1011_ref = {
    "engine.py": """import os
from memtable import MemTable
from snapshot import Snapshot
from wal import serialize_entry, parse_entry


class KVEngine:
    \"\"\"Key-Value engine backed by append-only Write-Ahead Log.\"\"\"

    def __init__(self, wal_path):
        self.wal_path = wal_path
        self.memtable = MemTable()
        self._recover()

    def _recover(self):
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                res = parse_entry(line)
                if not res:
                    continue
                op, k, v = res
                if op == "SET":
                    self.memtable.set(k, v)
                elif op == "DEL":
                    self.memtable.delete(k)

    def get(self, key):
        return self.memtable.get(key)

    def set(self, key, val):
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(serialize_entry("SET", key, str(val)))
        self.memtable.set(key, str(val))

    def delete(self, key):
        with open(self.wal_path, "a", encoding="utf-8") as f:
            f.write(serialize_entry("DEL", key))
        self.memtable.delete(key)

    def snapshot(self):
        return Snapshot(dict(self.memtable.items()))

    def compact(self):
        \"\"\"Compacts WAL by rewriting only live keys to a new log file.\"\"\"
        tmp_path = self.wal_path + ".compact"
        with open(tmp_path, "w", encoding="utf-8") as f:
            for k, v in self.memtable.items():
                f.write(serialize_entry("SET", k, v))
        os.replace(tmp_path, self.wal_path)
"""
}

register_task(
    tid=1011,
    name="KV Storage Engine with Write-Ahead Log (WAL) & Compaction",
    issue=t1011_issue,
    repo=t1011_repo,
    hidden=t1011_hidden,
    ref=t1011_ref,
)


# ==============================================================================
# Task 1012: Distributed Lease & Fencing Token Manager (4 files)
# ==============================================================================
t1012_issue = (
    "Bug report: In the distributed lease manager, attempting to renew an expired lease incorrectly re-acquires "
    "the lock instead of raising LeaseExpiredError. Furthermore, fencing tokens do not strictly increase upon renewal, "
    "and an unauthorized holder can release a lease belonging to another client. Fix manager.py and lease.py. "
    "Do not change the tests."
)

t1012_repo = {
    "clock.py": """class MockClock:
    \"\"\"Monotonic clock for deterministic testing.\"\"\"

    def __init__(self, initial=0.0):
        self._now = float(initial)

    def now(self):
        return self._now

    def advance(self, seconds):
        self._now += float(seconds)
        return self._now
""",
    "lease.py": """class LeaseExpiredError(Exception):
    \"\"\"Raised when renewing a lease that has already expired.\"\"\"
    pass


class Lease:
    def __init__(self, resource, holder, expires_at, fencing_token):
        self.resource = resource
        self.holder = holder
        self.expires_at = float(expires_at)
        self.fencing_token = int(fencing_token)

    def is_valid(self, now):
        \"\"\"Lease is valid strictly if now < expires_at.\"\"\"
        return now < self.expires_at
""",
    "manager.py": """from clock import MockClock
from lease import Lease, LeaseExpiredError


class LeaseManager:
    \"\"\"Manages distributed resource leases with monotonic fencing tokens.\"\"\"

    def __init__(self, clock=None, default_ttl=30.0):
        self.clock = clock or MockClock()
        self.default_ttl = float(default_ttl)
        self._leases = {}
        self._token_seq = 0

    def acquire(self, resource, holder, ttl=None):
        \"\"\"Acquire lease if free or expired. Returns Lease or None if held by another.\"\"\"
        now = self.clock.now()
        cur = self._leases.get(resource)
        if cur and cur.is_valid(now) and cur.holder != holder:
            return None

        self._token_seq += 1
        dur = float(ttl or self.default_ttl)
        lease = Lease(resource, holder, now + dur, self._token_seq)
        self._leases[resource] = lease
        return lease

    def renew(self, resource, holder, ttl=None):
        \"\"\"Extend existing lease. Raises LeaseExpiredError if lease expired or missing.\"\"\"
        now = self.clock.now()
        cur = self._leases.get(resource)
        # Buggy: fails to raise LeaseExpiredError if expired or wrong holder, silently re-acquires
        if cur is None:
            return self.acquire(resource, holder, ttl)

        dur = float(ttl or self.default_ttl)
        # Buggy: fails to increment fencing token on renewal
        cur.expires_at = now + dur
        return cur

    def release(self, resource, holder):
        \"\"\"Release active lease. Returns True if released, False otherwise.\"\"\"
        cur = self._leases.get(resource)
        # Buggy: does not verify that holder matches!
        if cur:
            del self._leases[resource]
            return True
        return False
""",
    "tests/test_lease.py": """from clock import MockClock
from manager import LeaseManager


def test_basic_acquire():
    clock = MockClock(0.0)
    lm = LeaseManager(clock, default_ttl=10.0)
    lease = lm.acquire("res1", "clientA")
    assert lease is not None
    assert lease.is_valid(clock.now()) is True
    assert lease.fencing_token == 1
""",
}

t1012_hidden = {
    "tests/test_hidden_lease.py": """import pytest
from clock import MockClock
from lease import LeaseExpiredError
from manager import LeaseManager


def test_fencing_token_monotonically_increases_on_renew():
    clock = MockClock(100.0)
    lm = LeaseManager(clock, default_ttl=10.0)
    l1 = lm.acquire("doc", "worker1")
    t1 = l1.fencing_token

    clock.advance(5.0)
    l2 = lm.renew("doc", "worker1")
    assert l2.fencing_token > t1, "Fencing token must increment on renewal!"


def test_renew_expired_raises_error():
    clock = MockClock(0.0)
    lm = LeaseManager(clock, default_ttl=10.0)
    lm.acquire("res", "worker1")

    # Advance past expiration (10.0s)
    clock.advance(10.1)
    with pytest.raises(LeaseExpiredError):
        lm.renew("res", "worker1")


def test_renew_wrong_holder_raises_error():
    clock = MockClock(0.0)
    lm = LeaseManager(clock, default_ttl=10.0)
    lm.acquire("res", "worker1")

    with pytest.raises(LeaseExpiredError):
        lm.renew("res", "impostor")


def test_release_authorization():
    clock = MockClock(0.0)
    lm = LeaseManager(clock, default_ttl=10.0)
    lm.acquire("lock", "worker1")

    # Impostor cannot release
    assert lm.release("lock", "worker2") is False
    assert lm.acquire("lock", "worker2") is None  # Still held by worker1

    # Worker1 can release
    assert lm.release("lock", "worker1") is True
    assert lm.acquire("lock", "worker2") is not None
"""
}

t1012_ref = {
    "manager.py": """from clock import MockClock
from lease import Lease, LeaseExpiredError


class LeaseManager:
    \"\"\"Manages distributed resource leases with monotonic fencing tokens.\"\"\"

    def __init__(self, clock=None, default_ttl=30.0):
        self.clock = clock or MockClock()
        self.default_ttl = float(default_ttl)
        self._leases = {}
        self._token_seq = 0

    def acquire(self, resource, holder, ttl=None):
        \"\"\"Acquire lease if free or expired. Returns Lease or None if held by another.\"\"\"
        now = self.clock.now()
        cur = self._leases.get(resource)
        if cur and cur.is_valid(now) and cur.holder != holder:
            return None

        self._token_seq += 1
        dur = float(ttl or self.default_ttl)
        lease = Lease(resource, holder, now + dur, self._token_seq)
        self._leases[resource] = lease
        return lease

    def renew(self, resource, holder, ttl=None):
        \"\"\"Extend existing lease. Raises LeaseExpiredError if lease expired or missing.\"\"\"
        now = self.clock.now()
        cur = self._leases.get(resource)
        if cur is None or not cur.is_valid(now) or cur.holder != holder:
            raise LeaseExpiredError(f"Lease for {resource} has expired or is not held by {holder}")

        self._token_seq += 1
        dur = float(ttl or self.default_ttl)
        cur.expires_at = now + dur
        cur.fencing_token = self._token_seq
        return cur

    def release(self, resource, holder):
        \"\"\"Release active lease. Returns True if released, False otherwise.\"\"\"
        now = self.clock.now()
        cur = self._leases.get(resource)
        if cur and cur.holder == holder and cur.is_valid(now):
            del self._leases[resource]
            return True
        return False
"""
}

register_task(
    tid=1012,
    name="Distributed Lease & Fencing Token Manager",
    issue=t1012_issue,
    repo=t1012_repo,
    hidden=t1012_hidden,
    ref=t1012_ref,
)

if __name__ == "__main__":
    print(f"suite_e4 loaded successfully with {len(T)} tasks:")
    for t in T:
        print(f"Task {t['id']}: {t['name']} ({len(t['repo'])} files)")
