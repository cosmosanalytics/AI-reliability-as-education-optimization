import os
import tiktoken

repo_root = "C:/Users/richa/ai-engineering/repo_push"
briefs_dir = os.path.join(repo_root, "briefs")
enc = tiktoken.get_encoding("cl100k_base")

handbook_text = """# Engineering Standards and House Conventions (`HANDBOOK.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule H01: Test Directory Protection
Never modify, delete, or create files within any `tests/` directory. All bug fixes, refactorings, and feature implementations must reside strictly within production source modules. Test files define immutable correctness contracts.

### Rule H02: Monetary Arithmetic and Half-Up Rounding Convention
All financial ledger balances, invoice line adjustments, price conversions, and monetary allocations must use fixed-point arithmetic with half-up rounding (`ROUND_HALF_UP`: ties broken towards positive infinity). Naive floating-point arithmetic and standard banker's rounding (`ROUND_HALF_EVEN`) are strictly prohibited in financial ledger modules.

### Rule H03: Container Immutability and Defensive Allocation
Functions accepting mutable containers (`dict`, `list`, `set`) must never mutate caller-supplied arguments in place. Always perform defensive deep copies or allocate new collection instances prior to modification. Functions must return newly allocated data structures.

### Rule H04: Structured Service Exception Hierarchy and Error Codes
All domain service errors, permission failures, and schema validations must raise `ServiceError(code="ERR_<CATEGORY>_<DETAIL>", message="...")` defined in `errors.py`. Never raise generic `ValueError`, `KeyError`, or raw `Exception`. Standard error codes:
- `"ERR_AUTH_SCOPE_DENIED"` for unauthorized access or missing scope.
- `"ERR_PAYLOAD_SCHEMA_INVALID"` for missing or malformed request payload attributes.
- `"ERR_RESOURCE_LOCKED"` for concurrent modification conflicts.
- `"ERR_RATE_LIMIT_EXCEEDED"` for quota and burst budget exhaustion.

### Rule H05: Temporal Representation (Half-Open vs Inclusive Spans)
Standard query intervals, analytics reporting spans, and metric windows must follow the half-open interval convention $[\\text{start}, \\text{end})$: inclusive of the start boundary and strictly exclusive of the end boundary ($\\text{start} \\le t < \\text{end}$). However, scheduled maintenance windows and cron reservation spans use the closed inclusive convention $[\\text{start}, \\text{end}]$: $\\text{start} \\le t \\le \\text{end}$.

### Rule H06: Hierarchical Access Control Scopes and Wildcards
Access control scopes must use the double-colon hierarchy `tenant::department::service::action` (e.g. `"corp::billing::invoices::write"`). Sibling paths must be checked against `::` segment boundaries. The single asterisk wildcard `*` matches exactly one segment; the double asterisk `**` matches arbitrary multi-segment prefixes.

### Rule H07: Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking
When prioritizing event dispatch queues or scheduling tasks, events with identical timestamp or priority score must be ordered deterministically by payload SHA-256 digest in ascending lexicographical order. Execution order must be 100% reproducible across invocations.

### Rule H08: Message Wire Envelope and Snake-Case Key Normalization
All internal wire messages, event stream records, and inter-service payloads must be wrapped in a standardized envelope: `{"_v": 2, "_ts": epoch_ms, "_src": service_name, "payload": data}`. All dictionary keys inside the payload must be strictly normalized to `snake_case`.

### Rule H09: Canonical UTC Timestamp Formatting with Millisecond Precision
All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase `'Z'` suffix (`YYYY-MM-DDTHH:MM:SS.sssZ`, e.g. `"2026-10-25T12:00:00.000Z"`). Microsecond precision, local timezone offsets, or omission of milliseconds are rejected.

### Rule H10: TSV Audit Logging and Backslash Escaping Convention
Internal audit log pipelines use TSV format: records are tab-separated (`\\t`), internal double quotes are escaped with backslash (`\\"`), newline characters are escaped as `\\n`, and `None`/null values are serialized as `\\N`. Do NOT use RFC 4180 double-quoting.

### Rule H11: Cache Key Namespace Architecture
Redis and cache cluster keys must strictly conform to the lowercase colon-delimited format: `app:v2:<tenant_id>:<entity_type>:<entity_id>`. All spaces in entity identifiers must be replaced with underscores, and entity types must be singular.

### Rule H12: Configuration Merge and Deduplicated List Concatenation
When merging hierarchical configuration dictionaries, nested dictionaries are merged recursively. However, list values must NOT be replaced; lists must be concatenated in order of `[base_items + override_items]` with duplicate items removed while preserving first-seen order.

### Rule H13: Outbound Request Idempotency Headers
All mutating outbound RPC or HTTP requests must attach an idempotency header `X-Idempotency-Key` formatted as `idemp_<timestamp_ms>_<hex_token_8chars>`. Retries must reuse the exact same idempotency key across attempts.

### Rule H14: Metric Percentile Estimation via Nearest-Rank Method
Telemetry metric percentiles ($P_{50}, P_{95}, P_{99}$) must be computed using the nearest-rank method: index $k = \\lceil \\frac{P}{100} \\cdot N \\rceil - 1$ on sorted arrays. Continuous linear interpolation is prohibited for SLA compliance metrics.

### Rule H15: Finite State Machine Transition Validation and Audit Tuples
Any state transition in workflow or lifecycle entities must validate allowed transitions and emit a structured audit tuple: `("STATE_TRANSITION", entity_id, old_state, new_state, actor_id, timestamp_ms)`. Invalid transitions must raise `ServiceError(code="ERR_INVALID_TRANSITION", ...)`.

### Rule H16: Rate Limiting Token Bucket Integer Truncation
Token-bucket rate limiters track burst capacity $C$ and refill rate $R$ tokens/second. When evaluating request admission, available token balance is floored to integer units (`math.floor(current_tokens)`); fractional tokens cannot be consumed.
"""

