# Benchmark Validation & Fairness Audit (`FAIRNESS_e5.md`)

This document establishes the construct-validity, task fairness, and per-assertion audit for **Suite E5** (28 instances across 7 bug families), complying with Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md` and Round 9 review requirements.

---

## 1. Executive Summary & Structural Invariants

| Invariant Dimension | Requirement | Measured / Audited Value | Status |
|:---|:---|:---|:---:|
| **Total Instances** | $\ge 24$ instances | **28 instances** across 7 bug families (4 per family) | **PASS** |
| **Class: STATED** | Standard instructions | **10 instances** (35.7%) | **PASS** |
| **Class: TAUGHT** | $\ge 8$ instances | **11 instances** (39.3%) | **PASS** |
| **Class: DISTRACTOR** | $\ge 2$ instances | **3 instances** (10.7%, Tasks 2004, 2008, 2016) | **PASS** |
| **Class: TRANSFER** | $\ge 3$ instances | **4 instances** (14.3%, Tasks 2025–2028 in `cache_ttl`) | **PASS** |
| **Hidden Root Cause (HRC)** | $\ge 33.3\%$ | **12 / 28 (42.9%)** outside traceback file | **PASS** |
| **Visible Test Sensitive (VTS)** | $\ge 33.3\%$ | **12 / 28 (42.9%)** naive fix fails visible test | **PASS** |
| **Root Cause Only w/ Exploration** | Tagged on all HRC | **12 / 12 (100%)** require Factor $u$ exploration | **PASS** |
| **Provided File Hints** | 0 `# BUG` / `# FIX` / `# TODO` | **0 hint comments** across all 28 repositories | **PASS** |
| **Repository Line Count** | 40–120 non-test lines | **40–80 lines across 2–4 files** per task | **PASS** |
| **Tune / Held-Out Split** | Stratified, fixed seed 42 | **12 Tune** (screening) / **16 Held-Out** (confirmation) | **PASS** |

---

## 2. Pre-Registered Tune / Held-Out Partition

- **Screening Experiment Split (Tuning Set, 12 instances):**
  `[2001, 2002, 2005, 2006, 2009, 2010, 2013, 2014, 2017, 2018, 2021, 2022]`
  - Stratification: Exactly 2 instances from each of Families 1–6 (6 STATED, 6 TAUGHT).
- **Confirmatory Study Split (Held-Out Set, 16 instances):**
  `[2003, 2004, 2007, 2008, 2011, 2012, 2015, 2016, 2019, 2020, 2023, 2024, 2025, 2026, 2027, 2028]`
  - Stratification: 2 instances from each of Families 1–6 (4 STATED, 5 TAUGHT, 3 DISTRACTOR) + **all 4 TRANSFER instances** from Family 7.

---

## 3. Comprehensive Per-Assertion Fairness Table (S-4 Requirement)

This table documents every assertion tested in the hidden suite, where its specification originates, whether an agent can derive it without the house handbook, and its experimental class tag.

