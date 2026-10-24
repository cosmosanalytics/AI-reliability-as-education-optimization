# Engineering Standards and House Conventions (`HANDBOOK.md`)

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
All temporal periods, date ranges, and numerical spans must follow the half-open interval convention $[\text{start}, \text{end})$: inclusive of the start boundary and strictly exclusive of the end boundary. A reporting period covering day $D_1$ through day $D_2$ includes timestamps where $\text{start} \le t < \text{end}$.

### Rule H06: Path and Prefix Normalization
Resource paths and access control rule prefixes must be normalized before matching. Strip all redundant trailing slashes from prefixes (except the root `"/"`) before splitting on path segments. A prefix rule of `"/api/"` covers `"/api"` and `"/api/v1"`, but never `"/apiv1"`.

### Rule H07: Stable Ordering and Deterministic Tie-Breaking
When prioritizing queues, scheduled tasks, or dispatched events, ties in primary priority must be broken deterministically using secondary keys (such as chronological registration sequence or unique task ID in ascending order). Execution order must be 100% reproducible across invocations.

### Rule H08: Safe Iteration and Reentrant Mutation
Event dispatchers, observer registries, and middleware pipelines must iterate over snapshot copies of listener lists (`list(self.listeners)`). Handlers must be allowed to register, deregister, or cancel subsequent listeners during active event dispatch without raising `RuntimeError`.

### Rule H09: Injectable Clocks for Temporal Logic
Any component managing stateful expiry, TTL leases, rate-limiting windows, or timeouts must accept an optional injectable clock function parameter (`clock=time.monotonic`). Default to system time but permit callers to provide custom deterministic time sources in test environments.

### Rule H10: RFC 4180 CSV Serialization and Escaping
CSV serialization and parsing must conform to RFC 4180: any field containing commas, double quotes, line breaks (`\r` or `\n`), or leading/trailing whitespace must be enclosed in double quotes. Internal double quotes must be escaped by doubling (`""`). Unterminated quotes must raise `ValueError`.