placebo_text = """# Engineering Standards and House Conventions (`PLACEBO.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule P01: Code Formatting and Maximum Line Length
All source code files must strictly comply with automated PEP 8 formatting standards and linting rules. Enforce a maximum line length of 88 characters for all statement bodies, list comprehensions, and function signatures. Split long chained method invocations and complex expressions across multiple indented lines with closing delimiters matching the opening indentation column to ensure maximum readability across development environments.

### Rule P02: Structured Documentation and Docstring Style
All public modules, classes, and exported functions must include comprehensive Google-style docstrings. Provide explicit `Args:`, `Returns:`, and `Raises:` documentation blocks describing parameter expectations, output representations, and potential failure conditions. Include descriptive narrative prose summarizing overall component behavior, architecture, and assumptions to provide full onboarding context for prospective contributors.

### Rule P03: Variable Naming and Identifier Conventions
Identifiers across the repository must follow unambiguous naming conventions: use `snake_case` for module-level functions and variable instances, `PascalCase` for class definitions, and `UPPER_SNAKE_CASE` for configuration constants. Never utilize ambiguous single-letter variable names outside of standard loop index counters (`i`, `j`). Choose meaningful, self-explanatory variable names that reflect the precise domain entity.

### Rule P04: Type Annotations and Static Verification
All function parameter lists and return signatures must declare complete static type annotations. Utilize modern standard library typing constructs (`Optional[T]`, `List[T]`, `Dict[K, V]`, `Callable`, `Tuple[T, ...]`). Ensure type signatures precisely describe allowable container contents and avoid ambiguous generic `Any` declarations whenever possible in production modules, enabling static type analyzers to detect subtle contract bugs.

### Rule P05: Module Organization and Import Grouping
Source file imports must be organized into three distinct blocks separated by single blank lines: standard library modules, external third-party dependencies, and internal package modules. Within each individual block, sort imported symbol names in strict ascending lexicographical order. Wildcard imports are completely prohibited to maintain clear namespace boundaries and explicit origin tracking.

### Rule P06: Structured Logging and Telemetry Standards
Use the standard library `logging` framework rather than unbuffered standard console streams. Obtain module-specific logger instances via `logging.getLogger(__name__)`. Provide contextual key-value attributes in log messages to facilitate centralized log aggregation and tracing across distributed processes. Never utilize unadorned `print()` statements for diagnostic information or operational tracking in production code.

### Rule P07: Error Message Phrasing and Clarity
Exception error messages must be crafted with professional clarity, operational precision, and consistency across modules. Begin error descriptions with an uppercase character and omit trailing punctuation marks. Explicitly specify the problematic parameter identifier and offending value within the message to accelerate developer remediation, triage, and root-cause analysis during incident investigations.

### Rule P08: Hygiene and Dead Code Elimination
Maintain impeccable codebase hygiene by removing unused imports, commented-out obsolete code fragments, and temporary debugging routines before committing changes to version control. Never commit placeholder `# TODO` or `# FIXME` markers without referencing an active tracking ticket identifier in the issue tracker to prevent technical debt from accumulating silently.

### Rule P09: Execution Profiling and Measurement Hooks
High-throughput processing pipelines, background thread workers, and batch processing loops should integrate non-intrusive latency profiling hooks. Instrument critical section boundaries with standardized timing metrics or context managers to surface execution bottlenecks without modifying the underlying business domain logic or inflating operational overhead.

### Rule P10: Source Header Declarations and Licensing
Every newly created repository source file must begin with standard repository file header declarations. Include standardized copyright notices, licensing references, and UTF-8 encoding declarations at the absolute top of the source file prior to any executable logic, import blocks, or module docstrings to establish explicit legal ownership and compliance.

### Rule P11: Function Parameter Count and Signature Cleanliness
Functions and methods must maintain compact parameter lists containing no more than five positional arguments. When a function requires numerous configuration options, encapsulate related parameters within structured dataclasses or typed dictionaries to maintain readability, simplify callers, and ensure extensible future enhancements.

### Rule P12: Constant Extraction and Configuration Separation
Hardcoded literal values, magical numerical constants, and static string templates must be extracted into designated module constants or centralized configuration files. Provide descriptive uppercase identifiers that document the underlying domain meaning and engineering rationale for each constant value across all execution modes.

### Rule P13: Cyclomatic Complexity and Nested Branch Reduction
Routines must avoid excessive nested conditional blocks and deeply indented control flow structures. Guard clauses and early return statements should be leveraged to handle validation failures immediately, keeping the primary execution path at the lowest indentation level and reducing cognitive burden for reviewers.

### Rule P14: Cohesive Module Boundaries and Single Responsibility
Each software module and component class must adhere strictly to the single responsibility principle. Group tightly coupled routines into dedicated modules and expose concise public interfaces while hiding internal implementation details behind private helper functions to minimize ripple effects during code refactorings.

### Rule P15: Defensive Precondition Checks and Null Safety
Public API boundaries and data ingestion gateways must perform rigorous precondition verification on all incoming payloads. Validate that required fields are present, collection bounds are respected, and unexpected null pointers are caught prior to processing downstream operations to guarantee high system stability.

### Rule P16: Dependency Isolation and Version Pinning
External third-party library dependencies must be explicitly pinned with exact version specifications in dependency manifest files. Avoid relying on transitive dependency installations or unpinned version ranges to ensure fully reproducible build environments, eliminating discrepancies between local workstations and CI environments.
"""

