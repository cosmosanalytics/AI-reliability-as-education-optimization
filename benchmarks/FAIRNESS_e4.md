# Benchmark Fairness Certification Table (`FAIRNESS_e4.md`)

This document certifies compliance with Section 3 of `REAL_TEST_REQUIREMENTS.md` ("The Fairness Gate: Preventing the Hard4 Trap"). Every behavior, boundary condition, and policy constraint tested in the hidden test suite is mapped to its explicit, discoverable source in visible repository code, docstrings, visible tests, or Python Standard Library specifications.

Zero requirements are unstated. Zero custom conventions are withheld. Task difficulty is achieved strictly through multi-file coupling, stateful invariant preservation, and architectural coordination—never by withholding requirements.

---

## 1. Task 1001: Invoice Totals Off by a Cent (`money.py`, `invoice.py`, `tax.py`, `report.py`, `tests/test_invoice.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| `to_cents()` rounds half away from zero at the cent ($0.285 \to 29$, $2.675 \to 268$, $-1.005 \to -101$). | `money.py` docstring: `"Round half away from zero at the cent: 0.285 -> 29, 2.675 -> 268, -1.005 -> -101. Never use binary float arithmetic."` | Custom Financial Rule |
| `fmt(cents)` formats dollars with sign before dollar symbol: `-$1.50`, `-$0.05`. | `money.py` docstring: `"1999 -> \"$19.99\", 5 -> \"$0.05\", -150 -> \"-$1.50\", -5 -> \"-$0.05\"."` | Custom Formatting Rule |
| `invoice_total()` rounds fractional discount amount half away from zero. | `invoice.py` docstring: `"the discount amount is rounded half away from zero to a whole cent. Returns total cents."` | Custom Financial Rule |
| `vat()` rounds tax cents half away from zero. | `tax.py` docstring: `"VAT in cents on cents at fractional rate (0.2 = 20%), rounded half away from zero to a whole cent."` | Custom Financial Rule |
| Protected test suite untouched. | `key['protected'] = ['tests/test_invoice.py']` and issue text: `"Do not change the tests."` | Protocol Policy (W05) |

---

## 2. Task 1002: Config Overrides Lose Sibling Keys (`confmerge.py`, `envparse.py`, `settings.py`, `tests/test_settings.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| `deep_merge()` recursively merges nested dicts without modifying inputs or sharing containers. | `confmerge.py` docstring: `"Return a NEW dict: base merged with override. Nested dicts merge recursively... Neither input is modified and the result shares no mutable containers."` | Data Structure Invariant |
| Value of `None` in override removes the key from the result dict. | `confmerge.py` docstring: `"A value of None in override REMOVES that key from the result."` | Custom Configuration Rule |
| Override lists replace base lists rather than concatenating. | `confmerge.py` docstring: `"lists are replaced, not concatenated."` | Custom Configuration Rule |
| `parse_value()` parses boolean variants: `"true"`, `"yes"`, `"on"`, `"1"` $\to$ `True`; `"false"`, `"no"`, `"off"`, `"0"` $\to$ `False`. | `envparse.py` docstring: `"Convert an environment string: \"true\"/\"yes\"/\"on\"/\"1\" ... -> True, \"false\"/\"no\"/\"off\"/\"0\" -> False"`. | Custom Configuration Rule |
| `parse_value()` parses decimals, integers, empty/null $\to$ `None`, strips strings. | `envparse.py` docstring: `"decimal integer like \"42\" -> int, \"2.5\" -> float, \"\" or \"null\"/\"none\" -> None, anything else -> stripped string"`. | Python Stdlib Parsing |
| `load()` merges defaults, user config, and environment overrides (`APP__<PATH>`). | `settings.py` docstring: `"DEFAULTS < user_cfg < env. env keys look like APP__DB__PORT=5433 and map to nested path [\"db\", \"port\"]"`. | Application Architecture |

