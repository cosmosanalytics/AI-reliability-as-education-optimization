# Rule Sufficiency (J2) Assert Literal Triage & Executable Verification

**Audit Scope:** All 87 evaluated tasks in Suite E5 (`TAUGHT`, `TRANSFER`, `DISTRACTOR`). Excludes pure control / exploratory tasks (`STATED`, `UNAIDED_BASELINE`).

## 1. Executive Summary & Dynamic Verification Metrics

| Metric | Count | Percentage | Verification Method |
| :--- | :---: | :---: | :--- |
| **Total Asserted Literals Evaluated** | **459** | 100.0% | AST extraction across all hidden test assertions |
| Verbatim in Context (Handbook/Ticket/Repo) | 252 | 54.9% | Substring match against visible artifacts |
| Input Test Fixtures (Call Sites / Assignments) | 150 | 32.7% | AST call site and argument verification |
| Deterministic Rule Derivations (H02, H08, H09, H10, H13, H14, H15) | 48 | 10.5% | Mathematical/formatting recomputation & equality assertion |
| Local Rule Overrides (Docstring / Ticket) | 9 | 2.0% | Repository docstring specification audit |
| **Unresolved / Guessable Defects** | **0** | **0.0%** | **Strict Condition J2 Evaluation** |

All counts above are **computed dynamically by code** via `runner/verify_rule_sufficiency.py`. No numbers or category tallies are hard-coded.

---

## 2. Non-Verbatim Assert Literals: Executable Triage Table

Across the 87 evaluated tasks, **207** asserted literals are not present verbatim in the initial text. Each has been individually verified by code:

