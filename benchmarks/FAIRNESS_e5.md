# Suite E5 Fairness Audit and Benchmark Specifications (`FAIRNESS_e5.md`)

This document establishes the binding fairness audit and specification matrix for `suite_e5` (28 template-generated instances across 7 bug families), adhering strictly to Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md`.

## 1. Summary Statistics
- **Total Evaluated Instances:** 28
- **Bug Families (7):** `money_rounding` (4), `config_merge` (4), `calendar_recurrence` (4), `csv_roundtrip` (4), `permission_prefix` (4), `event_ordering` (4), `cache_ttl` (4)
- **Class Tag Breakdown:**
  - `STATED`: 11 instances (all hidden requirements present in ticket/docstrings)
  - `TAUGHT`: 10 instances (house conventions supplied strictly via `HANDBOOK.md`)
  - `DISTRACTOR`: 3 instances (blind application of handbook rule causes failure)
  - `TRANSFER`: 4 instances (unseen family measuring cross-domain generalization)
- **Structural Variants:**
  - Hidden Root Cause (outside traceback file): 11 / 28 (39.3%, >= 33.3% required)
  - Visible-Test-Sensitive (naive fix fails visible test): 11 / 28 (39.3%, >= 33.3% required)

---

## 2. Fairness Standards by Class Tag
1. **STATED:** Every requirement tested by hidden assertions is explicitly documented in the issue description or in the docstring of files provided in the minimal context package (`traceback_files`). Zero secret assumptions.
2. **TAUGHT:** Requirements not obvious from general programming intuition (such as company-specific banker's rounding rules, immutable config deep-copying, deterministic ascending secondary tie-breaking, half-open date interval indexing, RFC 4180 escaping, or injectable clock defaults) are specified sentence-for-sentence in `briefs/HANDBOOK.md` and absent from `briefs/PLACEBO.md`.
3. **DISTRACTOR:** Intentionally presents an edge case where applying a handbook rule indiscriminately breaks intended functionality (e.g., stripping slashes when exact literal path matching is requested, or forcibly deep-copying when in-place accumulator mutation is explicitly specified).
4. **TRANSFER:** Evaluates the `cache_ttl` family without any corresponding worked examples in `briefs/P3.md`, verifying whether agents can synthesize general educational principles (Rule H09 injectable clocks) in novel contexts.

---

## 3. Instance Matrix

| ID | Family | Class Tag | Name | Hidden Root Cause? | Visible-Test Sensitive? | Handbook Rule | Visible Source / Hidden Assertion Contract |
|:---|:---|:---|:---|:---:|:---:|:---|:---|
| `2001` | `money_rounding` | **`STATED`** | Order Tax Calculation | Yes | No | `Rule H02` | Order tax calculation truncates fractional cents instead of using banker's rounding. |
| `2002` | `money_rounding` | **`TAUGHT`** | Invoice Discount Proration | No | Yes | `Rule H02` | Prorated discount lines do not sum up to total discount and violate company rounding rules. |
| `2003` | `money_rounding` | **`TAUGHT`** | Multi-currency FX Ledger | Yes | No | `Rule H02` | Ledger FX entries disagree on half-cent boundaries. |
| `2004` | `money_rounding` | **`DISTRACTOR`** | Coupon Rebate Allocation | No | Yes | `Rule H02 (Distractor: ticket explicitly overrides with ceiling rule)` | Rebates must round up per regulatory mandate, but currently truncate. |
| `2005` | `config_merge` | **`STATED`** | Hierarchical App Settings | No | Yes | `Rule H03` | merge_settings overwrites entire nested dictionaries, losing sibling configuration parameters. |
| `2006` | `config_merge` | **`TAUGHT`** | Plugin Parameter Resolver | Yes | No | `Rule H03` | Plugin parameter resolution corrupts global default structures due to mutable reference sharing. |
| `2007` | `config_merge` | **`STATED`** | Cloud Environment Layering | Yes | No | `Rule H03` | Layering cloud environments drops node cluster sizing configuration. |
| `2008` | `config_merge` | **`DISTRACTOR`** | Audit Policy Config | No | Yes | `Rule H03 (Distractor: ticket explicitly mandates in-place mutation)` | In-place policy mutation cache returns new dict instance, breaking caller identity contract. |
| `2009` | `calendar_recurrence` | **`STATED`** | Monthly Subscription Month-End | No | No | `Rule H05` | Billing date generator crashes with ValueError when billing on day 31. |
| `2010` | `calendar_recurrence` | **`TAUGHT`** | Quarterly Compliance Audit Schedule | Yes | No | `Rule H05` | Audit window filters include events occurring on the concluding cutoff boundary. |
| `2011` | `calendar_recurrence` | **`STATED`** | Shift Roster Generator | No | Yes | `Rule H05` | Roster generator outputs consecutive daily shifts rather than weekly intervals. |
| `2012` | `calendar_recurrence` | **`TAUGHT`** | Billing Period Usage Aggregator | Yes | No | `Rule H05` | Monthly usage reports drop events occurring in the final days of the month. |
| `2013` | `csv_roundtrip` | **`STATED`** | Export User Profile with Commas | No | Yes | `Rule H10` | CSV serializer outputs unquoted fields containing commas, corrupting tabular exports. |
| `2014` | `csv_roundtrip` | **`TAUGHT`** | Data Ingestion Pipeline | No | No | `Rule H10, Rule H04` | CSV reader silently accepts corrupted records with unterminated quotes without raising ValueError. |
| `2015` | `csv_roundtrip` | **`STATED`** | Audit Log Stream Exporter | Yes | No | `Rule H10` | Audit log exporter strips internal quotation marks, corrupting forensic event payloads. |
| `2016` | `csv_roundtrip` | **`DISTRACTOR`** | Tab-Separated TSV Batch Parser | No | No | `Rule H10 (Distractor: ticket explicitly defines raw TSV parsing)` | TSV parser splits on commas instead of tabs, failing on comma-separated values inside tab columns. |
| `2017` | `permission_prefix` | **`STATED`** | API Endpoint Access Control | No | Yes | `Rule H06` | ACL check allows access to unauthorized endpoints due to naive string prefix matching. |
| `2018` | `permission_prefix` | **`TAUGHT`** | Multi-tenant Document Permission | No | Yes | `Rule H06` | Document ACL ignores rules whose path prefixes contain trailing slashes. |
| `2019` | `permission_prefix` | **`STATED`** | Admin Group Role Inheritance | Yes | No | `Rule H06` | Users in nested groups fail to inherit administrative privileges. |
| `2020` | `permission_prefix` | **`TAUGHT`** | Wildcard Action Matrix | No | No | `Rule H04` | Action authorization gate returns boolean False instead of raising PermissionError on violation. |
| `2021` | `event_ordering` | **`STATED`** | Async Job Priority Dispatcher | No | No | `Rule H07` | Job dispatcher breaks priority ties arbitrarily, violating FIFO sequence. |
| `2022` | `event_ordering` | **`TAUGHT`** | Webhook Event Bus | No | Yes | `Rule H08` | Event bus emits crash or skip listeners when a subscriber unregisters inside a callback. |
| `2023` | `event_ordering` | **`STATED`** | Task Scheduler with Preemption | No | Yes | `Rule H07` | Task scheduler fails to prioritize higher priority tasks added dynamically. |
| `2024` | `event_ordering` | **`TAUGHT`** | Telemetry Metric Collector | Yes | No | `Rule H07` | Telemetry buffer emits metrics in arbitrary insertion order regardless of severity level. |
| `2025` | `cache_ttl` | **`TRANSFER`** | In-Memory Key-Value Store with TTL | No | No | `Rule H09` | TTLCache retains expired entries indefinitely and fails to support injectable clocks. |
| `2026` | `cache_ttl` | **`TRANSFER`** | Session Token Cache | Yes | No | `Rule H04, Rule H09` | Session validator fails to raise KeyError when inspecting expired user sessions. |
| `2027` | `cache_ttl` | **`TRANSFER`** | Rate Limiting Sliding Window Cache | Yes | No | `Rule H09` | RateLimiter fails to prune expired timestamps from sliding window, blocking clients permanently. |
| `2028` | `cache_ttl` | **`TRANSFER`** | Tiered Multi-level Cache | No | Yes | `Rule H09` | TieredCache fails to query L2 fallback store on L1 cache miss. |

---

## 4. Detailed Fairness and Mutation Verification

### Task 2001: Order Tax Calculation
- **Family:** `money_rounding`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H02`
- **Traceback Files Provided to Baseline:** `pricing.py`
- **Issue Summary:** Order tax calculation truncates fractional cents instead of using banker's rounding.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2002: Invoice Discount Proration
- **Family:** `money_rounding`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H02`
- **Traceback Files Provided to Baseline:** `discount.py`
- **Issue Summary:** Prorated discount lines do not sum up to total discount and violate company rounding rules.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2003: Multi-currency FX Ledger
- **Family:** `money_rounding`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H02`
- **Traceback Files Provided to Baseline:** `ledger.py`
- **Issue Summary:** Ledger FX entries disagree on half-cent boundaries.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2004: Coupon Rebate Allocation
- **Family:** `money_rounding`
- **Class Tag:** `DISTRACTOR`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H02 (Distractor: ticket explicitly overrides with ceiling rule)`
- **Traceback Files Provided to Baseline:** `rebate.py`
- **Issue Summary:** Rebates must round up per regulatory mandate, but currently truncate.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2005: Hierarchical App Settings
- **Family:** `config_merge`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H03`
- **Traceback Files Provided to Baseline:** `settings.py`
- **Issue Summary:** merge_settings overwrites entire nested dictionaries, losing sibling configuration parameters.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2006: Plugin Parameter Resolver
- **Family:** `config_merge`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H03`
- **Traceback Files Provided to Baseline:** `plugin_manager.py`
- **Issue Summary:** Plugin parameter resolution corrupts global default structures due to mutable reference sharing.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2007: Cloud Environment Layering
- **Family:** `config_merge`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H03`
- **Traceback Files Provided to Baseline:** `app.py`
- **Issue Summary:** Layering cloud environments drops node cluster sizing configuration.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2008: Audit Policy Config
- **Family:** `config_merge`
- **Class Tag:** `DISTRACTOR`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H03 (Distractor: ticket explicitly mandates in-place mutation)`
- **Traceback Files Provided to Baseline:** `fast_merge.py`
- **Issue Summary:** In-place policy mutation cache returns new dict instance, breaking caller identity contract.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2009: Monthly Subscription Month-End
- **Family:** `calendar_recurrence`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H05`
- **Traceback Files Provided to Baseline:** `recurrence.py`
- **Issue Summary:** Billing date generator crashes with ValueError when billing on day 31.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2010: Quarterly Compliance Audit Schedule
- **Family:** `calendar_recurrence`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H05`
- **Traceback Files Provided to Baseline:** `audit_manager.py`
- **Issue Summary:** Audit window filters include events occurring on the concluding cutoff boundary.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2011: Shift Roster Generator
- **Family:** `calendar_recurrence`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H05`
- **Traceback Files Provided to Baseline:** `roster.py`
- **Issue Summary:** Roster generator outputs consecutive daily shifts rather than weekly intervals.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2012: Billing Period Usage Aggregator
- **Family:** `calendar_recurrence`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H05`
- **Traceback Files Provided to Baseline:** `usage.py`
- **Issue Summary:** Monthly usage reports drop events occurring in the final days of the month.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2013: Export User Profile with Commas
- **Family:** `csv_roundtrip`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H10`
- **Traceback Files Provided to Baseline:** `csv_format.py`
- **Issue Summary:** CSV serializer outputs unquoted fields containing commas, corrupting tabular exports.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2014: Data Ingestion Pipeline
- **Family:** `csv_roundtrip`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H10, Rule H04`
- **Traceback Files Provided to Baseline:** `csv_reader.py`
- **Issue Summary:** CSV reader silently accepts corrupted records with unterminated quotes without raising ValueError.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2015: Audit Log Stream Exporter
- **Family:** `csv_roundtrip`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H10`
- **Traceback Files Provided to Baseline:** `exporter.py`
- **Issue Summary:** Audit log exporter strips internal quotation marks, corrupting forensic event payloads.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2016: Tab-Separated TSV Batch Parser
- **Family:** `csv_roundtrip`
- **Class Tag:** `DISTRACTOR`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H10 (Distractor: ticket explicitly defines raw TSV parsing)`
- **Traceback Files Provided to Baseline:** `tsv_parser.py`
- **Issue Summary:** TSV parser splits on commas instead of tabs, failing on comma-separated values inside tab columns.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2017: API Endpoint Access Control
- **Family:** `permission_prefix`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H06`
- **Traceback Files Provided to Baseline:** `acl.py`
- **Issue Summary:** ACL check allows access to unauthorized endpoints due to naive string prefix matching.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2018: Multi-tenant Document Permission
- **Family:** `permission_prefix`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H06`
- **Traceback Files Provided to Baseline:** `doc_perm.py`
- **Issue Summary:** Document ACL ignores rules whose path prefixes contain trailing slashes.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2019: Admin Group Role Inheritance
- **Family:** `permission_prefix`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H06`
- **Traceback Files Provided to Baseline:** `evaluator.py`
- **Issue Summary:** Users in nested groups fail to inherit administrative privileges.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2020: Wildcard Action Matrix
- **Family:** `permission_prefix`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H04`
- **Traceback Files Provided to Baseline:** `action_gate.py`
- **Issue Summary:** Action authorization gate returns boolean False instead of raising PermissionError on violation.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2021: Async Job Priority Dispatcher
- **Family:** `event_ordering`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H07`
- **Traceback Files Provided to Baseline:** `dispatcher.py`
- **Issue Summary:** Job dispatcher breaks priority ties arbitrarily, violating FIFO sequence.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2022: Webhook Event Bus
- **Family:** `event_ordering`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H08`
- **Traceback Files Provided to Baseline:** `bus.py`
- **Issue Summary:** Event bus emits crash or skip listeners when a subscriber unregisters inside a callback.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2023: Task Scheduler with Preemption
- **Family:** `event_ordering`
- **Class Tag:** `STATED`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H07`
- **Traceback Files Provided to Baseline:** `scheduler.py`
- **Issue Summary:** Task scheduler fails to prioritize higher priority tasks added dynamically.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2024: Telemetry Metric Collector
- **Family:** `event_ordering`
- **Class Tag:** `TAUGHT`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H07`
- **Traceback Files Provided to Baseline:** `collector.py`
- **Issue Summary:** Telemetry buffer emits metrics in arbitrary insertion order regardless of severity level.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2025: In-Memory Key-Value Store with TTL
- **Family:** `cache_ttl`
- **Class Tag:** `TRANSFER`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H09`
- **Traceback Files Provided to Baseline:** `ttl_cache.py`
- **Issue Summary:** TTLCache retains expired entries indefinitely and fails to support injectable clocks.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2026: Session Token Cache
- **Family:** `cache_ttl`
- **Class Tag:** `TRANSFER`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H04, Rule H09`
- **Traceback Files Provided to Baseline:** `session_store.py`
- **Issue Summary:** Session validator fails to raise KeyError when inspecting expired user sessions.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2027: Rate Limiting Sliding Window Cache
- **Family:** `cache_ttl`
- **Class Tag:** `TRANSFER`
- **Hidden Root Cause Outside Traceback:** `Yes`
- **Visible-Test Sensitive:** `No`
- **Handbook Citations:** `Rule H09`
- **Traceback Files Provided to Baseline:** `rate_limiter.py`
- **Issue Summary:** RateLimiter fails to prune expired timestamps from sliding window, blocking clients permanently.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

### Task 2028: Tiered Multi-level Cache
- **Family:** `cache_ttl`
- **Class Tag:** `TRANSFER`
- **Hidden Root Cause Outside Traceback:** `No`
- **Visible-Test Sensitive:** `Yes`
- **Handbook Citations:** `Rule H09`
- **Traceback Files Provided to Baseline:** `tiered_cache.py`
- **Issue Summary:** TieredCache fails to query L2 fallback store on L1 cache miss.
- **Pre-flight Status:** Verified offline via `tests/test_suite_e5_preflight.py`:
  - Gold Reference (`ref`): 100% strict pass (functional tests pass, zero violations, no tamper).
  - Unpatched Baseline: 100% failure on hidden test overlay.
  - Mutant 1 (`mutant1`): Fails hidden test overlay (mutation verified).
  - Mutant 2 (`mutant2`): Fails hidden test overlay (mutation verified).