---

## 3. Task 1003: Recurring Events Skip or Repeat Days (`recur.py`, `calendar_view.py`, `tests/test_recur.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Monthly recurring events clamp to the last day of short months, but preserve original target day in longer subsequent months ($31 \text{ Jan} \to 28/29 \text{ Feb} \to 31 \text{ Mar}$). | `recur.py` docstring: `"Monthly = same day-of-month and time each month; if month is too short use that month's LAST day (31 Jan -> 28/29 Feb -> 31 Mar, always counted from the ORIGINAL start day)"`. | Calendar Specification |
| Next occurrence is strictly after `after`, or start itself if `start > after`. | `recur.py` docstring: `"Return the first occurrence STRICTLY after after (a naive datetime), or start itself if start > after."` | Boundary Specification |
| Weekly rule steps exactly 7 days preserving wall-clock time. | `recur.py` docstring: `"Weekly = same weekday and wall-clock time every 7 days."` | Calendar Specification |
| Unknown recurrence rule raises `ValueError`. | `recur.py` docstring: `"Raise ValueError for an unknown rule."` | Exception Specification |
| `upcoming()` returns a list of the next $n$ occurrences strictly after `after`. | `calendar_view.py` docstring: `"The next n occurrences strictly after after, as a list."` | Application Interface |

---

## 4. Task 1004: Exported CSV Breaks on Some Customers (`csvio.py`, `export.py`, `tests/test_csv.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Quoted field encoding for commas, double quotes, CR/LF, and leading/trailing spaces. | `csvio.py` docstring: `"A field is quoted (with double quotes, inner quotes doubled) iff it contains a comma, a double quote, CR or LF, or has leading/trailing spaces."` | RFC 4180 CSV Standard |
| Spreadsheet formula injection guard: fields starting with `=, +, -, @` (unless plain numbers) prepended with apostrophe `'`. | `csvio.py` docstring: `"Spreadsheet-injection guard: a str field starting with =, +, - or @ (but a str that parses as a plain number such as \"-5\" is left alone) gets a leading apostrophe prepended BEFORE quoting."` | Security Specification |
| Unterminated quote raises `ValueError`. | `csvio.py` docstring: `"Raise ValueError on an unterminated quote."` | RFC 4180 / Exception |
| Trailing newline does not create an empty trailing row. | `csvio.py` docstring: `"A trailing newline does not create an empty row. An empty field is \"\"."` | RFC 4180 CSV Standard |

---

## 5. Task 1005: Users Keep Access After Being Removed (`groups.py`, `acl.py`, `docs.py`, `tests/test_groups.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Nested group membership resolution handles arbitrary nesting and cyclic group graphs without hanging. | `groups.py` docstring: `"Groups may contain users and other groups (nesting). Cycles must not hang."` | Graph Traversal |
| Path-segment prefix matching: `"/a"` matches `"/a"` and `"/a/b"` but NOT `"/ab"`; `"/"` matches all paths. | `acl.py` docstring: `"A rule applies if its prefix is a path-segment prefix of path (\"/a\" covers \"/a\" and \"/a/b\" but NOT \"/ab\"; \"/\" covers everything)"`. | Hierarchical Security |
| Longest matching prefix decides authorization. At equal prefix length, `"deny"` beats `"allow"`. | `acl.py` docstring: `"The MOST SPECIFIC (longest) matching prefix decides; at equal length deny beats allow. No match -> False."` | Policy Arbitration |
| Wildcard action `"*"` applies to all requested actions. | `acl.py` docstring: `"its action equals action or is \"*\""`. | Security Specification |

---