| Task ID | Bug Family | Hidden Test Assertion | Visible Source (Ticket / Docstring / Handbook) | Derivable Without Handbook? | Class Tag | Split |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **2001** | `money_rounding` | `test_bankers_rounding_half_cents` | pricing.py docstring: 'Tax calculation must use banker's rounding (round half to even)' | **Yes** | `STATED` | Tune |
| **2001** | `money_rounding` | `test_tax_engine_direct` | tax_engine.py module contract | **Yes** | `STATED` | Tune |
| **2002** | `money_rounding` | `test_half_cent_bankers_rounding` | HANDBOOK.md Rule H02: Banker's rounding on half-cent boundaries | **No** | `TAUGHT` | Tune |
| **2002** | `money_rounding` | `test_three_line_unallocated` | HANDBOOK.md Rule H02: Banker's rounding on half-cent boundaries | **No** | `TAUGHT` | Tune |
| **2003** | `money_rounding` | `test_bankers_rounding_fx` | HANDBOOK.md Rule H02: Banker's rounding on half-cents | **No** | `TAUGHT` | Held-Out |
| **2003** | `money_rounding` | `test_fx_engine_direct` | HANDBOOK.md Rule H02: Banker's rounding on half-cents | **No** | `TAUGHT` | Held-Out |
| **2004** | `money_rounding` | `test_statutory_ceiling_withholding` | payroll.py docstring: 'MUST round fractional cents UP (ceiling)' | **Yes** | `DISTRACTOR` | Held-Out |
| **2005** | `config_merge` | `test_deep_immutability_nested` | routing.py docstring: 'Inputs must remain strictly immutable' | **Yes** | `STATED` | Tune |
| **2006** | `config_merge` | `test_pool_template_immutability` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | `TAUGHT` | Tune |
| **2006** | `config_merge` | `test_env_loader_direct` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | `TAUGHT` | Tune |
| **2007** | `config_merge` | `test_pipeline_nested_immutability` | pipeline.py docstring: 'Inputs must remain immutable and nested options must be defensively copied' | **Yes** | `STATED` | Held-Out |
| **2007** | `config_merge` | `test_step_builder_direct` | step_builder.py module contract | **Yes** | `STATED` | Held-Out |
| **2008** | `config_merge` | `test_in_place_nested_mutation_contract` | session.py docstring: 'MUST mutate accumulator in-place ... Do NOT create deep copies' | **Yes** | `DISTRACTOR` | Held-Out |
| **2009** | `calendar_recurrence` | `test_end_exclusive` | intervals.py docstring: 'half-open interval [start, end), where start is inclusive and end is exclusive' | **Yes** | `STATED` | Tune |
| **2009** | `calendar_recurrence` | `test_subsecond_boundary` | intervals.py docstring: 'half-open interval [start, end)' | **Yes** | `STATED` | Tune |
| **2010** | `calendar_recurrence` | `test_boundary_taught_half_open` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | `TAUGHT` | Tune |
| **2010** | `calendar_recurrence` | `test_period_calc_direct` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | `TAUGHT` | Tune |
| **2011** | `calendar_recurrence` | `test_true_overlap` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | `STATED` | Held-Out |
| **2011** | `calendar_recurrence` | `test_nested_slot` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | `STATED` | Held-Out |
| **2012** | `calendar_recurrence` | `test_retention_half_open` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | `TAUGHT` | Held-Out |
| **2012** | `calendar_recurrence` | `test_window_evaluator_direct` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | `TAUGHT` | Held-Out |
| **2013** | `csv_roundtrip` | `test_rfc4180_quote_doubling` | csv_writer.py docstring: 'wrap in double quotes and escape internal quotes by doubling ("")' | **Yes** | `STATED` | Tune |
| **2013** | `csv_roundtrip` | `test_multiline_csv` | csv_writer.py docstring: 'If field contains comma, newline, or double quote' | **Yes** | `STATED` | Tune |
| **2014** | `csv_roundtrip` | `test_rfc4180_embedded_quotes_taught` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | `TAUGHT` | Tune |
| **2014** | `csv_roundtrip` | `test_comma_enclosure` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | `TAUGHT` | Tune |
| **2015** | `csv_roundtrip` | `test_rfc4180_metric_quotes` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | `TAUGHT` | Held-Out |
| **2015** | `csv_roundtrip` | `test_sanitizer_direct` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | `TAUGHT` | Held-Out |
| **2016** | `csv_roundtrip` | `test_bash_backslash_quoting_distractor` | tsv_formatter.py docstring: 'fields must be tab-delimited and internal quotes must be backslash-escaped (\") ... Do NOT use RFC 4180' | **Yes** | `DISTRACTOR` | Held-Out |
| **2017** | `permission_prefix` | `test_trailing_slash_normalization` | guard.py docstring: 'Normalizes trailing slashes ... Matches only full path segments' | **Yes** | `STATED` | Tune |
| **2018** | `permission_prefix` | `test_taught_segment_and_slash` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | `TAUGHT` | Tune |
| **2019** | `permission_prefix` | `test_segment_boundary_stated` | asset_service.py docstring: 'matches full directory segment boundaries and normalizes trailing slashes' | **Yes** | `STATED` | Held-Out |
| **2019** | `permission_prefix` | `test_path_normalizer_direct` | path_normalizer.py module contract | **Yes** | `STATED` | Held-Out |
| **2020** | `permission_prefix` | `test_scope_taught_boundaries` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | `TAUGHT` | Held-Out |
| **2020** | `permission_prefix` | `test_prefix_validator_direct` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | `TAUGHT` | Held-Out |
| **2021** | `event_ordering` | `test_deterministic_tiebreaker_stated` | dispatcher.py docstring: 'Sort jobs by descending priority ... job_id in ascending order' | **Yes** | `STATED` | Tune |
| **2022** | `event_ordering` | `test_taught_deterministic_timestamp_tiebreaker` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | `TAUGHT` | Tune |
| **2023** | `event_ordering` | `test_sequence_tiebreaker_stated` | rebalancer.py docstring: 'Sort tasks by weight in descending order ... sequence in ascending order' | **Yes** | `STATED` | Held-Out |
| **2024** | `event_ordering` | `test_stream_ordering_taught` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | `TAUGHT` | Held-Out |
| **2024** | `event_ordering` | `test_sort_helper_direct` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | `TAUGHT` | Held-Out |
| **2025** | `cache_ttl` | `test_injectable_clock_monotonic_taught` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |
| **2026** | `cache_ttl` | `test_session_boundary_taught` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |
| **2026** | `cache_ttl` | `test_session_validator_direct` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |
| **2027** | `cache_ttl` | `test_lease_expiry_taught` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |
| **2027** | `cache_ttl` | `test_clock_source_direct` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |
| **2028** | `cache_ttl` | `test_dns_exact_expiry_taught` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | `TRANSFER` | Held-Out |

