# Benchmark Validation & Fairness Audit (`FAIRNESS_e5.md`)

This document establishes the construct-validity, task fairness, reachability, and per-assertion audit for **Suite E5** (28 instances across 7 bug families), complying with Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md` and Round 10 review requirements.

---

## 1. Executive Summary & Structural Invariants

| Invariant Dimension | Requirement | Measured / Audited Value | Status |
|:---|:---|:---|:---:|
| **Total Instances** | $\ge 24$ instances | **28 instances** across 7 bug families (4 per family) | **PASS** |
| **Class: STATED** | Standard instructions | **10 instances** (35.7%) | **PASS** |
| **Class: TAUGHT** | $\ge 8$ instances | **11 instances** (39.3%) | **PASS** |
| **Class: DISTRACTOR** | $\ge 2$ instances | **3 instances** (10.7%, Tasks 2004, 2008 in Tune; 2016 in Held-Out) | **PASS** |
| **Class: TRANSFER** | $\ge 3$ instances | **4 instances** (14.3%, Tasks 2025–2028 in `cache_ttl`, deliberate family-held-out) | **PASS** |
| **Hidden Root Cause (HRC)** | $\ge 33.3\%$ | **12 / 28 (42.9%)** outside traceback file | **PASS** |
| **Visible Test Sensitive (VTS)** | $\ge 33.3\%$ | **12 / 28 (42.9%)** naive fix fails visible test | **PASS** |
| **Root Cause Reachability** | HRC root cause imported by traceback file | **12 / 12 (100%)** importable from traceback path | **PASS** |
| **Decoy Files** | 0 unimported filler files | **0 decoys** across all 28 repositories (100% on reachability path) | **PASS** |
| **Neutral Test IDs** | 0 design words in test IDs/tracebacks | **0 occurrences** of taught/stated/distractor/transfer/sensitive/hidden | **PASS** |
| **Traceback Purity** | Symptoms only; zero rule giveaways | **100% symptom-only** pytest assertions (`assert actual == expected`) | **PASS** |
| **Tune / Held-Out Split** | ~2/3 Tune, ~1/3 Held-out | **18 Tune (64.3%)** / **10 Held-Out (35.7%)** | **PASS** |

---

## 2. Pre-Registered Tune / Held-Out Partition (B3 Resolution)

- **Screening Experiment Split (Tuning Set, 18 instances = 64.3%):**
  `[2001, 2002, 2004, 2005, 2006, 2008, 2009, 2010, 2012, 2013, 2014, 2015, 2017, 2018, 2020, 2021, 2022, 2024]`
  - Composition: 6 STATED, 10 TAUGHT, 2 DISTRACTOR (Tasks 2004, 2008).
  - Power: 18 tasks $\times$ 16 cells $\times$ 5 runs = 1,440 attempts in screening factorial.
  - Stratification: Exactly 3 instances from each of Families 1–6.
- **Confirmatory Study Split (Held-Out Set, 10 instances = 35.7%):**
  `[2003, 2007, 2011, 2016, 2019, 2023, 2025, 2026, 2027, 2028]`
  - Composition: 4 STATED, 1 TAUGHT, 1 DISTRACTOR (Task 2016) + **all 4 TRANSFER instances** from Family 7 (`cache_ttl`).
  - Stratification: Exactly 1 instance from each of Families 1–6 PLUS all 4 instances of the held-out transfer family.
  - **Deliberate Transfer Design:** TRANSFER is intentionally structured as a domain-held-out transfer family (Family 7: `cache_ttl`), evaluating whether procedural heuristics transfer across domain boundaries without negative interference.

---

## 3. Comprehensive Per-Assertion Fairness Table (S-4 & B1/B2/B4 Resolution)

| Task ID | Bug Family | Test Assertion | Visible Source | Derivable Without Handbook? | Baseline Pass Rate (Measured) | Class Tag | Reachability Path | Decoys | Split |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---|:---:|:---:|
| **2001** | `money_rounding` | `test_vat_rate_calculation` | pricing.py docstring: 'Tax calculation must use banker's rounding (round half to even)' | **Yes** | *Pending Pilot Calibration* | `STATED` | `models.py, tax_engine.py, pricing.py` | **None (0)** | Tune |
| **2001** | `money_rounding` | `test_tax_engine_contract` | tax_engine.py module contract | **Yes** | *Pending Pilot Calibration* | `STATED` | `models.py, tax_engine.py, pricing.py` | **None (0)** | Tune |
| **2002** | `money_rounding` | `test_fractional_split` | HANDBOOK.md Rule H02: Banker's rounding on half-cent boundaries | **No** | *Pending Pilot Calibration* | `TAUGHT` | `models.py, utils.py, discount.py` | **None (0)** | Tune |
| **2002** | `money_rounding` | `test_multi_line_allocation` | HANDBOOK.md Rule H02: Banker's rounding on half-cent boundaries | **No** | *Pending Pilot Calibration* | `TAUGHT` | `models.py, utils.py, discount.py` | **None (0)** | Tune |
| **2003** | `money_rounding` | `test_fx_conversion` | HANDBOOK.md Rule H02: Banker's rounding on half-cents | **No** | *Pending Pilot Calibration* | `TAUGHT` | `rates.py, fx_engine.py, converter.py` | **None (0)** | Held-Out |
| **2003** | `money_rounding` | `test_fx_engine_contract` | HANDBOOK.md Rule H02: Banker's rounding on half-cents | **No** | *Pending Pilot Calibration* | `TAUGHT` | `rates.py, fx_engine.py, converter.py` | **None (0)** | Held-Out |
| **2004** | `money_rounding` | `test_payroll_deduction_rate` | payroll.py docstring: 'MUST round fractional cents UP (ceiling)' | **Yes** | *Pending Pilot Calibration* | `DISTRACTOR` | `models.py, validator.py, payroll.py` | **None (0)** | Tune |
| **2005** | `config_merge` | `test_config_isolation` | routing.py docstring: 'Inputs must remain strictly immutable' | **Yes** | *Pending Pilot Calibration* | `STATED` | `models.py, schema.py, routing.py` | **None (0)** | Tune |
| **2006** | `config_merge` | `test_pool_defaults_isolation` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | *Pending Pilot Calibration* | `TAUGHT` | `options.py, pool.py, env_loader.py` | **None (0)** | Tune |
| **2006** | `config_merge` | `test_env_loader_contract` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | *Pending Pilot Calibration* | `TAUGHT` | `options.py, pool.py, env_loader.py` | **None (0)** | Tune |
| **2007** | `config_merge` | `test_pipeline_defaults_isolation` | pipeline.py docstring: 'Inputs must remain immutable and nested options must be defensively copied' | **Yes** | *Pending Pilot Calibration* | `STATED` | `defaults.py, step_builder.py, pipeline.py` | **None (0)** | Held-Out |
| **2007** | `config_merge` | `test_step_builder_contract` | step_builder.py module contract | **Yes** | *Pending Pilot Calibration* | `STATED` | `defaults.py, step_builder.py, pipeline.py` | **None (0)** | Held-Out |
| **2008** | `config_merge` | `test_nested_accumulator_identity` | session.py docstring: 'MUST mutate accumulator in-place ... Do NOT create deep copies' | **Yes** | *Pending Pilot Calibration* | `DISTRACTOR` | `state.py, metrics.py, session.py` | **None (0)** | Tune |
| **2009** | `calendar_recurrence` | `test_interval_end_boundary` | intervals.py docstring: 'half-open interval [start, end), where start is inclusive and end is exclusive' | **Yes** | *Pending Pilot Calibration* | `STATED` | `calendar_models.py, formatters.py, intervals.py` | **None (0)** | Tune |
| **2009** | `calendar_recurrence` | `test_interval_subsecond_boundary` | intervals.py docstring: 'half-open interval [start, end)' | **Yes** | *Pending Pilot Calibration* | `STATED` | `calendar_models.py, formatters.py, intervals.py` | **None (0)** | Tune |
| **2010** | `calendar_recurrence` | `test_window_expiration` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | *Pending Pilot Calibration* | `TAUGHT` | `rules.py, subscription.py, period_calc.py` | **None (0)** | Tune |
| **2010** | `calendar_recurrence` | `test_period_calc_contract` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | *Pending Pilot Calibration* | `TAUGHT` | `rules.py, subscription.py, period_calc.py` | **None (0)** | Tune |
| **2011** | `calendar_recurrence` | `test_touching_slot_boundaries` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | *Pending Pilot Calibration* | `STATED` | `slots.py, audit.py, maintenance.py` | **None (0)** | Held-Out |
| **2011** | `calendar_recurrence` | `test_nested_slot` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | *Pending Pilot Calibration* | `STATED` | `slots.py, audit.py, maintenance.py` | **None (0)** | Held-Out |
| **2012** | `calendar_recurrence` | `test_retention_window_cutoff` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | *Pending Pilot Calibration* | `TAUGHT` | `log_store.py, window_evaluator.py, retention.py` | **None (0)** | Tune |
| **2012** | `calendar_recurrence` | `test_window_evaluator_contract` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | *Pending Pilot Calibration* | `TAUGHT` | `log_store.py, window_evaluator.py, retention.py` | **None (0)** | Tune |
| **2013** | `csv_roundtrip` | `test_quote_escaping` | csv_writer.py docstring: 'wrap in double quotes and escape internal quotes by doubling ("")' | **Yes** | *Pending Pilot Calibration* | `STATED` | `schema.py, io_helpers.py, csv_writer.py` | **None (0)** | Tune |
| **2013** | `csv_roundtrip` | `test_multiline_csv` | csv_writer.py docstring: 'If field contains comma, newline, or double quote' | **Yes** | *Pending Pilot Calibration* | `STATED` | `schema.py, io_helpers.py, csv_writer.py` | **None (0)** | Tune |
| **2014** | `csv_roundtrip` | `test_item_quote_escaping` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `item.py, catalog_validator.py, serializer.py` | **None (0)** | Tune |
| **2014** | `csv_roundtrip` | `test_comma_enclosure` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `item.py, catalog_validator.py, serializer.py` | **None (0)** | Tune |
| **2015** | `csv_roundtrip` | `test_metric_quote_escaping` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `metric.py, sanitizer.py, exporter.py` | **None (0)** | Tune |
| **2015** | `csv_roundtrip` | `test_sanitizer_contract` | HANDBOOK.md Rule H10: RFC 4180 CSV serialization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `metric.py, sanitizer.py, exporter.py` | **None (0)** | Tune |
| **2016** | `csv_roundtrip` | `test_quote_formatting` | tsv_formatter.py docstring: 'fields must be tab-delimited and internal quotes must be backslash-escaped (\") ... Do NOT use RFC 4180' | **Yes** | *Pending Pilot Calibration* | `DISTRACTOR` | `cmd_models.py, cmd_log.py, tsv_formatter.py` | **None (0)** | Held-Out |
| **2017** | `permission_prefix` | `test_trailing_slash_normalization` | guard.py docstring: 'Normalizes trailing slashes ... Matches only full path segments' | **Yes** | *Pending Pilot Calibration* | `STATED` | `policy.py, url_normalizer.py, guard.py` | **None (0)** | Tune |
| **2018** | `permission_prefix` | `test_path_normalization` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `path_resolver.py, audit_logger.py, rbac.py` | **None (0)** | Tune |
| **2019** | `permission_prefix` | `test_resource_isolation` | asset_service.py docstring: 'matches full directory segment boundaries and normalizes trailing slashes' | **Yes** | *Pending Pilot Calibration* | `STATED` | `models.py, path_normalizer.py, asset_service.py` | **None (0)** | Held-Out |
| **2019** | `permission_prefix` | `test_path_normalizer_contract` | path_normalizer.py module contract | **Yes** | *Pending Pilot Calibration* | `STATED` | `models.py, path_normalizer.py, asset_service.py` | **None (0)** | Held-Out |
| **2020** | `permission_prefix` | `test_channel_routing` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `webhook.py, prefix_validator.py, scope_checker.py` | **None (0)** | Tune |
| **2020** | `permission_prefix` | `test_prefix_validator_contract` | HANDBOOK.md Rule H06: Trailing slash and path prefix normalization | **No** | *Pending Pilot Calibration* | `TAUGHT` | `webhook.py, prefix_validator.py, scope_checker.py` | **None (0)** | Tune |
| **2021** | `event_ordering` | `test_equal_priority_tiebreak` | dispatcher.py docstring: 'Sort jobs by descending priority ... job_id in ascending order' | **Yes** | *Pending Pilot Calibration* | `STATED` | `job.py, queue_metrics.py, dispatcher.py` | **None (0)** | Tune |
| **2022** | `event_ordering` | `test_timestamp_order` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | *Pending Pilot Calibration* | `TAUGHT` | `notification.py, formatter.py, sorter.py` | **None (0)** | Tune |
| **2023** | `event_ordering` | `test_sequence_ordering` | rebalancer.py docstring: 'Sort tasks by weight in descending order ... sequence in ascending order' | **Yes** | *Pending Pilot Calibration* | `STATED` | `task_item.py, metrics.py, rebalancer.py` | **None (0)** | Held-Out |
| **2024** | `event_ordering` | `test_stream_sequencing` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | *Pending Pilot Calibration* | `TAUGHT` | `event_packet.py, sort_helper.py, sequencer.py` | **None (0)** | Tune |
| **2024** | `event_ordering` | `test_sort_helper_contract` | HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker | **No** | *Pending Pilot Calibration* | `TAUGHT` | `event_packet.py, sort_helper.py, sequencer.py` | **None (0)** | Tune |
| **2025** | `cache_ttl` | `test_token_expiry` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `token_record.py, cache_utils.py, cache.py` | **None (0)** | Held-Out |
| **2026** | `cache_ttl` | `test_session_expiry` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `session_data.py, session_validator.py, session_store.py` | **None (0)** | Held-Out |
| **2026** | `cache_ttl` | `test_session_validator_contract` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `session_data.py, session_validator.py, session_store.py` | **None (0)** | Held-Out |
| **2027** | `cache_ttl` | `test_lease_validity_boundary` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `lease_entry.py, clock_source.py, lease_guard.py` | **None (0)** | Held-Out |
| **2027** | `cache_ttl` | `test_clock_source_contract` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `lease_entry.py, clock_source.py, lease_guard.py` | **None (0)** | Held-Out |
| **2028** | `cache_ttl` | `test_dns_ttl_boundary` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | *Pending Pilot Calibration* | `TRANSFER` | `dns_record.py, dns_utils.py, dns_resolver.py` | **None (0)** | Held-Out |

---

## 4. Reachability and Zero-Decoy Architecture (B4 Resolution)

To prevent noise that artificially advantages tool-using conditions ($u=1$), every repository has been audited for reachability:
1. **Zero Decoy Modules:** Every file in every task repository is an active, imported module executed on the normal program path (e.g. input validation, data model definitions, error handling, format helpers). Decoys = 0 across all classes.
2. **HRC Reachability:** For all 12 Hidden Root Cause tasks, the root-cause file is imported directly by the traceback file, verified by automated preflight test `test_root_cause_reachability`.

---

## 5. Verification Checklist & Invariants

1. **Zero Synthetic Shortcuts:** All tasks evaluate via real pytest subprocess execution.
2. **Zero Hint Comments:** Guarded by `test_no_hint_comments_in_provided_files`.
3. **Zero Design Word Leaks:** Guarded by `test_no_design_words_in_tests_or_traces` (B1/B2).
4. **Token Balance:** Handbook (761 tokens) vs Placebo (754 tokens) balanced to within **0.920%** ($\le 3.0\%$).
5. **Hermetic Pre-flight:** 100% gold pass, 0% unpatched pass, 0% mutant passes across all 28 tasks.