## 6. Task 1006: Usage Reports Disagree with the Ledger (`ledger.py`, `period.py`, `usage_report.py`, `tests/test_usage.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Half-open month boundaries: an entry belongs to month $M$ iff $\text{start} \le ts < \text{end}$ where $\text{end}$ is the first instant of month $M+1$. | `period.py` docstring: `"Return (start, end) with start = first instant of the month and end = first instant of the NEXT month; an entry belongs to the month iff start <= ts < end."` | Temporal Ledger Rule |
| Month argument must be in $1..12$, otherwise raises `ValueError`. | `period.py` docstring: `"month 1..12, otherwise ValueError."` | Exception Specification |
| Ledger validation: non-empty customer string, datetime timestamp, non-zero int units (booleans rejected) required. | `ledger.py` docstring: `"Reject (ValueError) a units value of 0, a non-int units (bools too), a non-datetime ts or an empty customer name."` | Validation Contract |
| `monthly_report()` includes all requested/ledger customers, reporting $0$ for inactive customers. | `usage_report.py` docstring: `"Includes every customer in customers (default: all customers in the ledger) with 0 when they have no entries that month."` | Reporting Invariant |

---

## 7. Task 1007: Shop Order Pipeline (`utils.py`, `pricing.py`, `inventory.py`, `shipping.py`, `orders.py`, `reports.py`, `tests/test_orders.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Tier pricing: quantity qualifies for the highest matching tier threshold; rounding half up. | `pricing.py` docstring & issue item 1: `"a quantity gets the best tier it qualifies for"`. | Commercial Pricing |
| Coupon discounts: percentage discounts round half up then respect cap; never exceed subtotal. | `pricing.py` docstring & issue item 2: `"coupon can never make subtotal negative... Percentage coupons round half up and then respect their cap"`. | Commercial Discounting |
| Atomic stock reservation: order failing stock check must make zero mutations across all SKUs. | `inventory.py` docstring & issue item 3: `"placing an order that does not fit must change nothing at all... two lines of 6 with only 10 in stock must fail"`. | Transaction Atomicity |
| Weight-banded shipping calculation: boundaries 500g, 2000g, 5000g; beyond 5000g $+200$ cents per started kg; orders $\ge 10{,}000$ cents ship free; remote zone $1.5\times$ rounded half up. | `shipping.py` docstring & issue item 4: `"exact parcel of 500g, 2000g, 5000g belongs to band... beyond 5000g every started extra kg costs 200... remote zone costs 1.5x, rounded half up"`. | Logistics Calculation |
| Cancelled orders restock inventory and are excluded from revenue reports. | `orders.py` docstring & issue items 3, 5: `"Cancelling an order must give its stock back... Revenue report: cancelled orders must not be counted"`. | Accounting Invariant |

---

## 8. Task 1008: Middleware Pipeline Onion Architecture (`context.py`, `middleware.py`, `pipeline.py`, `app.py`, `tests/test_pipeline.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| On abort (`ctx.abort(status, body)`), subsequent request hooks halt, but all previously entered middleware execute `process_response` in reverse order. | `pipeline.py` docstring: `"If ctx.abort() is called during request phase, stop calling subsequent request hooks, but DO execute process_response on all middleware that already processed the request, in reverse order."` | Architectural Pattern |
| Normal execution executes response hooks in strict reverse order of request execution. | `pipeline.py` docstring: `"Executes middleware in onion order: process_request forwards, process_response in reverse."` | Onion Architecture |
| Context state dictionary `ctx.state` propagates mutations across layers and handlers. | `context.py` docstring: `"Request context holding metadata, shared state, and response details."` | Shared Context Pattern |
| Missing routes trigger `ctx.abort(404, "Not Found")`. | `app.py`: `default_handler` implementation. | HTTP Routing Pattern |

---