---

## 4. Root Cause and Factor $u$ Exploration Analysis (S-6 Requirement)

In Section 8 Addendum v2, **Factor $u$** is formally defined as **'repository exploration + test running'**.

### Baseline Context Package (B0 Contract)
Every baseline attempt ($u=0$) receives strictly:
1. Ticket text (symptom report).
2. Failing traceback excerpt.
3. **ONLY the file(s) named in the traceback (`traceback_files`), not the entire repository.**
4. Standard output envelope.

### Root Cause Isolation Audit
For the **12 Hidden Root Cause tasks** (`2001`, `2003`, `2006`, `2007`, `2010`, `2012`, `2015`, `2019`, `2020`, `2024`, `2026`, `2027`), the defective logic is housed in a separate helper module (`tax_engine.py`, `env_loader.py`, `period_calc.py`, `sanitizer.py`, `prefix_validator.py`, `sort_helper.py`, `session_validator.py`, `clock_source.py`) that is NOT present in `traceback_files`.

- **Symptom-Level Fix Analysis:** A patch applied strictly to the caller file named in the traceback cannot satisfy hidden test assertions that test the helper module directly or across other uninvoked callers.
- **Tagging:** All 12 tasks are tagged `root_cause_only_with_exploration = True`.
- **Factor $u$ Separation:** Factor $u$ (tools: `read_file`, `grep`, `run_tests`) is required for the agent to proactively explore the repository, discover the coupled helper module, and verify the fix prior to patch submission.

---

## 5. Verification Checklist & Invariants

1. **Zero Synthetic Shortcuts:** All tasks are evaluated via live pytest execution.
2. **Zero Hint Comments:** Verified via `test_no_hint_comments_in_provided_files` in `tests/test_suite_e5_preflight.py`.
3. **Token Balance:** Handbook (761 tokens) vs Placebo (754 tokens) balanced to within **0.920%** ($\le 3.0\%$).
4. **Hermetic Pre-flight:** 100% gold pass, 0% unpatched pass, 0% mutant passes.