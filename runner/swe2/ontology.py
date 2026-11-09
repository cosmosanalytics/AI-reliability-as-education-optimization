"""SWE-2 Know layer: ontology + knowledge graph + context graph, extracted from briefs/HANDBOOK.md.

The student model never sees HANDBOOK.md. It sees only typed nodes and triples defined here.
Every Literal/Format node value must occur verbatim in the handbook (checked by
`verify_grounding`), so the graph adds no knowledge the handbook does not contain.
Aliases are retrieval vocabulary only (how a ticket might name the concept).

Ontology (classes)
  Convention  a house rule (one per handbook rule, id = rule id)
  Domain      the code area a convention governs
  Behavior    an operation the convention requires
  Alternative a competing practice the convention prohibits
  Format      a string/record layout
  Literal     an exact token, constant, name or value
  Scope       where a convention (or an exception to it) applies
  Case        context-graph node: a worked example stated in the handbook (input -> output)

Relations
  governs(Convention, Domain)        applies_to(Convention, Scope)
  requires(Convention, Behavior)     prohibits(Convention, Alternative)
  has_format(X, Format)              uses_literal(X, Literal)
  except_in(Convention, Scope)       exception_requires(Scope, Behavior)
  derived_by(Literal, Behavior)      has_part(Format, Literal)
  has_case(Convention, Case)         case_input / case_output (Case, Literal)
"""

CLASSES = ["Convention", "Domain", "Behavior", "Alternative", "Format", "Literal", "Scope", "Case"]
RELATIONS = [
    "governs", "applies_to", "requires", "prohibits", "has_format", "uses_literal", "except_in",
    "exception_requires", "derived_by", "has_part", "has_case", "case_input", "case_output",
]

# node id -> (class, label, value-or-None, aliases)
# Literal/Format/Case values are verbatim handbook strings (grounded).
def _n(cls, label, value=None, aliases=()):
    return {"class": cls, "label": label, "value": value, "aliases": list(aliases)}