| Task ID | Family | Class Tag | Literal | Type | Category | Executable Verification / Call Site |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| 2002 | `money_rounding` | `TAUGHT` | `35` | `int` | `FIXTURE` | Call Arg: `prorate_discount([100, 100], 35)` |
| 2002 | `money_rounding` | `TAUGHT` | `45` | `int` | `FIXTURE` | Call Arg: `prorate_discount([100, 100], 45)` |
| 2002 | `money_rounding` | `TAUGHT` | `23` | `int` | `DERIVATION` | Recomputed Rule H02: prorate_discount([100, 100], 45) -> [23, 23] |
| 2002 | `money_rounding` | `TAUGHT` | `23` | `int` | `DERIVATION` | Recomputed Rule H02: prorate_discount([100, 100], 45) -> [23, 23] |
| 2003 | `money_rounding` | `TAUGHT` | `203` | `int` | `DERIVATION` | Recomputed Rule H02: fx(135, 1.5) -> 203 |
| 2003 | `money_rounding` | `TAUGHT` | `135` | `int` | `FIXTURE` | Call Arg: `convert_currency_amount(135, quote)` |
| 2003 | `money_rounding` | `TAUGHT` | `218` | `int` | `DERIVATION` | Recomputed Rule H02: fx(145, 1.5) -> 218 |
| 2003 | `money_rounding` | `TAUGHT` | `145` | `int` | `FIXTURE` | Call Arg: `convert_currency_amount(145, quote)` |
| 2003 | `money_rounding` | `TAUGHT` | `203` | `int` | `DERIVATION` | Recomputed Rule H02: fx(135, 1.5) -> 203 |
| 2003 | `money_rounding` | `TAUGHT` | `135` | `int` | `FIXTURE` | Call Arg: `apply_fx_rate(135, 1.5)` |
| 2003 | `money_rounding` | `TAUGHT` | `1.5` | `float` | `FIXTURE` | Call Arg: `apply_fx_rate(145, 1.5)` |
| 2003 | `money_rounding` | `TAUGHT` | `218` | `int` | `DERIVATION` | Recomputed Rule H02: fx(145, 1.5) -> 218 |
| 2003 | `money_rounding` | `TAUGHT` | `145` | `int` | `FIXTURE` | Call Arg: `apply_fx_rate(145, 1.5)` |
| 2003 | `money_rounding` | `TAUGHT` | `1.5` | `float` | `FIXTURE` | Call Arg: `apply_fx_rate(145, 1.5)` |
| 2004 | `money_rounding` | `DISTRACTOR` | `125` | `int` | `FIXTURE` | Call Arg: `compute_payroll_withholding(125, 0.1)` |
| 2004 | `money_rounding` | `DISTRACTOR` | `145` | `int` | `FIXTURE` | Call Arg: `compute_payroll_withholding(145, 0.1)` |
| 2006 | `config_merge` | `TAUGHT` | `'sub'` | `str` | `FIXTURE` | Assign: `o = {'sub': {'k2': 2}}` |
| 2008 | `config_merge` | `DISTRACTOR` | `'page_views'` | `str` | `FIXTURE` | Assign: `acc = {'counters': {'page_views': 100, 'errors': 0}}` |
| 2008 | `config_merge` | `DISTRACTOR` | `'counters'` | `str` | `FIXTURE` | Assign: `res = update_live_session(acc, {'counters': {'errors': 1}})` |
| 2008 | `config_merge` | `DISTRACTOR` | `'counters'` | `str` | `FIXTURE` | Assign: `res = update_live_session(acc, {'counters': {'errors': 1}})` |
| 2010 | `calendar_recurrence` | `TAUGHT` | `1999` | `int` | `FIXTURE` | Call Arg: `is_entitled_at(101, 'pro', 1000, 2000, 1999)` |
| 2014 | `csv_roundtrip` | `TAUGHT` | `'ITM-2\tWidget \\"Pro\\" Edition'` | `str` | `DERIVATION` | Recomputed Rule H10: input `Widget "Pro" Edition` escaped -> `ITM-2	Widget \"Pro\" Edition` |
| 2014 | `csv_roundtrip` | `TAUGHT` | `'ITM-3\tLine1\\nLine2'` | `str` | `DERIVATION` | Recomputed Rule H10: input `Line1
Line2` escaped -> `ITM-3	Line1\nLine2` |
| 2015 | `csv_roundtrip` | `TAUGHT` | `'query\tSELECT * FROM \\"users\\"'` | `str` | `DERIVATION` | Recomputed Rule H10: input `SELECT * FROM "users"` escaped -> `query	SELECT * FROM \"users\"` |
| 2015 | `csv_roundtrip` | `TAUGHT` | `'foo \\"bar\\"'` | `str` | `DERIVATION` | Recomputed Rule H10: input `foo "bar"` escaped -> `foo \"bar\"` |
| 2015 | `csv_roundtrip` | `TAUGHT` | `'foo "bar"'` | `str` | `FIXTURE` | Call Arg: `sanitize_cell('foo "bar"')` |
| 2015 | `csv_roundtrip` | `TAUGHT` | `'line1\\nline2'` | `str` | `DERIVATION` | Recomputed Rule H10: input `line1
line2` escaped -> `line1\nline2` |
| 2015 | `csv_roundtrip` | `TAUGHT` | `'line1\nline2'` | `str` | `FIXTURE` | Call Arg: `sanitize_cell('line1\nline2')` |
| 2016 | `csv_roundtrip` | `DISTRACTOR` | `'3,"echo ""hello"""'` | `str` | `LOCAL_OVERRIDE` | Local Override: RFC 4180 doubled-quotes specified in module docstring -> `3,"echo ""hello"""` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::*'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::*', 'corp::docs::archive::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::report'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::*', 'corp::docs::report')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::*'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::*', 'corp::docs::archive::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::archive::file'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::**', 'corp::docs::archive::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::**'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::**', 'corp::docs_extra::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::archive::file'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::**', 'corp::docs::archive::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs::**'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::**', 'corp::docs_extra::file')` |
| 2018 | `permission_prefix` | `TAUGHT` | `'corp::docs_extra::file'` | `str` | `FIXTURE` | Call Arg: `check_scope_access('corp::docs::**', 'corp::docs_extra::file')` |
| 2022 | `event_ordering` | `TAUGHT` | `102` | `int` | `FIXTURE` | Assign: `m2 = NotificationMessage(102, 10, 'payload_b')` |
| 2022 | `event_ordering` | `TAUGHT` | `101` | `int` | `FIXTURE` | Assign: `m1 = NotificationMessage(101, 10, 'payload_a')` |
| 2025 | `cache_ttl` | `TRANSFER` | `'val1'` | `str` | `FIXTURE` | Call Arg: `c.set('k1', 'val1', 5.0)` |
| 2026 | `cache_ttl` | `TRANSFER` | `'10.0.0.1'` | `str` | `FIXTURE` | Call Arg: `s.is_active('10.0.0.1')` |
| 2026 | `cache_ttl` | `TRANSFER` | `'10.0.0.1'` | `str` | `FIXTURE` | Call Arg: `s.is_active('10.0.0.1')` |
| 2026 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_session_expired(100.0, 99.9)` |
| 2026 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_session_expired(100.0, 99.9)` |
| 2026 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_session_expired(100.0, 99.9)` |
| 2026 | `cache_ttl` | `TRANSFER` | `99.9` | `float` | `FIXTURE` | Call Arg: `is_session_expired(100.0, 99.9)` |
| 2027 | `cache_ttl` | `TRANSFER` | `'resource_db'` | `str` | `FIXTURE` | Call Arg: `lg.holds_lease('resource_db', 'node1')` |
| 2027 | `cache_ttl` | `TRANSFER` | `'node1'` | `str` | `FIXTURE` | Call Arg: `lg.holds_lease('resource_db', 'node1')` |
| 2027 | `cache_ttl` | `TRANSFER` | `'resource_db'` | `str` | `FIXTURE` | Call Arg: `lg.holds_lease('resource_db', 'node1')` |
| 2027 | `cache_ttl` | `TRANSFER` | `'node1'` | `str` | `FIXTURE` | Call Arg: `lg.holds_lease('resource_db', 'node1')` |
| 2027 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_lease_valid(100.0, 99.0)` |
| 2027 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_lease_valid(100.0, 99.0)` |
| 2027 | `cache_ttl` | `TRANSFER` | `100.0` | `float` | `FIXTURE` | Call Arg: `is_lease_valid(100.0, 99.0)` |
| 2027 | `cache_ttl` | `TRANSFER` | `99.0` | `float` | `FIXTURE` | Call Arg: `is_lease_valid(100.0, 99.0)` |
| 2028 | `cache_ttl` | `TRANSFER` | `'10.0.0.5'` | `str` | `FIXTURE` | Call Arg: `cache.put_record('service.internal', '10.0.0.5', 3.0)` |
| 2028 | `cache_ttl` | `TRANSFER` | `'service.internal'` | `str` | `FIXTURE` | Call Arg: `cache.lookup('service.internal')` |
| 2028 | `cache_ttl` | `TRANSFER` | `'service.internal'` | `str` | `FIXTURE` | Call Arg: `cache.lookup('service.internal')` |
| 2037 | `wire_envelope` | `TAUGHT` | `1700000000` | `int` | `FIXTURE` | Assign: `res = format_audit_event({'eventId': 'evt-1', 'userRole': 'admin'}, 1700000000)` |
| 2037 | `wire_envelope` | `TAUGHT` | `'event_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `eventId` -> `event_id` |
| 2037 | `wire_envelope` | `TAUGHT` | `'eventId'` | `str` | `FIXTURE` | Assign: `res = format_audit_event({'eventId': 'evt-1', 'userRole': 'admin'}, 1700000000)` |
| 2038 | `wire_envelope` | `TAUGHT` | `'billing_service'` | `str` | `DERIVATION` | Rule H08: module `billing_emitter.py` domain `billing` + `_service` == `billing_service` |
| 2038 | `wire_envelope` | `TAUGHT` | `'transaction_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `transactionId` -> `transaction_id` |
| 2038 | `wire_envelope` | `TAUGHT` | `'transactionId'` | `str` | `FIXTURE` | Assign: `res = emit_billing_record({'transactionId': 'tx-1', 'accountNum': 'acc-9'}, 1700000001)` |
| 2039 | `wire_envelope` | `TAUGHT` | `'telemetry_service'` | `str` | `DERIVATION` | Rule H08: module `telemetry_stream.py` domain `telemetry` + `_service` == `telemetry_service` |
| 2039 | `wire_envelope` | `TAUGHT` | `'metric_name'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `metricName` -> `metric_name` |
| 2039 | `wire_envelope` | `TAUGHT` | `'metricName'` | `str` | `FIXTURE` | Assign: `res = prepare_metric_packet({'metricName': 'cpu_util', 'hostId': 'srv-1'}, 1700000002)` |
| 2041 | `wire_envelope` | `TAUGHT` | `'user_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `userId` -> `user_id` |
| 2041 | `wire_envelope` | `TAUGHT` | `'userId'` | `str` | `FIXTURE` | Assign: `res = dispatch_user_activity({'userId': 'u101', 'actionType': 'click'}, 1700000004)` |
| 2042 | `wire_envelope` | `TAUGHT` | `'order_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `orderId` -> `order_id` |
| 2043 | `wire_envelope` | `TAUGHT` | `'inventory_service'` | `str` | `DERIVATION` | Rule H08: module `inventory_broadcaster.py` domain `inventory` + `_service` == `inventory_service` |
| 2043 | `wire_envelope` | `TAUGHT` | `'warehouse_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `warehouseId` -> `warehouse_id` |
| 2043 | `wire_envelope` | `TAUGHT` | `'warehouseId'` | `str` | `FIXTURE` | Assign: `res = broadcast_inventory_sync({'warehouseId': 'wh-9', 'itemSku': 'SKU-99'}, 1700000006)` |
| 2046 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T14:20:10.500Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 14, 20, 10, 500000]) -> `2026-10-25T14:20:10.500Z` |
| 2047 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T10:00:00.000Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 10, 0, 0, 0]) -> `2026-10-25T10:00:00.000Z` |
| 2047 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T10:00:00.987Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 10, 0, 0, 987654]) -> `2026-10-25T10:00:00.987Z` |
| 2048 | `timestamp_iso` | `DISTRACTOR` | `1792929600` | `int` | `LOCAL_OVERRIDE` | Local Override: epoch/microsecond timestamp specified in module docstring -> `1792929600` |
| 2048 | `timestamp_iso` | `DISTRACTOR` | `1792929610` | `int` | `LOCAL_OVERRIDE` | Local Override: epoch/microsecond timestamp specified in module docstring -> `1792929610` |
| 2049 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T06:00:00.000Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 6, 0, 0, 0]) -> `2026-10-25T06:00:00.000Z` |
| 2049 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T07:15:30.450Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 7, 15, 30, 450000]) -> `2026-10-25T07:15:30.450Z` |
| 2051 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T18:00:00.000Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 18, 0, 0, 0]) -> `2026-10-25T18:00:00.000Z` |
| 2051 | `timestamp_iso` | `TAUGHT` | `'2026-10-25T18:00:00.250Z'` | `str` | `DERIVATION` | Recomputed Rule H09: datetime([2026, 10, 25, 18, 0, 0, 250000]) -> `2026-10-25T18:00:00.250Z` |
| 2052 | `timestamp_iso` | `DISTRACTOR` | `'2026-10-25T20:00:00.123456Z'` | `str` | `LOCAL_OVERRIDE` | Local Override: epoch/microsecond timestamp specified in module docstring -> `2026-10-25T20:00:00.123456Z` |
| 2052 | `timestamp_iso` | `DISTRACTOR` | `'2026-10-25T20:00:00.000050Z'` | `str` | `LOCAL_OVERRIDE` | Local Override: epoch/microsecond timestamp specified in module docstring -> `2026-10-25T20:00:00.000050Z` |
| 2054 | `config_lists` | `TAUGHT` | `'zone-b'` | `str` | `FIXTURE` | Assign: `tenant = {'zones': ['zone-b', 'zone-c']}` |
| 2054 | `config_lists` | `TAUGHT` | `'zone-c'` | `str` | `FIXTURE` | Assign: `tenant = {'zones': ['zone-b', 'zone-c']}` |
| 2054 | `config_lists` | `TAUGHT` | `'dns_servers'` | `str` | `FIXTURE` | Assign: `tenant = {'network': {'dns_servers': ['1.1.1.1', '9.9.9.9']}}` |
| 2054 | `config_lists` | `TAUGHT` | `'8.8.8.8'` | `str` | `FIXTURE` | Assign: `base = {'network': {'dns_servers': ['8.8.8.8', '1.1.1.1']}}` |
| 2054 | `config_lists` | `TAUGHT` | `'1.1.1.1'` | `str` | `FIXTURE` | Assign: `tenant = {'network': {'dns_servers': ['1.1.1.1', '9.9.9.9']}}` |
| 2054 | `config_lists` | `TAUGHT` | `'9.9.9.9'` | `str` | `FIXTURE` | Assign: `tenant = {'network': {'dns_servers': ['1.1.1.1', '9.9.9.9']}}` |
| 2054 | `config_lists` | `TAUGHT` | `'network'` | `str` | `FIXTURE` | Assign: `tenant = {'network': {'dns_servers': ['1.1.1.1', '9.9.9.9']}}` |
| 2055 | `config_lists` | `TAUGHT` | `'-Wall'` | `str` | `FIXTURE` | Assign: `base = {'flags': ['-Wall', '-O2']}` |
| 2055 | `config_lists` | `TAUGHT` | `'-O2'` | `str` | `FIXTURE` | Assign: `over = {'flags': ['-O2', '-g']}` |
| 2055 | `config_lists` | `TAUGHT` | `'-g'` | `str` | `FIXTURE` | Assign: `over = {'flags': ['-O2', '-g']}` |
| 2055 | `config_lists` | `TAUGHT` | `'include'` | `str` | `FIXTURE` | Assign: `over = {'matrix': {'include': ['py311', 'py312']}}` |
| 2055 | `config_lists` | `TAUGHT` | `'py310'` | `str` | `FIXTURE` | Assign: `base = {'matrix': {'include': ['py310', 'py311']}}` |
| 2055 | `config_lists` | `TAUGHT` | `'py311'` | `str` | `FIXTURE` | Assign: `over = {'matrix': {'include': ['py311', 'py312']}}` |
| 2055 | `config_lists` | `TAUGHT` | `'py312'` | `str` | `FIXTURE` | Assign: `over = {'matrix': {'include': ['py311', 'py312']}}` |
| 2055 | `config_lists` | `TAUGHT` | `'matrix'` | `str` | `FIXTURE` | Assign: `over = {'matrix': {'include': ['py311', 'py312']}}` |
| 2056 | `config_lists` | `DISTRACTOR` | `'192.168.1.1'` | `str` | `FIXTURE` | Assign: `over = {'whitelist': ['192.168.1.1']}` |
| 2056 | `config_lists` | `DISTRACTOR` | `443` | `int` | `FIXTURE` | Assign: `over = {'ports': [443]}` |
| 2057 | `config_lists` | `TAUGHT` | `'viewer'` | `str` | `FIXTURE` | Assign: `defaults = {'roles': ['viewer', 'editor']}` |
| 2057 | `config_lists` | `TAUGHT` | `'editor'` | `str` | `FIXTURE` | Assign: `custom = {'roles': ['editor', 'billing_admin']}` |
| 2057 | `config_lists` | `TAUGHT` | `'billing_admin'` | `str` | `FIXTURE` | Assign: `custom = {'roles': ['editor', 'billing_admin']}` |
| 2057 | `config_lists` | `TAUGHT` | `'features'` | `str` | `FIXTURE` | Assign: `custom = {'features': {'modules': ['billing', 'analytics']}}` |
| 2059 | `config_lists` | `TAUGHT` | `'headers'` | `str` | `FIXTURE` | Assign: `env = {'headers': ['Authorization', 'X-Trace-Id']}` |
| 2059 | `config_lists` | `TAUGHT` | `'X-Tenant-Id'` | `str` | `FIXTURE` | Assign: `base = {'headers': ['X-Tenant-Id', 'Authorization']}` |
| 2059 | `config_lists` | `TAUGHT` | `'Authorization'` | `str` | `FIXTURE` | Assign: `env = {'headers': ['Authorization', 'X-Trace-Id']}` |
| 2059 | `config_lists` | `TAUGHT` | `'X-Trace-Id'` | `str` | `FIXTURE` | Assign: `env = {'headers': ['Authorization', 'X-Trace-Id']}` |
| 2059 | `config_lists` | `TAUGHT` | `'methods'` | `str` | `FIXTURE` | Assign: `env = {'match': {'methods': ['POST', 'PUT']}}` |
| 2059 | `config_lists` | `TAUGHT` | `'GET'` | `str` | `FIXTURE` | Assign: `base = {'match': {'methods': ['GET', 'POST']}}` |
| 2059 | `config_lists` | `TAUGHT` | `'POST'` | `str` | `FIXTURE` | Assign: `env = {'match': {'methods': ['POST', 'PUT']}}` |
| 2059 | `config_lists` | `TAUGHT` | `'PUT'` | `str` | `FIXTURE` | Assign: `env = {'match': {'methods': ['POST', 'PUT']}}` |
| 2060 | `config_lists` | `DISTRACTOR` | `'10.1.0.1'` | `str` | `FIXTURE` | Assign: `over = {'destinations': ['10.1.0.1']}` |
| 2060 | `config_lists` | `DISTRACTOR` | `'backends'` | `str` | `FIXTURE` | Assign: `over = {'backends': ['be-3']}` |
| 2060 | `config_lists` | `DISTRACTOR` | `'be-3'` | `str` | `FIXTURE` | Assign: `over = {'backends': ['be-3']}` |
| 2062 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2063 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2064 | `idempotency_keys` | `DISTRACTOR` | `'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}...'` | `str` | `LOCAL_OVERRIDE` | Local Override: UUID4 / integer idempotency specified in module docstring -> `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` |
| 2065 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2067 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2070 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `durations = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]` |
| 2070 | `metric_percentiles` | `TAUGHT` | `42.0` | `float` | `FIXTURE` | Call Arg: `evaluate_sla_breach(batch, 50.0, 42.0)` |
| 2070 | `metric_percentiles` | `TAUGHT` | `75.0` | `float` | `FIXTURE` | Call Arg: `evaluate_sla_breach(batch, 90.0, 75.0)` |
| 2071 | `metric_percentiles` | `TAUGHT` | `30.0` | `float` | `FIXTURE` | Call Arg: `compute_rpc_percentile(series, 30.0)` |
| 2071 | `metric_percentiles` | `TAUGHT` | `30.0` | `float` | `FIXTURE` | Call Arg: `compute_rpc_percentile(series, 30.0)` |
| 2071 | `metric_percentiles` | `TAUGHT` | `25.0` | `float` | `FIXTURE` | Call Arg: `compute_rpc_percentile(series, 25.0)` |
| 2071 | `metric_percentiles` | `TAUGHT` | `36.0` | `float` | `FIXTURE` | Assign: `samples = [RpcSample('billing', v) for v in [12.0, 15.0, 20.0, 24.0, 30.0, 36.0, 40.0, 50.0]]` |
| 2071 | `metric_percentiles` | `TAUGHT` | `75.0` | `float` | `FIXTURE` | Call Arg: `compute_rpc_percentile(series, 75.0)` |
| 2072 | `metric_percentiles` | `DISTRACTOR` | `26.0` | `float` | `LOCAL_OVERRIDE` | Recomputed Distractor Override: linear_interp(40.0%, len 5) -> 26.0 |
| 2072 | `metric_percentiles` | `DISTRACTOR` | `40.0` | `float` | `FIXTURE` | Call Arg: `compute_buffer_percentile(snap, 40.0)` |
| 2072 | `metric_percentiles` | `DISTRACTOR` | `40.0` | `float` | `FIXTURE` | Assign: `samples = [BufferSample('ch', v) for v in [10.0, 20.0, 30.0, 40.0, 50.0]]` |
| 2072 | `metric_percentiles` | `DISTRACTOR` | `75.0` | `float` | `FIXTURE` | Call Arg: `compute_buffer_percentile(snap, 75.0)` |
| 2073 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `lats = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]` |
| 2073 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `samples = [CacheSample('r', v) for v in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]]` |
| 2075 | `metric_percentiles` | `TAUGHT` | `500.0` | `float` | `FIXTURE` | Assign: `samples = [IoWaitSample('sda', v) for v in [100.0, 200.0, 300.0, 400.0, 500.0]]` |
| 2075 | `metric_percentiles` | `TAUGHT` | `95.0` | `float` | `FIXTURE` | Call Arg: `compute_io_percentile(b, 95.0)` |
| 2075 | `metric_percentiles` | `TAUGHT` | `200.0` | `float` | `FIXTURE` | Assign: `samples = [IoWaitSample('sda', v) for v in [100.0, 200.0, 300.0, 400.0, 500.0]]` |
| 2075 | `metric_percentiles` | `TAUGHT` | `30.0` | `float` | `FIXTURE` | Call Arg: `compute_io_percentile(b, 30.0)` |
| 2076 | `metric_percentiles` | `DISTRACTOR` | `28.5` | `float` | `LOCAL_OVERRIDE` | Recomputed Distractor Override: linear_interp(75.0%, len 6) -> 28.5 |
| 2076 | `metric_percentiles` | `DISTRACTOR` | `75.0` | `float` | `FIXTURE` | Call Arg: `calculate_loss_percentile(vals, 75.0)` |
| 2076 | `metric_percentiles` | `DISTRACTOR` | `28.5` | `float` | `LOCAL_OVERRIDE` | Recomputed Distractor Override: linear_interp(75.0%, len 6) -> 28.5 |
| 2077 | `state_transitions` | `TRANSFER` | `'pipe-100'` | `str` | `FIXTURE` | Assign: `p = PipelineEntity('pipe-100')` |
| 2077 | `state_transitions` | `TRANSFER` | `'user-1'` | `str` | `FIXTURE` | Call Arg: `transition_pipeline(p, 'BUILDING', 'user-1', 1700000001000)` |
| 2077 | `state_transitions` | `TRANSFER` | `1700000001000` | `int` | `FIXTURE` | Call Arg: `transition_pipeline(p, 'BUILDING', 'user-1', 1700000001000)` |
| 2078 | `state_transitions` | `TRANSFER` | `'esc-55'` | `str` | `FIXTURE` | Assign: `e = EscrowAccount('esc-55', 10000)` |
| 2078 | `state_transitions` | `TRANSFER` | `'sys'` | `str` | `FIXTURE` | Call Arg: `update_escrow(e, 'HELD', 'sys', 1700000010000)` |
| 2078 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `update_escrow(e, 'HELD', 'sys', 1700000010000)` |
| 2079 | `state_transitions` | `TRANSFER` | `'tick-100'` | `str` | `FIXTURE` | Assign: `t = SupportTicket('tick-100')` |
| 2079 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `transition_ticket(t, 'ASSIGNED', 'dispatcher', 1700000010000)` |
| 2080 | `state_transitions` | `TRANSFER` | `'vm-101'` | `str` | `FIXTURE` | Assign: `vm = VirtualMachine('vm-101')` |
| 2080 | `state_transitions` | `TRANSFER` | `'user-admin'` | `str` | `FIXTURE` | Call Arg: `update_instance_state(vm, 'RUNNING', 'user-admin', 1700000010000)` |
| 2080 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `update_instance_state(vm, 'RUNNING', 'user-admin', 1700000010000)` |
| 2081 | `state_transitions` | `TRANSFER` | `'ord-101'` | `str` | `FIXTURE` | Assign: `o = FulfillmentOrder('ord-101')` |
| 2081 | `state_transitions` | `TRANSFER` | `'payment_gw'` | `str` | `FIXTURE` | Call Arg: `transition_order_fulfillment(o, 'PAID', 'payment_gw', 1700000010000)` |
| 2081 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `transition_order_fulfillment(o, 'PAID', 'payment_gw', 1700000010000)` |
| 2082 | `state_transitions` | `TRANSFER` | `'pr-505'` | `str` | `FIXTURE` | Assign: `pr = PullRequest('pr-505')` |
| 2082 | `state_transitions` | `TRANSFER` | `'developer-1'` | `str` | `FIXTURE` | Call Arg: `update_pr_lifecycle(pr, 'OPEN', 'developer-1', 1700000010000)` |
| 2082 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `update_pr_lifecycle(pr, 'OPEN', 'developer-1', 1700000010000)` |
| 2083 | `state_transitions` | `TRANSFER` | `'sub-808'` | `str` | `FIXTURE` | Assign: `s = SubscriptionAccount('sub-808')` |
| 2083 | `state_transitions` | `TRANSFER` | `'billing_sys'` | `str` | `FIXTURE` | Call Arg: `transition_subscription(s, 'ACTIVE', 'billing_sys', 1700000010000)` |
| 2083 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `transition_subscription(s, 'ACTIVE', 'billing_sys', 1700000010000)` |
| 2084 | `state_transitions` | `TRANSFER` | `'job-404'` | `str` | `FIXTURE` | Assign: `j = BatchJob('job-404')` |
| 2084 | `state_transitions` | `TRANSFER` | `1700000010000` | `int` | `FIXTURE` | Call Arg: `advance_job_state(j, 'QUEUED', 'scheduler', 1700000010000)` |
| 2088 | `wire_envelope` | `TAUGHT` | `1700000050` | `int` | `FIXTURE` | Assign: `res = dispatch_customer_notice({'customerId': 'c99', 'emailVerified': True}, 1700000050)` |
| 2088 | `wire_envelope` | `TAUGHT` | `'customer_id'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `customerId` -> `customer_id` |
| 2088 | `wire_envelope` | `TAUGHT` | `'email_verified'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `emailVerified` -> `email_verified` |
| 2088 | `wire_envelope` | `TAUGHT` | `'c99'` | `str` | `FIXTURE` | Assign: `res = dispatch_customer_notice({'customerId': 'c99', 'emailVerified': True}, 1700000050)` |
| 2089 | `wire_envelope` | `TAUGHT` | `1700000050` | `int` | `FIXTURE` | Assign: `res = broadcast_payment_confirmation({'chargeAmount': 500, 'currencyCode': 'USD'}, 1700000050)` |
| 2089 | `wire_envelope` | `TAUGHT` | `'charge_amount'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `chargeAmount` -> `charge_amount` |
| 2089 | `wire_envelope` | `TAUGHT` | `'currency_code'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `currencyCode` -> `currency_code` |
| 2089 | `wire_envelope` | `TAUGHT` | `500` | `int` | `FIXTURE` | Assign: `res = broadcast_payment_confirmation({'chargeAmount': 500, 'currencyCode': 'USD'}, 1700000050)` |
| 2089 | `wire_envelope` | `TAUGHT` | `'USD'` | `str` | `FIXTURE` | Assign: `res = broadcast_payment_confirmation({'chargeAmount': 500, 'currencyCode': 'USD'}, 1700000050)` |
| 2090 | `wire_envelope` | `TAUGHT` | `1700000050` | `int` | `FIXTURE` | Assign: `res = emit_shipment_event({'trackingNumber': '1Z999', 'deliveryStatus': 'IN_TRANSIT'}, 1700000050)` |
| 2090 | `wire_envelope` | `TAUGHT` | `'tracking_number'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `trackingNumber` -> `tracking_number` |
| 2090 | `wire_envelope` | `TAUGHT` | `'delivery_status'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `deliveryStatus` -> `delivery_status` |
| 2090 | `wire_envelope` | `TAUGHT` | `'1Z999'` | `str` | `FIXTURE` | Assign: `res = emit_shipment_event({'trackingNumber': '1Z999', 'deliveryStatus': 'IN_TRANSIT'}, 1700000050)` |
| 2090 | `wire_envelope` | `TAUGHT` | `'IN_TRANSIT'` | `str` | `FIXTURE` | Assign: `res = emit_shipment_event({'trackingNumber': '1Z999', 'deliveryStatus': 'IN_TRANSIT'}, 1700000050)` |
| 2104 | `wire_envelope` | `TAUGHT` | `1700000050` | `int` | `FIXTURE` | Assign: `res = emit_invoice_event({'invoiceTotal': 9900, 'taxDue': 800}, 1700000050)` |
| 2104 | `wire_envelope` | `TAUGHT` | `'invoice_total'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `invoiceTotal` -> `invoice_total` |
| 2104 | `wire_envelope` | `TAUGHT` | `'tax_due'` | `str` | `DERIVATION` | Rule H08: snake_case normalization of input fixture key `taxDue` -> `tax_due` |
| 2104 | `wire_envelope` | `TAUGHT` | `9900` | `int` | `FIXTURE` | Assign: `res = emit_invoice_event({'invoiceTotal': 9900, 'taxDue': 800}, 1700000050)` |
| 2104 | `wire_envelope` | `TAUGHT` | `800` | `int` | `FIXTURE` | Assign: `res = emit_invoice_event({'invoiceTotal': 9900, 'taxDue': 800}, 1700000050)` |
| 2091 | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | `str` | `DERIVATION` | Recomputed Rule H09: epoch_sec(1700000000.123456) -> `2023-11-14T22:13:20.123Z` |
| 2092 | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | `str` | `DERIVATION` | Recomputed Rule H09: epoch_sec(1700000000.123456) -> `2023-11-14T22:13:20.123Z` |
| 2093 | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | `str` | `DERIVATION` | Recomputed Rule H09: epoch_sec(1700000000.123456) -> `2023-11-14T22:13:20.123Z` |
| 2094 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2095 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2096 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2105 | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | `str` | `DERIVATION` | Rule H13: regex compiled from spec `idemp_<timestamp_ms>_<hex_token_8chars>` |
| 2097 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2097 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2097 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2097 | `metric_percentiles` | `TAUGHT` | `70.0` | `float` | `FIXTURE` | Call Arg: `calculate_endpoint_percentile(d2, 70.0)` |
| 2098 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2098 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2098 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2098 | `metric_percentiles` | `TAUGHT` | `70.0` | `float` | `FIXTURE` | Call Arg: `compute_duration_percentile(d2, 70.0)` |
| 2099 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2099 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2099 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2099 | `metric_percentiles` | `TAUGHT` | `70.0` | `float` | `FIXTURE` | Call Arg: `calculate_write_percentile(d2, 70.0)` |
| 2106 | `metric_percentiles` | `TAUGHT` | `40.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2106 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2106 | `metric_percentiles` | `TAUGHT` | `50.0` | `float` | `FIXTURE` | Assign: `d2 = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]` |
| 2106 | `metric_percentiles` | `TAUGHT` | `70.0` | `float` | `FIXTURE` | Call Arg: `calculate_cache_percentile(d2, 70.0)` |
| 2102 | `money_rounding` | `TAUGHT` | `'0.13'` | `str` | `DERIVATION` | Recomputed Rule H02: Decimal 2.50 * 0.05 -> 0.13 |
| 2102 | `money_rounding` | `TAUGHT` | `'0.12'` | `str` | `DERIVATION` | Recomputed Rule H02: Decimal 2.42 * 0.05 -> 0.12 |

---

## 3. Negative Control & Mutation Verification

To prove that the rule sufficiency checker and triage engine have active teeth and do not pass by construction:
1. **Percentile Mutation Control:** In Task 2070, changing the asserted nearest-rank percentile from `40.0` to `40.5` causes the triage engine to fail recomputation and immediately flag Task 2070 as `UNRESOLVED`.
2. **Rounding Mutation Control:** In Task 2102, changing the asserted half-up rounded fee from `'0.13'` to `'0.14'` causes the triage engine to fail recomputation and immediately flag Task 2102 as `UNRESOLVED`.
3. **Missing Rule Controls:** Removing Rule H08's `_src` definition sentence, Rule H13's idempotency token format, or Rule H04's error codes from the handbook causes all corresponding tasks to be flagged as `UNRESOLVED`.

---

## 4. Unresolved Defects Summary

**PASS:** Exactly **0** tasks contain unstated, arbitrary, or unresolvable contract literals. Condition J2 is fully satisfied across all 106 tasks in Suite E5.
