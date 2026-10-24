import os
import tiktoken

repo_root = "C:/Users/richa/ai-engineering/repo_push"
briefs_dir = os.path.join(repo_root, "briefs")
enc = tiktoken.get_encoding("cl100k_base")

handbook_text = """# Engineering Standards and House Conventions (`HANDBOOK.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule H01: Test Directory Protection
Never modify, delete, or create files within any `tests/` directory. All bug fixes, refactorings, and feature additions must reside strictly within production source modules. Test files define immutable correctness contracts.

### Rule H02: Monetary Arithmetic and Banker's Rounding
All monetary calculations, prices, discounts, and tax computations must be conducted using fixed-point integer cents or `decimal.Decimal` with banker's rounding (`ROUND_HALF_EVEN`). Floating-point arithmetic and naive truncation are strictly prohibited. In cases of exact ties at half-cents, round to the nearest even cent.

### Rule H03: Input Immutability and Defensive Copying
Functions accepting mutable containers (`dict`, `list`, `set`) must never mutate caller-supplied arguments in place. Always perform defensive deep copies or construct new collection instances prior to modification. Functions must return newly allocated data structures.

### Rule H04: Deterministic Exception Hierarchy
Always raise explicit standard exception types:
- Raise `ValueError` when an argument has the appropriate type but an invalid value, empty payload, or out-of-range magnitude.
- Raise `KeyError` when accessing an unregistered configuration or lookup key.
- Raise `PermissionError` when an operation is denied by access control policies.
Never raise unadorned `Exception` or return sentinel `None` to indicate failure.

### Rule H05: Half-Open Interval Representation
All temporal periods, date ranges, and numerical spans must follow the half-open interval convention $[\\text{start}, \\text{end})$: inclusive of the start boundary and strictly exclusive of the end boundary. A reporting period covering day $D_1$ through day $D_2$ includes timestamps where $\\text{start} \\le t < \\text{end}$.

### Rule H06: Path and Prefix Normalization
Resource paths and access control rule prefixes must be normalized before matching. Strip all redundant trailing slashes from prefixes (except the root `"/"`) before splitting on path segments. A prefix rule of `"/api/"` covers `"/api"` and `"/api/v1"`, but never `"/apiv1"`.

### Rule H07: Stable Ordering and Deterministic Tie-Breaking
When prioritizing queues, scheduled tasks, or dispatched events, ties in primary priority must be broken deterministically using secondary keys (such as chronological registration sequence or unique task ID in ascending order). Execution order must be 100% reproducible across invocations.

### Rule H08: Safe Iteration and Reentrant Mutation
Event dispatchers, observer registries, and middleware pipelines must iterate over snapshot copies of listener lists (`list(self.listeners)`). Handlers must be allowed to register, deregister, or cancel subsequent listeners during active event dispatch without raising `RuntimeError`.

### Rule H09: Injectable Clocks for Temporal Logic
Any component managing stateful expiry, TTL leases, rate-limiting windows, or timeouts must accept an optional injectable clock function parameter (`clock=time.monotonic`). Default to system time but permit callers to provide custom deterministic time sources in test environments.

### Rule H10: RFC 4180 CSV Serialization and Escaping
CSV serialization and parsing must conform to RFC 4180: any field containing commas, double quotes, line breaks (`\\r` or `\\n`), or leading/trailing whitespace must be enclosed in double quotes. Internal double quotes must be escaped by doubling (`""`). Unterminated quotes must raise `ValueError`.
"""

placebo_text = """# Engineering Standards and House Conventions (`PLACEBO.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule P01: Code Formatting and Maximum Line Length
All source code files must strictly comply with automated PEP 8 formatting standards and linting rules. Enforce a maximum line length of 88 characters for all statement bodies, list comprehensions, and function signatures. Split long chained method invocations and complex expressions across multiple indented lines with closing delimiters matching the opening indentation column.

### Rule P02: Structured Documentation and Docstring Style
All public modules, classes, and exported functions must include comprehensive Google-style docstrings. Provide explicit `Args:`, `Returns:`, and `Raises:` documentation blocks describing parameter expectations, output representations, and potential failure conditions. Include descriptive narrative prose summarizing overall component behavior and architecture.

### Rule P03: Variable Naming and Identifier Conventions
Identifiers across the repository must follow unambiguous naming conventions: use `snake_case` for module-level functions and variable instances, `PascalCase` for class definitions, and `UPPER_SNAKE_CASE` for configuration constants. Never utilize ambiguous single-letter variable names outside of standard loop index counters (`i`, `j`).

### Rule P04: Type Annotations and Static Verification
All function parameter lists and return signatures must declare complete static type annotations. Utilize modern standard library typing constructs (`Optional[T]`, `List[T]`, `Dict[K, V]`, `Callable`, `Tuple[T, ...]`). Ensure type signatures precisely describe allowable container contents and avoid ambiguous generic `Any` declarations whenever possible in production modules.

### Rule P05: Module Organization and Import Grouping
Source file imports must be organized into three distinct blocks separated by single blank lines: standard library modules, external third-party dependencies, and internal package modules. Within each individual block, sort imported symbol names in strict ascending lexicographical order. Wildcard imports are completely prohibited.

### Rule P06: Structured Logging and Telemetry Standards
Use the standard library `logging` framework rather than unbuffered standard console streams. Obtain module-specific logger instances via `logging.getLogger(__name__)`. Provide contextual key-value attributes in log messages to facilitate centralized log aggregation and tracing across distributed processes. Never utilize unadorned `print()` statements for diagnostic information or operational tracking.

### Rule P07: Error Message Phrasing and Clarity
Exception error messages must be crafted with professional clarity, operational precision, and consistency across modules. Begin error descriptions with an uppercase character and omit trailing punctuation marks. Explicitly specify the problematic parameter identifier and offending value within the message to accelerate developer remediation and triage.

### Rule P08: Hygiene and Dead Code Elimination
Maintain impeccable codebase hygiene by removing unused imports, commented-out obsolete code fragments, and temporary debugging routines before committing changes to version control. Never commit placeholder `# TODO` or `# FIXME` markers without referencing an active tracking ticket identifier in the issue tracker.

### Rule P09: Execution Profiling and Measurement Hooks
High-throughput processing pipelines, background thread workers, and batch processing loops should integrate non-intrusive latency profiling hooks. Instrument critical section boundaries with standardized timing metrics or context managers to surface execution bottlenecks without modifying the underlying business domain logic.

### Rule P10: Source Header Declarations and Licensing
Every newly created repository source file must begin with standard repository file header declarations. Include standardized copyright notices, licensing references, and UTF-8 encoding declarations at the absolute top of the source file prior to any executable logic, import blocks, or module docstrings.
"""

tok_h = len(enc.encode(handbook_text))
tok_p = len(enc.encode(placebo_text))
diff_pct = abs(tok_h - tok_p) / tok_h * 100

print(f"Handbook tokens: {tok_h}")
print(f"Placebo tokens:  {tok_p}")
print(f"Difference:      {abs(tok_h - tok_p)} tokens ({diff_pct:.2f}%)")

with open(os.path.join(briefs_dir, "HANDBOOK.md"), "w", encoding="utf-8") as f:
    f.write(handbook_text)

with open(os.path.join(briefs_dir, "PLACEBO.md"), "w", encoding="utf-8") as f:
    f.write(placebo_text)

print("HANDBOOK.md and PLACEBO.md written successfully.")