def build(source="handbook"):
    if source == "placebo":
        from ontology_placebo import NODES as PN, TRIPLES as PT
        return {"nodes": PN, "triples": PT}
    N, T = {}, []

    def node(i, *a, **k):
        N[i] = _n(*a, **k)
        return i

    def tr(s, p, o):
        T.append([s, p, o])

    # H01 test protection
    c = node("H01", "Convention", "test directory protection", aliases=["tests", "test files", "protected"])
    tr(c, "applies_to", node("H01.scope", "Scope", "files within any tests/ directory", "tests/"))
    tr(c, "prohibits", node("H01.alt", "Alternative", "modify, delete, or create test files"))
    tr(c, "requires", node("H01.beh", "Behavior", "fixes reside strictly within production source modules"))

    # H02 money
    c = node("H02", "Convention", "monetary arithmetic rounding", aliases=[
        "money", "cents", "invoice", "ledger", "price", "currency", "rounding", "balance", "allocation",
        "refund", "tax", "billing", "decimal", "fee"])
    tr(c, "governs", node("D.money", "Domain", "financial ledger balances, invoice line adjustments, price conversions, monetary allocations"))
    tr(c, "requires", node("H02.fixed", "Behavior", "fixed-point arithmetic"))
    tr(c, "uses_literal", node("H02.hu", "Literal", "half-up rounding mode", "ROUND_HALF_UP", ["half up", "ties"]))
    tr("H02.hu", "derived_by", node("H02.tie", "Behavior", "ties broken towards positive infinity"))
    tr(c, "prohibits", node("H02.float", "Alternative", "naive floating-point arithmetic", aliases=["float"]))
    tr(c, "prohibits", node("H02.he", "Alternative", "banker's rounding", "ROUND_HALF_EVEN", ["bankers", "half even"]))

    # H03 immutability
    c = node("H03", "Convention", "container immutability / defensive allocation", aliases=[
        "mutate", "mutation", "dict", "list", "set", "copy", "deepcopy", "caller", "in place", "merge",
        "config", "options", "defaults", "shared", "aliasing"])
    tr(c, "applies_to", node("H03.scope", "Scope", "functions accepting mutable containers", "dict, list, set"))
    tr(c, "prohibits", node("H03.alt", "Alternative", "mutating caller-supplied arguments in place"))
    tr(c, "requires", node("H03.copy", "Behavior", "defensive deep copies or new collection instances before modification"))
    tr(c, "requires", node("H03.ret", "Behavior", "return newly allocated data structures"))

    # H04 service errors
    c = node("H04", "Convention", "structured service exception hierarchy", aliases=[
        "error", "exception", "raise", "ValueError", "KeyError", "permission", "unauthorized", "scope",
        "schema", "validation", "payload", "locked", "conflict", "rate limit", "quota", "error code"])
    tr(c, "uses_literal", node("H04.cls", "Literal", "exception class", 'ServiceError(code="ERR_<CATEGORY>_<DETAIL>", message="...")'))
    tr("H04.cls", "uses_literal", node("H04.mod", "Literal", "defining module", "errors.py"))
    tr(c, "applies_to", node("H04.scope", "Scope", "domain service errors, permission failures, schema validations"))
    tr(c, "prohibits", node("H04.alt", "Alternative", "generic exceptions", "ValueError, KeyError, or raw Exception"))
    for k, (val, al) in {
        "auth": ("ERR_AUTH_SCOPE_DENIED", "unauthorized access or missing scope"),
        "schema": ("ERR_PAYLOAD_SCHEMA_INVALID", "missing or malformed request payload attributes and schema verification failures"),
        "valid": ("ERR_VALIDATION_FAILED", "missing or malformed request payload attributes and schema verification failures"),
        "lock": ("ERR_RESOURCE_LOCKED", "concurrent modification conflicts"),
        "rate": ("ERR_RATE_LIMIT_EXCEEDED", "quota and burst budget exhaustion"),
    }.items():
        lit = node(f"H04.{k}", "Literal", f"error code for {al}", val)
        tr(c, "uses_literal", lit)

    # H05 intervals
    c = node("H05", "Convention", "temporal interval representation", aliases=[
        "interval", "window", "span", "boundary", "start", "end", "inclusive", "exclusive", "range",
        "maintenance", "cron", "reservation", "query", "report", "metric window", "calendar", "schedule"])
    tr(c, "applies_to", node("H05.std", "Scope", "standard query intervals, analytics reporting spans, metric windows"))
    tr("H05.std", "has_format", node("H05.ho", "Format", "half-open interval", "[\\text{start}, \\text{end})"))
    tr("H05.ho", "derived_by", node("H05.hob", "Behavior", "inclusive of start, exclusive of end", "start <= t < end"))
    tr(c, "except_in", node("H05.maint", "Scope", "scheduled maintenance windows and cron reservation spans"))
    tr("H05.maint", "has_format", node("H05.cl", "Format", "closed inclusive interval", "[\\text{start}, \\text{end}]"))
    tr("H05.cl", "derived_by", node("H05.clb", "Behavior", "inclusive of both ends", "start <= t <= end"))

    # H06 scopes
    c = node("H06", "Convention", "hierarchical access-control scopes", aliases=[
        "permission", "scope", "access", "acl", "prefix", "sibling", "wildcard", "authorize", "grant",
        "path", "hierarchy", "tenant", "department"])
    tr(c, "has_format", node("H06.fmt", "Format", "scope path", "tenant::department::service::action"))
    tr("H06.fmt", "has_part", node("H06.sep", "Literal", "segment separator", "::"))
    tr(c, "has_case", node("H06.case", "Case", "example scope", '"corp::billing::invoices::write"'))
    tr(c, "requires", node("H06.seg", "Behavior", "sibling paths checked against :: segment boundaries"))
    tr(c, "uses_literal", node("H06.star", "Literal", "single-segment wildcard (matches exactly one segment)", "*"))
    tr(c, "uses_literal", node("H06.dstar", "Literal", "multi-segment wildcard (matches arbitrary multi-segment prefixes)", "**"))

    # H07 event ordering
    c = node("H07", "Convention", "deterministic event ordering", aliases=[
        "event", "queue", "priority", "order", "ordering", "tie", "tie-break", "sort", "dispatch",
        "schedule", "deterministic", "reproducible", "timestamp", "heap"])
    tr(c, "applies_to", node("H07.scope", "Scope", "event dispatch queues and task scheduling"))
    tr(c, "requires", node("H07.tb", "Behavior", "events with identical timestamp or priority score ordered by payload SHA-256 digest ascending lexicographic"))
    tr("H07.tb", "uses_literal", node("H07.sha", "Literal", "digest", "SHA-256"))
    tr(c, "requires", node("H07.rep", "Behavior", "execution order 100% reproducible across invocations"))

    # H08 wire envelope
    c = node("H08", "Convention", "message wire envelope", aliases=[
        "envelope", "wire", "message", "payload", "event stream", "record", "serialize", "snake_case",
        "camelCase", "keys", "dispatcher", "formatter", "_src", "_v", "_ts", "producer", "service"])
    tr(c, "applies_to", node("H08.scope", "Scope", "internal wire messages, event stream records, inter-service payloads"))
    tr(c, "has_format", node("H08.fmt", "Format", "envelope", '{"_v": 2, "_ts": epoch_ms, "_src": service_name, "payload": data}'))
    tr("H08.fmt", "has_part", node("H08.v", "Literal", "version field", '"_v": 2'))
    tr("H08.fmt", "has_part", node("H08.ts", "Literal", "timestamp field (epoch milliseconds)", '"_ts": epoch_ms'))
    tr("H08.fmt", "has_part", node("H08.src", "Literal", "source field", '"_src": service_name'))
    tr("H08.src", "derived_by", node("H08.srcb", "Behavior", "first word of the module's file name before the underscore, followed by _service", "_service"))
    tr(c, "has_case", node("H08.c1", "Case", "order_dispatcher.py emits order_service"))
    tr("H08.c1", "case_input", node("H08.c1i", "Literal", "module", "order_dispatcher.py"))
    tr("H08.c1", "case_output", node("H08.c1o", "Literal", "_src", "order_service"))
    tr(c, "has_case", node("H08.c2", "Case", "activity_dispatcher.py emits activity_service"))
    tr("H08.c2", "case_input", node("H08.c2i", "Literal", "module", "activity_dispatcher.py"))
    tr("H08.c2", "case_output", node("H08.c2o", "Literal", "_src", "activity_service"))
    tr(c, "has_case", node("H08.c3", "Case", "audit_formatter.py emits audit_service"))
    tr("H08.c3", "case_input", node("H08.c3i", "Literal", "module", "audit_formatter.py"))
    tr("H08.c3", "case_output", node("H08.c3o", "Literal", "_src", "audit_service"))
    tr(c, "requires", node("H08.snake", "Behavior", "all dictionary keys inside the payload normalized to snake_case", "snake_case"))

    # H09 timestamps
    c = node("H09", "Convention", "canonical UTC timestamp formatting", aliases=[
        "timestamp", "datetime", "iso", "iso 8601", "utc", "isoformat", "export", "milliseconds",
        "microseconds", "timezone", "offset", "Z", "time format", "strftime"])
    tr(c, "applies_to", node("H09.scope", "Scope", "all exported string timestamps"))
    tr(c, "has_format", node("H09.fmt", "Format", "ISO 8601 UTC with milliseconds and uppercase Z", "YYYY-MM-DDTHH:MM:SS.sssZ"))
    tr(c, "has_case", node("H09.case", "Case", "example timestamp", '"2026-10-25T12:00:00.000Z"'))
    tr("H09.fmt", "has_part", node("H09.z", "Literal", "uppercase suffix", "'Z'"))
    tr(c, "prohibits", node("H09.alt", "Alternative", "microsecond precision, local timezone offsets, or omission of milliseconds"))

    # H10 TSV
    c = node("H10", "Convention", "TSV audit log escaping", aliases=[
        "tsv", "csv", "audit", "log", "export", "escape", "quote", "quotes", "newline", "null", "None",
        "tab", "delimiter", "serialize", "row", "record", "round trip"])
    tr(c, "applies_to", node("H10.scope", "Scope", "internal audit log pipelines"))
    tr(c, "has_format", node("H10.fmt", "Format", "TSV", "TSV format"))
    tr("H10.fmt", "has_part", node("H10.tab", "Literal", "field separator (tab)", "\\t"))
    tr("H10.fmt", "has_part", node("H10.q", "Literal", "escaped double quote (backslash)", '\\"'))
    tr("H10.fmt", "has_part", node("H10.nl", "Literal", "escaped newline", "\\n"))
    tr("H10.fmt", "has_part", node("H10.null", "Literal", "serialized None/null", "\\N"))
    tr(c, "prohibits", node("H10.alt", "Alternative", "RFC 4180 double-quoting", "RFC 4180"))

    # H11 cache keys
    c = node("H11", "Convention", "cache key namespace", aliases=[
        "cache", "redis", "key", "namespace", "ttl", "expiry", "invalidate", "tenant", "entity",
        "plural", "singular", "spaces", "underscore", "lowercase"])
    tr(c, "applies_to", node("H11.scope", "Scope", "Redis and cache cluster keys"))
    tr(c, "has_format", node("H11.fmt", "Format", "lowercase colon-delimited key", "app:v2:<tenant_id>:<entity_type>:<entity_id>"))
    tr(c, "requires", node("H11.sp", "Behavior", "spaces in entity identifiers replaced with underscores"))
    tr(c, "requires", node("H11.sing", "Behavior", "entity types must be singular"))
    tr(c, "requires", node("H11.low", "Behavior", "keys lowercase"))

    # H12 config lists
    c = node("H12", "Convention", "configuration merge with list concatenation", aliases=[
        "config", "merge", "override", "base", "nested", "list", "lists", "deduplicate", "duplicates",
        "concatenate", "plugins", "hosts", "layered", "settings", "recursive"])
    tr(c, "applies_to", node("H12.scope", "Scope", "merging hierarchical configuration dictionaries"))
    tr(c, "requires", node("H12.rec", "Behavior", "nested dictionaries merged recursively"))
    tr(c, "requires", node("H12.cat", "Behavior", "list values concatenated base then override, duplicates removed preserving first-seen order", "[base_items + override_items]"))
    tr(c, "prohibits", node("H12.alt", "Alternative", "replacing list values with the override list"))

    # H13 idempotency
    c = node("H13", "Convention", "outbound request idempotency headers", aliases=[
        "idempotency", "idempotent", "retry", "retries", "header", "rpc", "http", "request", "outbound",
        "duplicate", "key", "token", "uuid", "mutating", "gateway"])
    tr(c, "applies_to", node("H13.scope", "Scope", "all mutating outbound RPC or HTTP requests"))
    tr(c, "uses_literal", node("H13.hdr", "Literal", "header name", "X-Idempotency-Key"))
    tr("H13.hdr", "has_format", node("H13.fmt", "Format", "idempotency key", "idemp_<timestamp_ms>_<hex_token_8chars>"))
    tr(c, "requires", node("H13.reuse", "Behavior", "retries reuse the exact same idempotency key across attempts"))

    # H14 percentiles
    c = node("H14", "Convention", "metric percentile estimation", aliases=[
        "percentile", "p50", "p95", "p99", "latency", "telemetry", "metric", "sla", "quantile",
        "median", "interpolation", "rank", "statistics"])
    tr(c, "applies_to", node("H14.scope", "Scope", "telemetry metric percentiles, SLA compliance metrics"))
    tr(c, "requires", node("H14.nr", "Behavior", "nearest-rank method on sorted arrays"))
    tr("H14.nr", "uses_literal", node("H14.k", "Literal", "index", "k = \\lceil \\frac{P}{100} \\cdot N \\rceil - 1"))
    tr(c, "prohibits", node("H14.alt", "Alternative", "continuous linear interpolation"))

    # H15 FSM
    c = node("H15", "Convention", "state machine transition validation and audit", aliases=[
        "state", "transition", "workflow", "lifecycle", "status", "fsm", "state machine", "audit",
        "invalid transition", "order status", "approve", "cancel"])
    tr(c, "applies_to", node("H15.scope", "Scope", "any state transition in workflow or lifecycle entities"))
    tr(c, "requires", node("H15.val", "Behavior", "validate allowed transitions"))
    tr(c, "has_format", node("H15.tuple", "Format", "audit tuple", '("STATE_TRANSITION", entity_id, old_state, new_state, actor_id, timestamp_ms)'))
    tr(c, "uses_literal", node("H15.err", "Literal", "error for invalid transitions", 'ServiceError(code="ERR_INVALID_TRANSITION", ...)'))

    # H16 token bucket
    c = node("H16", "Convention", "token bucket integer truncation", aliases=[
        "rate limit", "token bucket", "burst", "refill", "throttle", "admission", "tokens", "fractional"])
    tr(c, "applies_to", node("H16.scope", "Scope", "token-bucket rate limiters (burst capacity C, refill rate R tokens/second)"))
    tr(c, "requires", node("H16.fl", "Behavior", "available token balance floored to integer units", "math.floor(current_tokens)"))
    tr(c, "prohibits", node("H16.alt", "Alternative", "consuming fractional tokens"))

    return {"nodes": N, "triples": T}


def verify_grounding(graph, handbook_text):
    """Every Literal/Format/Case value must appear verbatim in the source text."""
    bad = []
    for i, n in graph["nodes"].items():
        if n["class"] in ("Literal", "Format", "Case") and n["value"]:
            if n["value"] not in handbook_text:
                bad.append((i, n["value"]))
    return bad