# Fine-tuning additions to achieve exact parity (within 1%)
additions = [
    " Development teams must enforce automated linting and style validation in continuous integration pipelines to catch deviations before review.",
    " High quality docstrings serve as the definitive specification for component behavior, preventing misunderstandings across engineering squads.",
    " Descriptive naming conventions reduce the time required for new engineers to navigate unfamiliar parts of the system during triage.",
    " Comprehensive static typing eliminates entire classes of runtime exceptions and substantially accelerates safe refactoring initiatives.",
]

for add in additions:
    if len(enc.encode(placebo_text)) < len(enc.encode(handbook_text)):
        placebo_text += add

tok_h = len(enc.encode(handbook_text))
tok_p = len(enc.encode(placebo_text))
diff_pct = abs(tok_h - tok_p) / tok_h * 100

print(f"Handbook v2 tokens: {tok_h}")
print(f"Placebo v2 tokens:  {tok_p}")
print(f"Difference:         {abs(tok_h - tok_p)} tokens ({diff_pct:.2f}%)")

assert diff_pct <= 3.0, f"Token difference {diff_pct:.2f}% exceeds 3% limit!"

with open(os.path.join(briefs_dir, "HANDBOOK.md"), "w", encoding="utf-8") as f:
    f.write(handbook_text)

with open(os.path.join(briefs_dir, "PLACEBO.md"), "w", encoding="utf-8") as f:
    f.write(placebo_text)

print("HANDBOOK.md and PLACEBO.md v2 successfully updated and token-balanced!")
