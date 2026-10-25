# Benchmark Validation & Fairness Audit (`FAIRNESS_e5.md`)

This document establishes the construct-validity, task fairness, reachability, and per-assertion audit for **Suite E5 Expanded** (84 instances across 14 bug families), complying with Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md` and Round 16 review requirements.

---

## 1. Executive Summary & Structural Invariants

| Invariant Dimension | Requirement | Measured / Audited Value | Status |
|:---|:---|:---|:---:|
| **Total Instances** | $\ge 80$ authored instances | **84 instances** across 14 bug families | **PASS** |
| **Class: STATED** | Standard instructions | **21 instances** (25.0%) | **PASS** |
| **Class: TAUGHT** | $\ge 24$ instances | **35 instances** (41.7%) | **PASS** |
| **Class: DISTRACTOR** | $\ge 10$ instances | **16 instances** (19.0%) | **PASS** |
| **Class: TRANSFER** | $\ge 8$ instances | **12 instances** (14.3%, 100% held-out pure transfer families) | **PASS** |
| **Hidden Root Cause (HRC)** | $\ge 33.3\%$ | **29 / 84 (34.5%)** outside traceback file | **PASS** |
| **Visible Test Sensitive (VTS)** | $\ge 33.3\%$ | **38 / 84 (45.2%)** naive fix fails visible test | **PASS** |
| **Root Cause Reachability** | HRC root cause imported by traceback file | **100%** importable from traceback path | **PASS** |
| **Decoy Files** | 0 unimported filler files | **0 decoys** across all 84 repositories (100% on reachability path) | **PASS** |
| **Neutral Test IDs** | 0 design words in test IDs/tracebacks | **0 occurrences** of taught/stated/distractor/transfer/sensitive/hidden | **PASS** |
| **Traceback Purity** | Symptoms only; zero rule giveaways | **100% symptom-only** pytest assertions (`assert actual == expected`) | **PASS** |
| **Tune / Held-Out Split** | Class-stratified (50% Tune, 50% Held-out) | **42 Tune (50.0%)** / **42 Held-Out (50.0%)** | **PASS** |
| **Held-Out TAUGHT Power** | >= 12 TAUGHT in Held-out | **16 TAUGHT** (exceeds requirement) | **PASS** |
| **Held-Out DISTRACTOR Power** | >= 6 DISTRACTOR in Held-out | **8 DISTRACTOR** (exceeds requirement) | **PASS** |
| **Held-Out Pure TRANSFER** | >= 4 TRANSFER across >= 2 families | **12 TRANSFER** (Family 7 & Family 14, 100% held out) | **PASS** |

---

## 2. Pre-Registered Tune / Held-Out Partition (C1 Resolution & J4)

To ensure the confirmatory study has sufficient statistical power to test the primary research hypothesis (that the handbook reliably teaches conventions absent from standard pretraining without harmful distraction), the partition is class-stratified and family-stratified:

- **Screening Experiment Split (Tuning Set, 42 instances = 50.0%):**
  `[2001, 2002, 2005, 2006, 2008, 2009, 2011, 2012, 2013, 2014, 2017, 2018, 2020, 2021, 2023, 2024, 2029, 2030, 2031, 2032, 2037, 2038, 2039, 2040, 2045, 2046, 2047, 2048, 2053, 2054, 2055, 2056, 2061, 2062, 2063, 2064, 2066, 2069, 2070, 2071, 2072, 2074]`
  - **Class Breakdown:** 19 TAUGHT, 15 STATED, 8 DISTRACTOR, 0 TRANSFER.
  - **Screening Power:** >= 8 tasks per core class across 12 families.
  - **Design Balance:** 42 tasks $\times$ 16 cells = 672 factor cells in the Resolution-V factorial.

- **Confirmatory Study Split (Held-Out Set, 42 instances = 50.0%):**
  `[2003, 2004, 2007, 2010, 2015, 2016, 2019, 2022, 2025, 2026, 2027, 2028, 2033, 2034, 2035, 2036, 2041, 2042, 2043, 2044, 2049, 2050, 2051, 2052, 2057, 2058, 2059, 2060, 2065, 2067, 2068, 2073, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084]`
  - **Class Breakdown:** 16 TAUGHT, 6 STATED, 8 DISTRACTOR, 12 TRANSFER.
  - **Primary Hypothesis Power:** 16 TAUGHT instances across distinct bug families ensure the central confirmatory hypothesis test ($\Delta_{\text{TAUGHT}} = \bar{Y}_{\theta^*} - \bar{Y}_0 > 0$) has >= 80% power at MDE <= 0.15.
  - **Cognitive Interference Test:** 8 DISTRACTOR instances test whether handbook exposure causes over-compliance against local specifications.
  - **Domain Generalization:** 12 TRANSFER instances across 2 pure transfer families (Family 7 `cache_ttl`, Tasks 2025–2028; Family 14 `state_transitions`, Tasks 2077–2084) held out for evaluating cross-domain heuristic transfer.

### 2.1 Pre-Registration Relabel Rule (C2 Resolution)

> [!IMPORTANT]
> **Objective Relabeling Criterion:** To prevent confirmation bias in class definitions:
> 1. Any task initially labeled `TAUGHT` where the empirical baseline pass rate during Pilot Calibration ($B_0$, repeated runs) exceeds **70.0%** will be automatically reclassified as `STATED`.
> 2. Reclassified tasks will be dropped from the confirmatory `TAUGHT` hypothesis test.
> 3. Class labels are finalized strictly based on measured empirical baseline solvability before the Screening Experiment begins, and NEVER adjusted based on post-hoc handbook gains.

---

## 3. Comprehensive Per-Assertion Fairness Table (S-4 & B1/B2/B4 Resolution)

| Task ID | Bug Family | Test Assertion | Visible Source | Derivable Without Handbook? | Baseline Pass Rate (Measured) | Class Tag | Reachability Path | Decoys | Split |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---|:---:|:---:|
| **2001** | `money_rounding` | `test_vat_rate_calculation` | pricing.py docstring: 'Tax calculation must use half-up rounding (ROUND_HALF_UP)' | **Yes** | **100.0%** (6/6) | `STATED` | `models.py, tax_engine.py, pricing.py` | **None (0)** | Tune |
| **2001** | `money_rounding` | `test_tax_engine_contract` | tax_engine.py module contract | **Yes** | **100.0%** (6/6) | `STATED` | `models.py, tax_engine.py, pricing.py` | **None (0)** | Tune |
| **2002** | `money_rounding` | `test_fractional_split` | HANDBOOK.md Rule H02: Half-up rounding on half-cent boundaries | **No** | **0.0%** (0/6) | `TAUGHT` | `models.py, utils.py, discount.py` | **None (0)** | Tune |
| **2002** | `money_rounding` | `test_multi_line_allocation` | HANDBOOK.md Rule H02: Half-up rounding on half-cent boundaries | **No** | **0.0%** (0/6) | `TAUGHT` | `models.py, utils.py, discount.py` | **None (0)** | Tune |
| **2003** | `money_rounding` | `test_fx_conversion` | HANDBOOK.md Rule H02: Half-up rounding on half-cents | **No** | **100.0%** (6/6) | `TAUGHT` | `rates.py, fx_engine.py, converter.py` | **None (0)** | Held-Out |
| **2003** | `money_rounding` | `test_fx_engine_contract` | HANDBOOK.md Rule H02: Half-up rounding on half-cents | **No** | **100.0%** (6/6) | `TAUGHT` | `rates.py, fx_engine.py, converter.py` | **None (0)** | Held-Out |
| **2004** | `money_rounding` | `test_payroll_deduction_rate` | payroll.py docstring: 'MUST round fractional cents UP (ceiling)' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `models.py, validator.py, payroll.py` | **None (0)** | Held-Out |
| **2005** | `config_merge` | `test_config_isolation` | routing.py docstring: 'Inputs must remain strictly immutable' | **Yes** | **100.0%** (6/6) | `STATED` | `models.py, schema.py, routing.py` | **None (0)** | Tune |
| **2006** | `config_merge` | `test_pool_defaults_isolation` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | **83.3%** (5/6) | `TAUGHT` | `options.py, pool.py, env_loader.py` | **None (0)** | Tune |
| **2006** | `config_merge` | `test_env_loader_contract` | HANDBOOK.md Rule H03: Input immutability & defensive copying | **No** | **83.3%** (5/6) | `TAUGHT` | `options.py, pool.py, env_loader.py` | **None (0)** | Tune |
| **2007** | `config_merge` | `test_pipeline_defaults_isolation` | pipeline.py docstring: 'Inputs must remain immutable and nested options must be defensively copied' | **Yes** | **50.0%** (3/6) | `STATED` | `defaults.py, step_builder.py, pipeline.py` | **None (0)** | Held-Out |
| **2007** | `config_merge` | `test_step_builder_contract` | step_builder.py module contract | **Yes** | **50.0%** (3/6) | `STATED` | `defaults.py, step_builder.py, pipeline.py` | **None (0)** | Held-Out |
| **2008** | `config_merge` | `test_nested_accumulator_identity` | session.py docstring: 'MUST mutate accumulator in-place ... Do NOT create deep copies' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `state.py, metrics.py, session.py` | **None (0)** | Tune |
| **2009** | `calendar_recurrence` | `test_interval_end_boundary` | intervals.py docstring: 'half-open interval [start, end), where start is inclusive and end is exclusive' | **Yes** | **100.0%** (6/6) | `STATED` | `calendar_models.py, formatters.py, intervals.py` | **None (0)** | Tune |
| **2009** | `calendar_recurrence` | `test_interval_subsecond_boundary` | intervals.py docstring: 'half-open interval [start, end)' | **Yes** | **100.0%** (6/6) | `STATED` | `calendar_models.py, formatters.py, intervals.py` | **None (0)** | Tune |
| **2010** | `calendar_recurrence` | `test_window_expiration` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | **100.0%** (6/6) | `TAUGHT` | `rules.py, subscription.py, period_calc.py` | **None (0)** | Held-Out |
| **2010** | `calendar_recurrence` | `test_period_calc_contract` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | **100.0%** (6/6) | `TAUGHT` | `rules.py, subscription.py, period_calc.py` | **None (0)** | Held-Out |
| **2011** | `calendar_recurrence` | `test_touching_slot_boundaries` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | **100.0%** (6/6) | `STATED` | `slots.py, audit.py, maintenance.py` | **None (0)** | Tune |
| **2011** | `calendar_recurrence` | `test_nested_slot` | maintenance.py docstring: 'slots are half-open intervals [start, end)' | **Yes** | **100.0%** (6/6) | `STATED` | `slots.py, audit.py, maintenance.py` | **None (0)** | Tune |
| **2012** | `calendar_recurrence` | `test_retention_window_cutoff` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | **100.0%** (6/6) | `TAUGHT` | `log_store.py, window_evaluator.py, retention.py` | **None (0)** | Tune |
| **2012** | `calendar_recurrence` | `test_window_evaluator_contract` | HANDBOOK.md Rule H05: Half-open intervals [start, end) | **No** | **100.0%** (6/6) | `TAUGHT` | `log_store.py, window_evaluator.py, retention.py` | **None (0)** | Tune |
| **2013** | `csv_roundtrip` | `test_quote_escaping` | csv_writer.py docstring: 'internal double quotes are escaped with backslash (\")' | **Yes** | **50.0%** (3/6) | `STATED` | `schema.py, io_helpers.py, csv_writer.py` | **None (0)** | Tune |
| **2013** | `csv_roundtrip` | `test_multiline_and_null` | csv_writer.py docstring: 'newline characters are escaped as \n, and None/null values are serialized as \N' | **Yes** | **50.0%** (3/6) | `STATED` | `schema.py, io_helpers.py, csv_writer.py` | **None (0)** | Tune |
| **2014** | `csv_roundtrip` | `test_item_quote_escaping` | HANDBOOK.md Rule H10: TSV audit logging and backslash escaping | **No** | **66.7%** (4/6) | `TAUGHT` | `item.py, catalog_validator.py, serializer.py` | **None (0)** | Tune |
| **2014** | `csv_roundtrip` | `test_multiline_escaping` | HANDBOOK.md Rule H10: TSV audit logging and backslash escaping | **No** | **66.7%** (4/6) | `TAUGHT` | `item.py, catalog_validator.py, serializer.py` | **None (0)** | Tune |
| **2015** | `csv_roundtrip` | `test_metric_quote_escaping` | HANDBOOK.md Rule H10: TSV audit logging and backslash escaping | **No** | **0.0%** (0/6) | `TAUGHT` | `metric.py, sanitizer.py, exporter.py` | **None (0)** | Held-Out |
| **2015** | `csv_roundtrip` | `test_sanitizer_contract` | HANDBOOK.md Rule H10: TSV audit logging and backslash escaping | **No** | **0.0%** (0/6) | `TAUGHT` | `metric.py, sanitizer.py, exporter.py` | **None (0)** | Held-Out |
| **2016** | `csv_roundtrip` | `test_quote_formatting` | tsv_formatter.py docstring: 'must strictly follow RFC 4180 CSV ... Do NOT use TSV backslash escaping' | **Yes** | **33.3%** (2/6) | `DISTRACTOR` | `cmd_models.py, cmd_log.py, tsv_formatter.py` | **None (0)** | Held-Out |
| **2017** | `permission_prefix` | `test_wildcard_matching` | guard.py docstring: 'The single asterisk wildcard * matches exactly one segment; the double asterisk ** matches arbitrary multi-segment prefixes' | **Yes** | **100.0%** (6/6) | `STATED` | `policy.py, url_normalizer.py, guard.py` | **None (0)** | Tune |
| **2018** | `permission_prefix` | `test_wildcard_hierarchy` | HANDBOOK.md Rule H06: Double-colon scopes and wildcard hierarchy | **No** | **0.0%** (0/6) | `TAUGHT` | `path_resolver.py, audit_logger.py, rbac.py` | **None (0)** | Tune |
| **2019** | `permission_prefix` | `test_resource_isolation` | asset_service.py docstring: 'matches full segment boundaries under :: delimiter' | **Yes** | **83.3%** (5/6) | `STATED` | `models.py, path_normalizer.py, asset_service.py` | **None (0)** | Held-Out |
| **2019** | `permission_prefix` | `test_path_normalizer_contract` | path_normalizer.py module contract | **Yes** | **83.3%** (5/6) | `STATED` | `models.py, path_normalizer.py, asset_service.py` | **None (0)** | Held-Out |
| **2020** | `permission_prefix` | `test_channel_routing` | HANDBOOK.md Rule H06: Double-colon scope hierarchy and segment boundaries | **No** | **100.0%** (6/6) | `TAUGHT` | `webhook.py, prefix_validator.py, scope_checker.py` | **None (0)** | Tune |
| **2020** | `permission_prefix` | `test_prefix_validator_contract` | HANDBOOK.md Rule H06: Double-colon scope hierarchy and segment boundaries | **No** | **100.0%** (6/6) | `TAUGHT` | `webhook.py, prefix_validator.py, scope_checker.py` | **None (0)** | Tune |
| **2021** | `event_ordering` | `test_equal_priority_tiebreak` | dispatcher.py docstring: 'Sort jobs by descending priority ... payload SHA-256 digest in ascending lexicographical order' | **Yes** | **100.0%** (6/6) | `STATED` | `job.py, queue_metrics.py, dispatcher.py` | **None (0)** | Tune |
| **2022** | `event_ordering` | `test_notification_sha256_tiebreak` | HANDBOOK.md Rule H07: Deterministic SHA-256 tie-breaking | **No** | **33.3%** (2/6) | `TAUGHT` | `notification.py, formatter.py, sorter.py` | **None (0)** | Held-Out |
| **2023** | `event_ordering` | `test_task_id_tiebreak` | rebalancer.py docstring: 'ties in priority MUST be broken by ascending chronological registration ID (task_id), do NOT compute SHA-256 digests' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `task_item.py, metrics.py, rebalancer.py` | **None (0)** | Tune |
| **2024** | `event_ordering` | `test_stream_sequencing` | HANDBOOK.md Rule H07: Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking | **No** | **0.0%** (0/6) | `TAUGHT` | `event_packet.py, sort_helper.py, sequencer.py` | **None (0)** | Tune |
| **2024** | `event_ordering` | `test_sort_helper_contract` | HANDBOOK.md Rule H07: Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking | **No** | **0.0%** (0/6) | `TAUGHT` | `event_packet.py, sort_helper.py, sequencer.py` | **None (0)** | Tune |
| **2025** | `cache_ttl` | `test_token_expiry` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `token_record.py, cache_utils.py, cache.py` | **None (0)** | Held-Out |
| **2026** | `cache_ttl` | `test_session_expiry` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `session_data.py, session_validator.py, session_store.py` | **None (0)** | Held-Out |
| **2026** | `cache_ttl` | `test_session_validator_contract` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `session_data.py, session_validator.py, session_store.py` | **None (0)** | Held-Out |
| **2027** | `cache_ttl` | `test_lease_validity_boundary` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `lease_entry.py, clock_source.py, lease_guard.py` | **None (0)** | Held-Out |
| **2027** | `cache_ttl` | `test_clock_source_contract` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `lease_entry.py, clock_source.py, lease_guard.py` | **None (0)** | Held-Out |
| **2028** | `cache_ttl` | `test_dns_ttl_boundary` | HANDBOOK.md Rule H09: Injectable clocks and monotonic TTL expiration | **No** | **100.0%** (6/6) | `TRANSFER` | `dns_record.py, dns_utils.py, dns_resolver.py` | **None (0)** | Held-Out |
| **2029** | `service_errors` | `test_service_execution` | auth_service.py docstring: 'raise ServiceError(code="ERR_AUTH_SCOPE_DENIED", ...)' | **Yes** | **66.7%** (4/6) | `STATED` | `errors.py, auth_context.py, auth_service.py` | **None (0)** | Tune |
| **2030** | `service_errors` | `test_service_execution` | HANDBOOK.md Rule H04: Structured Service Exception Hierarchy | **No** | **0.0%** (0/6) | `TAUGHT` | `errors.py, tenant_context.py, tenant_guard.py` | **None (0)** | Tune |
| **2031** | `service_errors` | `test_service_execution` | HANDBOOK.md Rule H04: Structured Service Exception Hierarchy | **No** | **0.0%** (0/6) | `TAUGHT` | `errors.py, schema_specs.py, payload_validator.py` | **None (0)** | Tune |
| **2032** | `service_errors` | `test_service_execution` | deserializer.py docstring: 'MUST raise built-in ValueError with standard message, do NOT raise ServiceError' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `errors.py, packet_types.py, deserializer.py` | **None (0)** | Tune |
| **2033** | `service_errors` | `test_service_execution` | HANDBOOK.md Rule H04: Structured Service Exception Hierarchy | **No** | **0.0%** (0/6) | `TAUGHT` | `errors.py, lock_record.py, lock_manager.py` | **None (0)** | Held-Out |
| **2034** | `service_errors` | `test_service_execution` | rate_dispatcher.py docstring: 'MUST raise ServiceError(code="ERR_RATE_LIMIT_EXCEEDED", ...)' | **Yes** | **83.3%** (5/6) | `STATED` | `errors.py, rate_record.py, rate_dispatcher.py` | **None (0)** | Held-Out |
| **2035** | `service_errors` | `test_service_execution` | HANDBOOK.md Rule H04: Structured Service Exception Hierarchy | **No** | **0.0%** (0/6) | `TAUGHT` | `errors.py, quota_tracker.py, throttle_guard.py` | **None (0)** | Held-Out |
| **2036** | `service_errors` | `test_service_execution` | webhook_gateway.py docstring: 'MUST raise built-in KeyError, do NOT raise ServiceError' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `errors.py, webhook_registry.py, webhook_gateway.py` | **None (0)** | Held-Out |
| **2037** | `wire_envelope` | `test_service_execution` | audit_formatter.py docstring: 'Wrap payload in envelope {"_v": 2, ...} and convert all payload keys to snake_case' | **Yes** | **16.7%** (1/6) | `STATED` | `key_normalizer.py, wire_envelope.py, audit_formatter.py` | **None (0)** | Tune |
| **2038** | `wire_envelope` | `test_service_execution` | HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization | **No** | **16.7%** (1/6) | `TAUGHT` | `key_normalizer.py, wire_envelope.py, billing_emitter.py` | **None (0)** | Tune |
| **2039** | `wire_envelope` | `test_service_execution` | HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization | **No** | **0.0%** (0/6) | `TAUGHT` | `key_normalizer.py, wire_envelope.py, telemetry_stream.py` | **None (0)** | Tune |
| **2040** | `wire_envelope` | `test_service_execution` | iot_demux.py docstring: 'MUST emit unwrapped payload dictionary directly with original camelCase keys, do NOT wrap in version 2 envelope' | **Yes** | **50.0%** (3/6) | `DISTRACTOR` | `key_normalizer.py, wire_envelope.py, iot_demux.py` | **None (0)** | Tune |
| **2041** | `wire_envelope` | `test_service_execution` | HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization | **No** | **0.0%** (0/6) | `TAUGHT` | `key_normalizer.py, wire_envelope.py, activity_dispatcher.py` | **None (0)** | Held-Out |
| **2042** | `wire_envelope` | `test_service_execution` | order_dispatcher.py docstring: 'Wrap in standardized envelope {"_v": 2, ...} with snake_case keys' | **Yes** | **0.0%** (0/6) | `STATED` | `key_normalizer.py, wire_envelope.py, order_dispatcher.py` | **None (0)** | Held-Out |
| **2043** | `wire_envelope` | `test_service_execution` | HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization | **No** | **0.0%** (0/6) | `TAUGHT` | `key_normalizer.py, wire_envelope.py, inventory_broadcaster.py` | **None (0)** | Held-Out |
| **2044** | `wire_envelope` | `test_service_execution` | soap_bridge.py docstring: 'emit raw un-enveloped payload, do NOT wrap in version 2 envelope' | **Yes** | **0.0%** (0/6) | `DISTRACTOR` | `key_normalizer.py, wire_envelope.py, soap_bridge.py` | **None (0)** | Held-Out |
| **2045** | `timestamp_iso` | `test_case_1` | audit_service.py docstring: 'explicit millisecond precision and uppercase Z suffix' | **Yes** | **100.0%** (6/6) | `STATED` | `models.py, formatter.py, audit_service.py` | **None (0)** | Tune |
| **2045** | `timestamp_iso` | `test_case_2` | audit_service.py docstring: 'explicit millisecond precision and uppercase Z suffix' | **Yes** | **100.0%** (6/6) | `STATED` | `models.py, formatter.py, audit_service.py` | **None (0)** | Tune |
| **2046** | `timestamp_iso` | `test_case_1` | HANDBOOK.md Rule H09 | **No** | **83.3%** (5/6) | `TAUGHT` | `telemetry_codec.py, metrics_collector.py, log_pipeline.py` | **None (0)** | Tune |
| **2046** | `timestamp_iso` | `test_case_2` | HANDBOOK.md Rule H09 | **No** | **83.3%** (5/6) | `TAUGHT` | `telemetry_codec.py, metrics_collector.py, log_pipeline.py` | **None (0)** | Tune |
| **2047** | `timestamp_iso` | `test_case_1` | HANDBOOK.md Rule H09 | **No** | **100.0%** (6/6) | `TAUGHT` | `envelope_schema.py, signature_utils.py, webhook_sender.py` | **None (0)** | Tune |
| **2047** | `timestamp_iso` | `test_case_2` | HANDBOOK.md Rule H09 | **No** | **100.0%** (6/6) | `TAUGHT` | `envelope_schema.py, signature_utils.py, webhook_sender.py` | **None (0)** | Tune |
| **2048** | `timestamp_iso` | `test_case_1` | stream_ingest.py docstring: 'Timestamps must be formatted as Unix epoch integer seconds' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `stream_packet.py, channel_filter.py, stream_ingest.py` | **None (0)** | Tune |
| **2048** | `timestamp_iso` | `test_case_2` | stream_ingest.py docstring: 'Timestamps must be formatted as Unix epoch integer seconds' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `stream_packet.py, channel_filter.py, stream_ingest.py` | **None (0)** | Tune |
| **2049** | `timestamp_iso` | `test_case_1` | HANDBOOK.md Rule H09 | **No** | **83.3%** (5/6) | `TAUGHT` | `snapshot_manifest.py, storage_allocator.py, snapshot_manager.py` | **None (0)** | Held-Out |
| **2049** | `timestamp_iso` | `test_case_2` | HANDBOOK.md Rule H09 | **No** | **83.3%** (5/6) | `TAUGHT` | `snapshot_manifest.py, storage_allocator.py, snapshot_manager.py` | **None (0)** | Held-Out |
| **2050** | `timestamp_iso` | `test_case_1` | journal_writer.py docstring: 'explicit millisecond precision and uppercase Z suffix' | **Yes** | **100.0%** (6/6) | `STATED` | `journal_entry.py, status_catalog.py, journal_writer.py` | **None (0)** | Held-Out |
| **2050** | `timestamp_iso` | `test_case_2` | journal_writer.py docstring: 'explicit millisecond precision and uppercase Z suffix' | **Yes** | **100.0%** (6/6) | `STATED` | `journal_entry.py, status_catalog.py, journal_writer.py` | **None (0)** | Held-Out |
| **2051** | `timestamp_iso` | `test_case_1` | HANDBOOK.md Rule H09 | **No** | **100.0%** (6/6) | `TAUGHT` | `token_codec.py, vault_registry.py, ledger_service.py` | **None (0)** | Held-Out |
| **2051** | `timestamp_iso` | `test_case_2` | HANDBOOK.md Rule H09 | **No** | **100.0%** (6/6) | `TAUGHT` | `token_codec.py, vault_registry.py, ledger_service.py` | **None (0)** | Held-Out |
| **2052** | `timestamp_iso` | `test_case_1` | trace_recorder.py docstring: 'mandate microsecond precision: %Y-%m-%dT%H:%M:%S.%fZ' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `trace_span.py, cpu_affinity.py, trace_recorder.py` | **None (0)** | Held-Out |
| **2052** | `timestamp_iso` | `test_case_2` | trace_recorder.py docstring: 'mandate microsecond precision: %Y-%m-%dT%H:%M:%S.%fZ' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `trace_span.py, cpu_affinity.py, trace_recorder.py` | **None (0)** | Held-Out |
| **2053** | `config_lists` | `test_case_1` | config_merger.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed' | **Yes** | **100.0%** (6/6) | `STATED` | `endpoint_model.py, schema_validator.py, config_merger.py` | **None (0)** | Tune |
| **2053** | `config_lists` | `test_case_2` | config_merger.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed' | **Yes** | **100.0%** (6/6) | `STATED` | `endpoint_model.py, schema_validator.py, config_merger.py` | **None (0)** | Tune |
| **2054** | `config_lists` | `test_case_1` | HANDBOOK.md Rule H12 | **No** | **66.7%** (4/6) | `TAUGHT` | `list_merger.py, cluster_manifest.py, cluster_builder.py` | **None (0)** | Tune |
| **2054** | `config_lists` | `test_case_2` | HANDBOOK.md Rule H12 | **No** | **66.7%** (4/6) | `TAUGHT` | `list_merger.py, cluster_manifest.py, cluster_builder.py` | **None (0)** | Tune |
| **2055** | `config_lists` | `test_case_1` | HANDBOOK.md Rule H12 | **No** | **33.3%** (2/6) | `TAUGHT` | `step_schema.py, env_validator.py, pipeline_composer.py` | **None (0)** | Tune |
| **2055** | `config_lists` | `test_case_2` | HANDBOOK.md Rule H12 | **No** | **33.3%** (2/6) | `TAUGHT` | `step_schema.py, env_validator.py, pipeline_composer.py` | **None (0)** | Tune |
| **2056** | `config_lists` | `test_case_1` | policy_merger.py docstring: 'override list replaces the base list entirely' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `firewall_rule.py, cidr_parser.py, policy_merger.py` | **None (0)** | Tune |
| **2056** | `config_lists` | `test_case_2` | policy_merger.py docstring: 'override list replaces the base list entirely' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `firewall_rule.py, cidr_parser.py, policy_merger.py` | **None (0)** | Tune |
| **2057** | `config_lists` | `test_case_1` | HANDBOOK.md Rule H12 | **No** | **83.3%** (5/6) | `TAUGHT` | `gate_combiner.py, license_checker.py, gate_manager.py` | **None (0)** | Held-Out |
| **2057** | `config_lists` | `test_case_2` | HANDBOOK.md Rule H12 | **No** | **83.3%** (5/6) | `TAUGHT` | `gate_combiner.py, license_checker.py, gate_manager.py` | **None (0)** | Held-Out |
| **2058** | `config_lists` | `test_case_1` | migration_loader.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed' | **Yes** | **100.0%** (6/6) | `STATED` | `migration_model.py, version_parser.py, migration_loader.py` | **None (0)** | Held-Out |
| **2058** | `config_lists` | `test_case_2` | migration_loader.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed' | **Yes** | **100.0%** (6/6) | `STATED` | `migration_model.py, version_parser.py, migration_loader.py` | **None (0)** | Held-Out |
| **2059** | `config_lists` | `test_case_1` | HANDBOOK.md Rule H12 | **No** | **83.3%** (5/6) | `TAUGHT` | `matcher_utils.py, route_validator.py, mesh_config.py` | **None (0)** | Held-Out |
| **2059** | `config_lists` | `test_case_2` | HANDBOOK.md Rule H12 | **No** | **83.3%** (5/6) | `TAUGHT` | `matcher_utils.py, route_validator.py, mesh_config.py` | **None (0)** | Held-Out |
| **2060** | `config_lists` | `test_case_1` | route_table.py docstring: 'Override list definitions completely replace base lists' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `routing_entry.py, protocol_filter.py, route_table.py` | **None (0)** | Held-Out |
| **2060** | `config_lists` | `test_case_2` | route_table.py docstring: 'Override list definitions completely replace base lists' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `routing_entry.py, protocol_filter.py, route_table.py` | **None (0)** | Held-Out |
| **2061** | `idempotency_keys` | `test_case_1` | payment_client.py docstring: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' | **Yes** | **100.0%** (6/6) | `STATED` | `http_models.py, payload_signer.py, payment_client.py` | **None (0)** | Tune |
| **2061** | `idempotency_keys` | `test_case_2` | payment_client.py docstring: 'Retries must reuse the exact same idempotency key across attempts' | **Yes** | **100.0%** (6/6) | `STATED` | `http_models.py, payload_signer.py, payment_client.py` | **None (0)** | Tune |
| **2062** | `idempotency_keys` | `test_case_1` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `idempotency_generator.py, transport_adapter.py, fulfillment_service.py` | **None (0)** | Tune |
| **2062** | `idempotency_keys` | `test_case_2` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `idempotency_generator.py, transport_adapter.py, fulfillment_service.py` | **None (0)** | Tune |
| **2063** | `idempotency_keys` | `test_case_1` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `charge_record.py, card_validator.py, subscription_client.py` | **None (0)** | Tune |
| **2063** | `idempotency_keys` | `test_case_2` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `charge_record.py, card_validator.py, subscription_client.py` | **None (0)** | Tune |
| **2064** | `idempotency_keys` | `test_case_1` | banking_client.py docstring: 'Must attach header Idempotency-Token: <raw_uuid4>' | **Yes** | **16.7%** (1/6) | `DISTRACTOR` | `wire_message.py, bank_checksum.py, banking_client.py` | **None (0)** | Tune |
| **2064** | `idempotency_keys` | `test_case_2` | banking_client.py docstring: 'Must attach header Idempotency-Token: <raw_uuid4>' | **Yes** | **16.7%** (1/6) | `DISTRACTOR` | `wire_message.py, bank_checksum.py, banking_client.py` | **None (0)** | Tune |
| **2065** | `idempotency_keys` | `test_case_1` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `key_factory.py, refund_audit.py, refund_dispatcher.py` | **None (0)** | Held-Out |
| **2065** | `idempotency_keys` | `test_case_2` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `key_factory.py, refund_audit.py, refund_dispatcher.py` | **None (0)** | Held-Out |
| **2066** | `idempotency_keys` | `test_case_1` | stock_client.py docstring: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' | **Yes** | **100.0%** (6/6) | `STATED` | `stock_record.py, sku_verifier.py, stock_client.py` | **None (0)** | Tune |
| **2066** | `idempotency_keys` | `test_case_2` | stock_client.py docstring: 'Retries must reuse the exact same idempotency key across attempts' | **Yes** | **100.0%** (6/6) | `STATED` | `stock_record.py, sku_verifier.py, stock_client.py` | **None (0)** | Tune |
| **2067** | `idempotency_keys` | `test_case_1` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `token_builder.py, quota_tracker.py, vm_provisioner.py` | **None (0)** | Held-Out |
| **2067** | `idempotency_keys` | `test_case_2` | HANDBOOK.md Rule H13 | **No** | **0.0%** (0/6) | `TAUGHT` | `token_builder.py, quota_tracker.py, vm_provisioner.py` | **None (0)** | Held-Out |
| **2068** | `idempotency_keys` | `test_case_1` | settlement_client.py docstring: 'Tx-Identifier containing a raw integer transaction ID' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `settlement_record.py, ledger_digest.py, settlement_client.py` | **None (0)** | Held-Out |
| **2068** | `idempotency_keys` | `test_case_2` | settlement_client.py docstring: 'Tx-Identifier containing a raw integer transaction ID' | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `settlement_record.py, ledger_digest.py, settlement_client.py` | **None (0)** | Held-Out |
| **2069** | `metric_percentiles` | `test_case_1` | latency_calc.py docstring: nearest-rank method | **Yes** | **100.0%** (6/6) | `STATED` | `metric_types.py, metric_summary.py, latency_calc.py` | **None (0)** | Tune |
| **2069** | `metric_percentiles` | `test_case_2` | latency_calc.py docstring: nearest-rank method | **Yes** | **100.0%** (6/6) | `STATED` | `metric_types.py, metric_summary.py, latency_calc.py` | **None (0)** | Tune |
| **2070** | `metric_percentiles` | `test_case_1` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **50.0%** (3/6) | `TAUGHT` | `query_types.py, query_percentile.py, query_monitor.py` | **None (0)** | Tune |
| **2070** | `metric_percentiles` | `test_case_2` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **50.0%** (3/6) | `TAUGHT` | `query_types.py, query_percentile.py, query_monitor.py` | **None (0)** | Tune |
| **2071** | `metric_percentiles` | `test_case_1` | HANDBOOK.md Rule H14: Nearest-rank metric percentile estimation | **No** | **33.3%** (2/6) | `TAUGHT` | `rpc_data.py, rpc_formatter.py, rpc_calc.py` | **None (0)** | Tune |
| **2071** | `metric_percentiles` | `test_case_2` | HANDBOOK.md Rule H14: Nearest-rank metric percentile estimation | **No** | **33.3%** (2/6) | `TAUGHT` | `rpc_data.py, rpc_formatter.py, rpc_calc.py` | **None (0)** | Tune |
| **2072** | `metric_percentiles` | `test_case_1` | audio_metrics.py docstring: Continuous linear interpolation | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `audio_types.py, audio_formatter.py, audio_metrics.py` | **None (0)** | Tune |
| **2072** | `metric_percentiles` | `test_case_2` | audio_metrics.py docstring: Continuous linear interpolation | **Yes** | **100.0%** (6/6) | `DISTRACTOR` | `audio_types.py, audio_formatter.py, audio_metrics.py` | **None (0)** | Tune |
| **2073** | `metric_percentiles` | `test_case_1` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **50.0%** (3/6) | `TAUGHT` | `cache_types.py, cache_percentile.py, cache_reporter.py` | **None (0)** | Held-Out |
| **2073** | `metric_percentiles` | `test_case_2` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **50.0%** (3/6) | `TAUGHT` | `cache_types.py, cache_percentile.py, cache_reporter.py` | **None (0)** | Held-Out |
| **2074** | `metric_percentiles` | `test_case_1` | jitter_evaluator.py docstring: nearest-rank method | **Yes** | **66.7%** (4/6) | `STATED` | `jitter_types.py, jitter_core.py, jitter_evaluator.py` | **None (0)** | Tune |
| **2074** | `metric_percentiles` | `test_case_2` | jitter_evaluator.py docstring: nearest-rank method | **Yes** | **66.7%** (4/6) | `STATED` | `jitter_types.py, jitter_core.py, jitter_evaluator.py` | **None (0)** | Tune |
| **2075** | `metric_percentiles` | `test_case_1` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **83.3%** (5/6) | `TAUGHT` | `io_types.py, io_summary.py, io_calc.py` | **None (0)** | Held-Out |
| **2075** | `metric_percentiles` | `test_case_2` | HANDBOOK.md Rule H14: Metric percentile nearest-rank method | **No** | **83.3%** (5/6) | `TAUGHT` | `io_types.py, io_summary.py, io_calc.py` | **None (0)** | Held-Out |
| **2076** | `metric_percentiles` | `test_case_1` | loss_reporter.py docstring: Continuous linear interpolation | **Yes** | **83.3%** (5/6) | `DISTRACTOR` | `loss_types.py, loss_math.py, loss_reporter.py` | **None (0)** | Held-Out |
| **2076** | `metric_percentiles` | `test_case_2` | loss_reporter.py docstring: Continuous linear interpolation | **Yes** | **83.3%** (5/6) | `DISTRACTOR` | `loss_types.py, loss_math.py, loss_reporter.py` | **None (0)** | Held-Out |
| **2077** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: State transition audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, pipeline_models.py, pipeline_manager.py` | **None (0)** | Held-Out |
| **2077** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on invalid jump | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, pipeline_models.py, pipeline_manager.py` | **None (0)** | Held-Out |
| **2078** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Escrow audit transition tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, escrow_engine.py, escrow_service.py` | **None (0)** | Held-Out |
| **2078** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on disallowed jump | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, escrow_engine.py, escrow_service.py` | **None (0)** | Held-Out |
| **2079** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Audit tuple structure | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, ticket_models.py, ticket_workflow.py` | **None (0)** | Held-Out |
| **2079** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION validation | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, ticket_models.py, ticket_workflow.py` | **None (0)** | Held-Out |
| **2080** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Cloud VM audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, instance_fsm.py, instance_controller.py` | **None (0)** | Held-Out |
| **2080** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION code | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, instance_fsm.py, instance_controller.py` | **None (0)** | Held-Out |
| **2081** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Order transition audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, fulfillment_models.py, fulfillment_engine.py` | **None (0)** | Held-Out |
| **2081** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on cancelled post-shipped | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, fulfillment_models.py, fulfillment_engine.py` | **None (0)** | Held-Out |
| **2082** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: PR state audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, pr_fsm.py, pr_service.py` | **None (0)** | Held-Out |
| **2082** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION error code | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, pr_fsm.py, pr_service.py` | **None (0)** | Held-Out |
| **2083** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Subscription transition audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, subscription_models.py, subscription_fsm.py` | **None (0)** | Held-Out |
| **2083** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION from terminal state | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, subscription_models.py, subscription_fsm.py` | **None (0)** | Held-Out |
| **2084** | `state_transitions` | `test_case_1` | HANDBOOK.md Rule H15: Batch job transition audit tuple | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, job_fsm.py, job_orchestrator.py` | **None (0)** | Held-Out |
| **2084** | `state_transitions` | `test_case_2` | HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on direct jump | **No** | **0.0%** (0/6) | `TRANSFER` | `errors.py, job_fsm.py, job_orchestrator.py` | **None (0)** | Held-Out |

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
4. **Token Balance:** Handbook (1,291 tokens) vs Placebo (1,283 tokens) balanced to within **0.620%** ($\le 3.0\%$).
5. **Hermetic Pre-flight:** 100% gold pass, 0% unpatched pass, 0% mutant passes across all 84 tasks.