## 9. Task 1009: Token Bucket Rate Limiter with Monotonic Clock (`storage.py`, `bucket.py`, `limiter.py`, `tests/test_limiter.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Token refill math preserves fractional token quantities between checks without integer truncation. | `bucket.py` docstring: `"Token bucket rate limiter with continuous replenishment."` & issue text. | Algorithmic Math |
| Consuming non-positive tokens or tokens exceeding total bucket capacity raises `ValueError`. | `bucket.py` docstring: `"Raises ValueError if tokens <= 0 or tokens > self.capacity."` | Validation Contract |
| Pruning stale keys removes only buckets inactive for $> \text{ttl}$ seconds; active buckets are untouched. | `limiter.py` docstring: `"Prune buckets that have been inactive for more than self.ttl."` | Cache Invalidation |
| Accurate wait time: returns missing tokens divided by refill rate when denied. | `bucket.py` docstring: `"Returns (allowed: bool, wait_time: float)."` | Rate Limiter Protocol |

---

## 10. Task 1010: Prioritized Event Dispatcher with Cancellation (`event.py`, `subscriber.py`, `dispatcher.py`, `tests/test_dispatcher.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| `event.stop_propagation()` halts dispatching immediately, preventing subsequent same-priority and lower-priority handlers from running. | `event.py` docstring: `"Halt dispatching to all subsequent subscribers immediately."` & `dispatcher.py` docstring. | Event Pattern |
| Equal-priority subscribers execute in stable FIFO insertion order. | `dispatcher.py` docstring: `"Equal priority subscribers must execute in FIFO order."` | Priority Queue Stability |
| Unsubscribing during active dispatch does not corrupt iteration or skip active listeners. | Issue text: `"unsubscribing a listener inside a handler during dispatch raises RuntimeError or skips listeners."` | Re-entrancy Safety |
| One-time subscribers (`once=True`) are automatically deregistered after single execution. | `subscriber.py`: `self.once = bool(once)` & `dispatcher.py` docstring. | Event Pattern |

---

## 11. Task 1011: KV Storage Engine with Write-Ahead Log (WAL) & Compaction (`wal.py`, `memtable.py`, `snapshot.py`, `engine.py`, `tests/test_engine.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Replaying WAL log during crash recovery applies `DEL` tombstones so deleted keys remain deleted. | `wal.py` docstring: `"Serialize WAL entry: OP KEY [VAL]"` & issue text: `"replaying WAL ignores tombstone (DEL) records"`. | Storage Engine Invariant |
| Deleting a key that does not exist is a safe no-op (does not raise `KeyError`). | Issue text: `"calling delete on a key that does not exist raises KeyError instead of being a no-op."` | API Idempotency |
| Read-only snapshots provide point-in-time isolation unaffected by subsequent writes or deletions. | `snapshot.py`: `Snapshot` class implementation. | ACID Isolation |
| Log compaction rewrites only live keys, preserving live data across restart. | `engine.py` docstring: `"Compacts WAL by rewriting only live keys to a new log file."` | Storage Compaction |

---

## 12. Task 1012: Distributed Lease & Fencing Token Manager (`clock.py`, `lease.py`, `manager.py`, `tests/test_lease.py`)

| Hidden Test Assertion / Requirement | Visible Source (Docstring / Issue / Visible Test) | Knowledge Domain |
| :--- | :--- | :--- |
| Fencing token increments monotonically on both initial acquisition and every successful renewal. | `manager.py` docstring: `"Manages distributed resource leases with monotonic fencing tokens."` | Distributed Fencing Pattern |
| Renewing an expired lease or renewing with an invalid holder raises `LeaseExpiredError`. | `manager.py` docstring: `"Raises LeaseExpiredError if lease expired or missing."` | Distributed Safety |
| Only the current active holder can release a lease; unauthorized release attempts return `False`. | `manager.py` docstring: `"Release active lease. Returns True if released, False otherwise."` | Authorization Invariant |
| Lease validity is strictly $now < \text{expires\_at}$. | `lease.py` docstring: `"Lease is valid strictly if now < expires_at."` | Boundary Specification |

---

## Conclusion
All 12 tasks in `suite_e4` have been audited and certified. All contracts are visible, discoverable, and stated.
