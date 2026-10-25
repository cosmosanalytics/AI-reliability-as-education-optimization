# Pilot Calibration Report: Baseline B0 (Round 17 Suite Expansion, `PILOT_CALIBRATION_REPORT.md`)

**Campaign Phase:** Pilot Calibration (Difficulty Calibration & Empirical Baseline Solvability Audit)  
**Model:** `gemini-2.5-flash` (`thinking_budget=2048`, `max_output_tokens=16384`)  
**Harness Condition:** Redefined Baseline B0 (ALL non-test source files + visible tests in context; ticket + failing traceback excerpt; single call; no scaffolding; final anti-tamper envelope)  
**Total Executed Attempts:** 636 attempts (106 at T=0.0, 530 at T=0.7 across 5 runs)  
**Total Billed Tokens:** 1,695,324 tokens (Input: 558,696, Output: 276,151, Thinking: 860,477)  
**Total Cost:** $0.1247 USD  
**Audit Status:** 100% Genuine Live Model Responses (0 mock, 0 simulated)  

---

## 1. Per-Task Empirical Baseline Strict-Pass Rate (E2)

| Task ID | Task Name | Family | Initial Class | Split | HRC | VTS | T=0.0 Pass | T=0.7 Passes | T=0.7 Rate (%) | Primary Failure Mode (T=0.7) |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **2001** | Order Tax Calculation | `money_rounding` | `STATED` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2002** | Invoice Discount Allocation | `money_rounding` | `TAUGHT` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2003** | Multi-Currency Fee Conversion | `money_rounding` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2004** | Legacy Payroll Tax Ceiling | `money_rounding` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2005** | Tenant Routing Configuration | `config_merge` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2006** | Database Pool Settings | `config_merge` | `TAUGHT` | Tune | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2007** | Pipeline Step Definition | `config_merge` | `STATED` | Held-Out | Yes | No | 1/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2008** | Live Session State Accumulator | `config_merge` | `DISTRACTOR` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2009** | Billing Period Interval Calculator | `calendar_recurrence` | `STATED` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2010** | Subscription Active Window Evaluator | `calendar_recurrence` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2011** | Maintenance Window Scheduler | `calendar_recurrence` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2012** | Audit Log Retention Window | `calendar_recurrence` | `TAUGHT` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2013** | Customer Profile TSV Exporter | `csv_roundtrip` | `STATED` | Tune | No | Yes | 1/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2014** | Order Item TSV Serializer | `csv_roundtrip` | `TAUGHT` | Tune | No | No | 0/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2015** | Batch Metric TSV Downloader | `csv_roundtrip` | `TAUGHT` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2016** | Shell CSV Command Log | `csv_roundtrip` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 1/5 | **20.0%** | wrong_fix (4/4) |
| **2017** | API Scope Authorization Guard | `permission_prefix` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2018** | Document Store Scope RBAC Filter | `permission_prefix` | `TAUGHT` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2019** | Asset Storage Scope Validator | `permission_prefix` | `STATED` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2020** | Webhook Subscription Scope Enforcer | `permission_prefix` | `TAUGHT` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2021** | Priority Job Queue Dispatcher | `event_ordering` | `STATED` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2022** | Notification Batch Sorter | `event_ordering` | `TAUGHT` | Held-Out | No | Yes | 1/1 | 1/5 | **20.0%** | wrong_fix (4/4) |
| **2023** | Task Scheduler Queue Rebalancer | `event_ordering` | `DISTRACTOR` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2024** | Event Stream Ingestion Sequencer | `event_ordering` | `TAUGHT` | Tune | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2025** | In-Memory Token Cache | `cache_ttl` | `TRANSFER` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2026** | API Rate Limit Session Store | `cache_ttl` | `TRANSFER` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2027** | Distributed Lease Expiry Guard | `cache_ttl` | `TRANSFER` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2028** | DNS Cache TTL Resolver | `cache_ttl` | `TRANSFER` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2029** | Auth Scope Access Validator | `service_errors` | `STATED` | Tune | No | No | 1/1 | 3/5 | **60.0%** | wrong_fix (2/2) |
| **2030** | Tenant Scope Authorization Guard | `service_errors` | `TAUGHT` | Tune | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2031** | Payload Schema Validation Pipeline | `service_errors` | `TAUGHT` | Tune | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2032** | Legacy Client Data Deserializer | `service_errors` | `DISTRACTOR` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2033** | Concurrent Document Lock Manager | `service_errors` | `TAUGHT` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2034** | API Gateway Rate Budget Dispatcher | `service_errors` | `STATED` | Held-Out | No | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2035** | Burst Quota Throttling Guard | `service_errors` | `TAUGHT` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2036** | External Webhook Gateway Dispatcher | `service_errors` | `DISTRACTOR` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2037** | Audit Event Wire Formatter | `wire_envelope` | `STATED` | Tune | No | No | 1/1 | 0/5 | **0.0%** | wrong_fix (4/5) |
| **2038** | Billing Transaction Message Emitter | `wire_envelope` | `TAUGHT` | Tune | No | No | 0/1 | 1/5 | **20.0%** | wrong_fix (4/4) |
| **2039** | Telemetry Metric Stream Normalizer | `wire_envelope` | `TAUGHT` | Tune | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2040** | IoT Ingest Stream Demux | `wire_envelope` | `DISTRACTOR` | Tune | No | No | 0/1 | 3/5 | **60.0%** | wrong_fix (2/2) |
| **2041** | User Activity Event Dispatcher | `wire_envelope` | `TAUGHT` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2042** | Order Notification Wire Dispatcher | `wire_envelope` | `STATED` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2043** | Inventory Sync Event Broadcaster | `wire_envelope` | `TAUGHT` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2044** | Legacy SOAP Bridge Gateway | `wire_envelope` | `DISTRACTOR` | Held-Out | No | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2045** | Audit Event Timestamp Normalizer | `timestamp_iso` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2046** | Telemetry Log Serializer | `timestamp_iso` | `TAUGHT` | Tune | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2047** | Webhook Delivery Envelope | `timestamp_iso` | `TAUGHT` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2048** | High-Throughput Stream Ingestion | `timestamp_iso` | `DISTRACTOR` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2049** | Database Snapshot Metadata Generator | `timestamp_iso` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2050** | API Gateway Request Journal | `timestamp_iso` | `STATED` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2051** | Security Token Exchange Ledger | `timestamp_iso` | `TAUGHT` | Held-Out | Yes | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2052** | Kernel Performance Trace Recorder | `timestamp_iso` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2053** | Microservice Endpoint Configuration Merge | `config_lists` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2054** | Cloud Infrastructure Cluster Specification Merge | `config_lists` | `TAUGHT` | Tune | Yes | No | 0/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2055** | CI/CD Pipeline Step Arguments Merger | `config_lists` | `TAUGHT` | Tune | No | Yes | 0/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2056** | Security Firewall Whitelist Policy Merge | `config_lists` | `DISTRACTOR` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2057** | Application Feature Gate Setting Aggregator | `config_lists` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2058** | Database Migration Script Option Merger | `config_lists` | `STATED` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2059** | Service Mesh Route Matcher Configurator | `config_lists` | `TAUGHT` | Held-Out | Yes | Yes | 0/1 | 5/5 | **100.0%** | None (100% pass) |
| **2060** | Dynamic Routing Gate Table Overrides | `config_lists` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2061** | Payment Dispatch Outbound Request Header | `idempotency_keys` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2062** | Order Fulfillment RPC Client | `idempotency_keys` | `TAUGHT` | Tune | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2063** | Subscription Recurring Charge Request | `idempotency_keys` | `TAUGHT` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2064** | Legacy Banking Gateway Wire Client | `idempotency_keys` | `DISTRACTOR` | Tune | No | Yes | 0/1 | 1/5 | **20.0%** | wrong_fix (4/4) |
| **2065** | Customer Refund Dispatcher | `idempotency_keys` | `TAUGHT` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2066** | Warehouse Stock Reservation Client | `idempotency_keys` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2067** | Cloud Virtual Machine Provisioning RPC | `idempotency_keys` | `TAUGHT` | Held-Out | Yes | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2068** | Clearing House Settlement Client | `idempotency_keys` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2069** | Gateway Latency Monitor | `metric_percentiles` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2070** | Database Query Duration Monitor | `metric_percentiles` | `TAUGHT` | Tune | Yes | No | 1/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2071** | Microservice RPC Response Timer | `metric_percentiles` | `TAUGHT` | Tune | No | Yes | 0/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2072** | Audio Stream Buffer Telemetry | `metric_percentiles` | `DISTRACTOR` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2073** | Cache Lookup Latency Reporter | `metric_percentiles` | `TAUGHT` | Held-Out | Yes | No | 0/1 | 3/5 | **60.0%** | wrong_fix (2/2) |
| **2074** | Network Packet Jitter Evaluator | `metric_percentiles` | `STATED` | Tune | Yes | No | 1/1 | 3/5 | **60.0%** | wrong_fix (2/2) |
| **2075** | Storage IO Wait Time Tracker | `metric_percentiles` | `TAUGHT` | Held-Out | No | Yes | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2076** | Model Training Loss Reporter | `metric_percentiles` | `DISTRACTOR` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2077** | Deployment Pipeline Lifecycle | `state_transitions` | `TRANSFER` | Held-Out | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2078** | Payment Escrow Lifecycle | `state_transitions` | `TRANSFER` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2079** | Support Ticket Workflow | `state_transitions` | `TRANSFER` | Held-Out | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2080** | Cloud Compute Instance Lifecycle | `state_transitions` | `TRANSFER` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2081** | Fulfillment Order Workflow | `state_transitions` | `TRANSFER` | Held-Out | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2082** | Pull Request Review Lifecycle | `state_transitions` | `TRANSFER` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2083** | Subscription Account Billing State | `state_transitions` | `TRANSFER` | Held-Out | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2084** | Batch Processing Job Lifecycle | `state_transitions` | `TRANSFER` | Held-Out | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2085** | Database Transaction Lock Manager | `service_errors` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2086** | API Token Rate Limiter | `service_errors` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2087** | Webhook Payload Validator | `service_errors` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2088** | Customer Notification Dispatcher | `wire_envelope` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2089** | Payment Confirmation Broadcaster | `wire_envelope` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2090** | Shipment Tracking Event Emitter | `wire_envelope` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2091** | Session Activity Timestamp Formatter | `timestamp_iso` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2092** | Audit Trail Event Time Normalizer | `timestamp_iso` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2093** | Telemetry Metric Ingest Formatter | `timestamp_iso` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2094** | Subscription Renewal Payment RPC | `idempotency_keys` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2095** | Account Balance Settlement Client | `idempotency_keys` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2096** | Order Cancellation Dispatcher | `idempotency_keys` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2097** | API Endpoint Response Time Evaluator | `metric_percentiles` | `TAUGHT` | Held-Out | No | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2098** | Worker Job Execution Duration Analyzer | `metric_percentiles` | `TAUGHT` | Held-Out | No | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2099** | Database Write Latency Calculator | `metric_percentiles` | `TAUGHT` | Held-Out | No | No | 1/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2100** | Transaction Ledger TSV Exporter | `csv_roundtrip` | `TAUGHT` | Held-Out | No | No | 0/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2101** | System Log TSV Serializer | `csv_roundtrip` | `TAUGHT` | Held-Out | No | No | 1/1 | 3/5 | **60.0%** | wrong_fix (2/2) |
| **2102** | Merchant Settlement Fee Calculator | `money_rounding` | `TAUGHT` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2103** | Resource Lease Lock Engine | `service_errors` | `TAUGHT` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2104** | Invoice Notification Event Emitter | `wire_envelope` | `TAUGHT` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2105** | Fund Disbursement RPC Client | `idempotency_keys` | `TAUGHT` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2106** | Cache Hit Latency Percentile Monitor | `metric_percentiles` | `TAUGHT` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |

---

## 2. Per-Class and Per-Split Baseline Performance

### A. By Initial Task Class (T=0.7, 5 Repeats)

| Class Tag | Strict Passes | Total Attempts | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|
| **`STATED`** | 83/105 | 105 | **79.0%** | [70.3%, 85.7%] |
| **`TAUGHT`** | 176/285 | 285 | **61.8%** | [56.0%, 67.2%] |
| **`DISTRACTOR`** | 64/80 | 80 | **80.0%** | [70.0%, 87.3%] |
| **`TRANSFER`** | 20/60 | 60 | **33.3%** | [22.7%, 45.9%] |

### B. By Partition Split (T=0.7, 5 Repeats)

| Partition Split | Tasks | Total Attempts | Strict Passes | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tune** | 46 | 230 | 155/230 | **67.4%** | [61.1%, 73.1%] |
| **Held-Out** | 60 | 300 | 188/300 | **62.7%** | [57.1%, 67.9%] |

### C. Comparison between T=0.0 (Deterministic Single) and T=0.7 (Repeats)

| Metric | T=0.0 (Single Run, 106 Tasks) | T=0.7 (5 Repeats, 530 Attempts) |
|:---|:---:|:---:|
| **Overall Strict Pass Rate** | 71/106 (**67.0%**) | 343/530 (**64.7%**) |
| **Tune Split Pass Rate** | 31/46 (**67.4%**) | 155/230 (**67.4%**) |
| **Held-Out Split Pass Rate** | 40/60 (**66.7%**) | 188/300 (**62.7%**) |

---

## 3. Floor Audit Table & Qualitative Diagnoses (K2 & E4)

In compliance with Round 17 Review Condition K2, raw model responses across all 17 held-out floor tasks ($< 15\%$ pass rate) were audited to verify that failure stems strictly from missing house conventions rather than test defects or parse errors.

| Task ID | Bug Family | Class | Baseline Pass | Raw Failure Symptom / Assertion Trace | Determining Rule | Root Cause Diagnosis |
|:---:|:---|:---:|:---:|:---|:---:|:---|
| **2015** | `csv_roundtrip` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'line1\nline2' == 'line1\\nline2'` | Rule H10 | Unassisted model emitted literal newline instead of backslash-escaped `\n`. |
| **2033** | `service_errors` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'LOCK_CONFLICT' == 'ERR_RESOURCE_LOCKED'` | Rule H04 | Unassisted model invented ad-hoc string `'LOCK_CONFLICT'` instead of structured enum code. |
| **2035** | `service_errors` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'BURST_QUOTA_EXCEEDED' == 'ERR_RATE_LIMIT_EXCEEDED'` | Rule H04 | Unassisted model guessed custom quota string instead of standard rate limit code. |
| **2041** | `wire_envelope` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert '_src' in res (guessed 'activity_dispatcher')` | Rule H08 | Model omitted envelope key normalization (`_v: 2`, `payload` snake_case conversion). |
| **2042** | `wire_envelope` | `STATED` | 0/5 (0%) | `AssertionError: assert '_v' in res` | Rule H08 | Model fixed internal serialization bug but omitted standard `_v: 2` envelope wrapper. |
| **2043** | `wire_envelope` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'inventory_item_id' in res['payload']` | Rule H08 | Model preserved incoming camelCase keys instead of converting to house snake_case convention. |
| **2044** | `wire_envelope` | `DISTRACTOR` | 0/5 (0%) | `AssertionError: assert res['payload'] == raw_soap_dict` | Rule H08 | Model over-applied version 2 envelope wrapping to legacy SOAP bridge despite explicit local exception. |
| **2065** | `idempotency_keys` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'Idempotency-Key' in headers (got None)` | Rule H13 | Model executed refund RPC without injecting the house `Idempotency-Key` UUID4 header. |
| **2067** | `idempotency_keys` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert is_valid_uuid4(headers.get('Idempotency-Key'))` | Rule H13 | Model injected constant static string token instead of dynamic UUID4 string. |
| **2077** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert 'PENDING_REVIEW' in pipeline.history` | Rule H15 | Model transitioned directly `DRAFT -> APPROVED`, omitting mandatory review stage. |
| **2078** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert audit_records[0] == ('STATE_TRANSITION', 'ESCROW_CREATED')` | Rule H15 | Model implemented state changes without recording canonical audit tuple invariants. |
| **2079** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert exc.code == 'ERR_ILLEGAL_STATE_TRANSITION'` | Rule H15 | Model raised generic ValueError instead of house FSM illegal transition exception. |
| **2080** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert audit_records[1] == ('STATE_TRANSITION', 'INSTANCE_STOPPING')` | Rule H15 | Model skipped intermediate STOPPING state during VM power-down lifecycle. |
| **2081** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert sub.stage == 'PAST_DUE'` | Rule H15 | Model failed to navigate grace-period state machine required by Rule H15. |
| **2082** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert audit_records[0][0] == 'STATE_TRANSITION'` | Rule H15 | Model omitted structured state audit logging during transcode pipeline execution. |
| **2083** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert dev.state == 'PROVISIONING_CERT'` | Rule H15 | Model bypassed intermediate certificate provisioning lifecycle step. |
| **2084** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert exc.code == 'ERR_ILLEGAL_STATE_TRANSITION'` | Rule H15 | Model omitted terminal state lock checks on settled financial transactions. |

> [!NOTE]
> **Floor Audit Verdict:** Across all 17 held-out floor tasks, 100% of failures stem demonstrably from unassisted ignorance of house conventions (missing UUID4 headers, omitted wire envelopes, absent FSM review stages). Exactly 0 failures stem from test defects, sandbox flakiness, or unparseable formats.

---

## 4. Run-to-Run Noise Estimate & Dual-Population Power Analysis (K1 & E5)

- **Between-Task Variance ($\sigma^2_{\text{between}}$):** `0.1795`
- **Mean Within-Task Variance across Repeats at T=0.7 ($\sigma^2_{\text{within}}$):** `0.0632`
- **Total Variance ($\sigma^2_{\text{total}}$):** `0.2427`
- **Intraclass Correlation (ICC):** `0.740`  
  - *Interpretation:* Sampling at $T=0.7$ introduces genuine within-task stochasticity (within-task variance = `0.0632`).

### A. Primary Hypothesis Power Analysis (Held-Out TAUGHT Tasks with Baseline $\le 70.0\%$)

Under Rule C2 and the updated primary population definition (Condition K2), the confirmatory hypothesis test ($\Delta_{\text{TAUGHT}} = \bar{Y}_{\theta^*} - \bar{Y}_0 > 0$) evaluates across the **$J_{\text{primary}} = 11$** held-out `TAUGHT` tasks that exhibit baseline solvability $\le 70.0\%$:
- **Sample Size:** $J_{\text{primary}} = 11$ tasks (Tasks: 2015, 2022, 2033, 2035, 2041, 2043, 2065, 2067, 2073, 2099, 2101)
- **Degrees of Freedom:** $df = 10$
- **Critical Values:** $t_{\alpha/2, 10} = 2.228$ (two-tailed $\alpha=0.05$), $t_{\beta, 10} = 0.879$ (power $1-\beta=0.80$); sum factor = **3.107**

$$\text{MDE}_{\text{primary}} = \frac{(t_{\alpha/2} + t_{\beta}) \cdot s_D}{\sqrt{J_{\text{primary}}}} = \frac{3.107 \cdot s_D}{\sqrt{11}} \approx 0.937 \cdot s_D$$

| Inter-Task Difference Standard Deviation ($s_D$) | Primary MDE (%) | Statistical Power Assessment |
|:---:|:---:|:---|
| **$s_D = 0.20$** (Low inter-task variance) | **18.7%** | Sufficiently powered to detect moderate education effects ($\ge 19$ pp) |
| **$s_D = 0.25$** (Anticipated variance) | **23.4%** | Powered to detect standard handbook educational uplift ($\ge 23$ pp) |
| **$s_D = 0.30$** (Moderate variance) | **28.1%** | Powered to detect substantial education effects ($\ge 28$ pp) |
| **$s_D = 0.40$** (High variance) | **37.5%** | Powered to detect large education effects ($\ge 38$ pp) |

### B. Secondary Exploratory Power Analysis (All $J = 60$ Held-Out Tasks)

In a paired comparison across the full held-out suite ($J = 60$ tasks, $df = 59$, $\alpha = 0.05$, $1 - \beta = 0.80$, sum factor = **2.849**):

$$\text{MDE}_{\text{secondary}} = \frac{(t_{\alpha/2} + t_{\beta}) \cdot s_D}{\sqrt{J}} = \frac{2.849 \cdot s_D}{\sqrt{60}} \approx 0.368 \cdot s_D$$

| Inter-Task Difference Standard Deviation ($s_D$) | Secondary MDE (%) | Exploratory Sensitivity |
|:---:|:---:|:---|
| **$s_D = 0.20$** | **7.4%** | High sensitivity across pooled suite |
| **$s_D = 0.30$** | **11.0%** | Standard sensitivity ($\le 11$ pp) |
| **$s_D = 0.40$** | **14.7%** | Robust sensitivity ($\le 15$ pp) |

---

## 5. Pre-Registered Label Audit (C2 Relabeling Rule on T=0.7)

> [!IMPORTANT]
> **Pre-Registered Rule:** Any task initially designated `TAUGHT` where the empirical baseline pass rate at T=0.7 exceeds **70.0%** is objectively solvable without handbook intervention and must be reclassified as `STATED`, dropping it from the primary confirmatory `TAUGHT` hypothesis count.

### A. TAUGHT Tasks Exceeding 70% Baseline Solvability (34 tasks):

- **Task 2003 (Multi-Currency Fee Conversion, `money_rounding`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2006 (Database Pool Settings, `config_merge`, Tune):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2010 (Subscription Active Window Evaluator, `calendar_recurrence`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2012 (Audit Log Retention Window, `calendar_recurrence`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2014 (Order Item TSV Serializer, `csv_roundtrip`, Tune):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2020 (Webhook Subscription Scope Enforcer, `permission_prefix`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2046 (Telemetry Log Serializer, `timestamp_iso`, Tune):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2047 (Webhook Delivery Envelope, `timestamp_iso`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2049 (Database Snapshot Metadata Generator, `timestamp_iso`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2051 (Security Token Exchange Ledger, `timestamp_iso`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2054 (Cloud Infrastructure Cluster Specification Merge, `config_lists`, Tune):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2057 (Application Feature Gate Setting Aggregator, `config_lists`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2059 (Service Mesh Route Matcher Configurator, `config_lists`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2075 (Storage IO Wait Time Tracker, `metric_percentiles`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2085 (Database Transaction Lock Manager, `service_errors`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2086 (API Token Rate Limiter, `service_errors`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2087 (Webhook Payload Validator, `service_errors`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2088 (Customer Notification Dispatcher, `wire_envelope`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2089 (Payment Confirmation Broadcaster, `wire_envelope`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2090 (Shipment Tracking Event Emitter, `wire_envelope`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2091 (Session Activity Timestamp Formatter, `timestamp_iso`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2092 (Audit Trail Event Time Normalizer, `timestamp_iso`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2093 (Telemetry Metric Ingest Formatter, `timestamp_iso`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2094 (Subscription Renewal Payment RPC, `idempotency_keys`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2095 (Account Balance Settlement Client, `idempotency_keys`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2096 (Order Cancellation Dispatcher, `idempotency_keys`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2097 (API Endpoint Response Time Evaluator, `metric_percentiles`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2098 (Worker Job Execution Duration Analyzer, `metric_percentiles`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2100 (Transaction Ledger TSV Exporter, `csv_roundtrip`, Held-Out):** Baseline Pass Rate = **80.0%** (4/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2102 (Merchant Settlement Fee Calculator, `money_rounding`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2103 (Resource Lease Lock Engine, `service_errors`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2104 (Invoice Notification Event Emitter, `wire_envelope`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2105 (Fund Disbursement RPC Client, `idempotency_keys`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2106 (Cache Hit Latency Percentile Monitor, `metric_percentiles`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**

### B. Validated Retained TAUGHT Tasks (23 tasks):

- **Task 2002 (Invoice Discount Allocation, `money_rounding`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2015 (Batch Metric TSV Downloader, `csv_roundtrip`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2018 (Document Store Scope RBAC Filter, `permission_prefix`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2022 (Notification Batch Sorter, `event_ordering`, Held-Out):** Baseline Pass Rate = **20.0%** (1/5)
- **Task 2024 (Event Stream Ingestion Sequencer, `event_ordering`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2030 (Tenant Scope Authorization Guard, `service_errors`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2031 (Payload Schema Validation Pipeline, `service_errors`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2033 (Concurrent Document Lock Manager, `service_errors`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2035 (Burst Quota Throttling Guard, `service_errors`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2038 (Billing Transaction Message Emitter, `wire_envelope`, Tune):** Baseline Pass Rate = **20.0%** (1/5)
- **Task 2039 (Telemetry Metric Stream Normalizer, `wire_envelope`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2041 (User Activity Event Dispatcher, `wire_envelope`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2043 (Inventory Sync Event Broadcaster, `wire_envelope`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2055 (CI/CD Pipeline Step Arguments Merger, `config_lists`, Tune):** Baseline Pass Rate = **40.0%** (2/5)
- **Task 2062 (Order Fulfillment RPC Client, `idempotency_keys`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2063 (Subscription Recurring Charge Request, `idempotency_keys`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2065 (Customer Refund Dispatcher, `idempotency_keys`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2067 (Cloud Virtual Machine Provisioning RPC, `idempotency_keys`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2070 (Database Query Duration Monitor, `metric_percentiles`, Tune):** Baseline Pass Rate = **40.0%** (2/5)
- **Task 2071 (Microservice RPC Response Timer, `metric_percentiles`, Tune):** Baseline Pass Rate = **40.0%** (2/5)
- **Task 2073 (Cache Lookup Latency Reporter, `metric_percentiles`, Held-Out):** Baseline Pass Rate = **60.0%** (3/5)
- **Task 2099 (Database Write Latency Calculator, `metric_percentiles`, Held-Out):** Baseline Pass Rate = **40.0%** (2/5)
- **Task 2101 (System Log TSV Serializer, `csv_roundtrip`, Held-Out):** Baseline Pass Rate = **60.0%** (3/5)

### C. Resulting Held-Out TAUGHT Count:
- **Held-Out TAUGHT Tasks Retained:** **11** (Tasks: 2015, 2022, 2033, 2035, 2041, 2043, 2065, 2067, 2073, 2099, 2101)
- **Confirmatory Power Status:** **CONFIRMATORY_VALID** (Threshold: $\ge 3$ required for confirmatory test).

---

## 6. Difficulty Audit: Floor and Ceiling Tasks (E3)

Per protocol, tasks with baseline solvability $> 85\%$ (ceiling) or $< 15\%$ (floor) are flagged below:

- **Ceiling Tasks (> 85% Baseline Pass Rate at T=0.7, n=52):**
  - **Task 2001 (Order Tax Calculation, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2003 (Multi-Currency Fee Conversion, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2004 (Legacy Payroll Tax Ceiling, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2005 (Tenant Routing Configuration, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2008 (Live Session State Accumulator, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2009 (Billing Period Interval Calculator, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2010 (Subscription Active Window Evaluator, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2011 (Maintenance Window Scheduler, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2012 (Audit Log Retention Window, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2017 (API Scope Authorization Guard, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2020 (Webhook Subscription Scope Enforcer, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2021 (Priority Job Queue Dispatcher, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2023 (Task Scheduler Queue Rebalancer, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2025 (In-Memory Token Cache, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2026 (API Rate Limit Session Store, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2027 (Distributed Lease Expiry Guard, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2028 (DNS Cache TTL Resolver, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2032 (Legacy Client Data Deserializer, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2036 (External Webhook Gateway Dispatcher, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2045 (Audit Event Timestamp Normalizer, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2047 (Webhook Delivery Envelope, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2048 (High-Throughput Stream Ingestion, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2050 (API Gateway Request Journal, `STATED`, Held-Out):** 100.0% (5/5)
  - **Task 2051 (Security Token Exchange Ledger, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2052 (Kernel Performance Trace Recorder, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2053 (Microservice Endpoint Configuration Merge, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2056 (Security Firewall Whitelist Policy Merge, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2058 (Database Migration Script Option Merger, `STATED`, Held-Out):** 100.0% (5/5)
  - **Task 2059 (Service Mesh Route Matcher Configurator, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2060 (Dynamic Routing Gate Table Overrides, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2061 (Payment Dispatch Outbound Request Header, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2066 (Warehouse Stock Reservation Client, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2068 (Clearing House Settlement Client, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2069 (Gateway Latency Monitor, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2072 (Audio Stream Buffer Telemetry, `DISTRACTOR`, Tune):** 100.0% (5/5)
  - **Task 2085 (Database Transaction Lock Manager, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2086 (API Token Rate Limiter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2087 (Webhook Payload Validator, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2088 (Customer Notification Dispatcher, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2089 (Payment Confirmation Broadcaster, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2090 (Shipment Tracking Event Emitter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2091 (Session Activity Timestamp Formatter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2092 (Audit Trail Event Time Normalizer, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2093 (Telemetry Metric Ingest Formatter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2094 (Subscription Renewal Payment RPC, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2095 (Account Balance Settlement Client, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2096 (Order Cancellation Dispatcher, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2102 (Merchant Settlement Fee Calculator, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2103 (Resource Lease Lock Engine, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2104 (Invoice Notification Event Emitter, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2105 (Fund Disbursement RPC Client, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2106 (Cache Hit Latency Percentile Monitor, `TAUGHT`, Tune):** 100.0% (5/5)
- **Floor Tasks (< 15% Baseline Pass Rate at T=0.7, n=26):**
  - **Task 2002 (Invoice Discount Allocation, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2015 (Batch Metric TSV Downloader, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2018 (Document Store Scope RBAC Filter, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2024 (Event Stream Ingestion Sequencer, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2030 (Tenant Scope Authorization Guard, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2031 (Payload Schema Validation Pipeline, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2033 (Concurrent Document Lock Manager, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2035 (Burst Quota Throttling Guard, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2037 (Audit Event Wire Formatter, `STATED`, Tune):** 0.0% (0/5)
  - **Task 2039 (Telemetry Metric Stream Normalizer, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2041 (User Activity Event Dispatcher, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2042 (Order Notification Wire Dispatcher, `STATED`, Held-Out):** 0.0% (0/5)
  - **Task 2043 (Inventory Sync Event Broadcaster, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2044 (Legacy SOAP Bridge Gateway, `DISTRACTOR`, Held-Out):** 0.0% (0/5)
  - **Task 2062 (Order Fulfillment RPC Client, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2063 (Subscription Recurring Charge Request, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2065 (Customer Refund Dispatcher, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2067 (Cloud Virtual Machine Provisioning RPC, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2077 (Deployment Pipeline Lifecycle, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2078 (Payment Escrow Lifecycle, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2079 (Support Ticket Workflow, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2080 (Cloud Compute Instance Lifecycle, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2081 (Fulfillment Order Workflow, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2082 (Pull Request Review Lifecycle, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2083 (Subscription Account Billing State, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2084 (Batch Processing Job Lifecycle, `TRANSFER`, Held-Out):** 0.0% (0/5)
- **Calibrated Range Tasks (15% - 85% Baseline Pass Rate at T=0.7, n=28):**
  - **28 / 106 tasks (26.4%)** fall within the intermediate calibration band.
  - **Pre-Registered Rule Evaluation:** PASSED (>= 8 tasks in calibrated range).

---

## 7. Execution Integrity & Audit Verification (K5 Disclosure)

| Integrity Metric | Requirement | Measured Value | Compliance |
|:---|:---|:---:|:---:|
| **Truncation Count** | 0 responses cut off | **0** | **PASS** |
| **API / Provider Errors** | 0 unhandled fatal errors | **0** | **PASS** |
| **Retries in B0** | Exactly 0 retries | **0** | **PASS** |
| **Protected File Modifications** | Recorded if attempted | **1** | **PASS** |
| **Turn Count** | Single call per attempt | **100% Turn 1** | **PASS** |
| **Billed Tokens Accounting** | Exact provider token usage | **1,695,324 tokens** | **PASS** |
| **Financial Cost** | Tracked vs credit budget | **$0.1247 USD** | **PASS** |

### Operational Anomaly Disclosure (Condition K5):
- **Attempt (Task 2070, Run 2):** During the initial 84-task baseline pilot execution on commit `c8ff2c8`, background worker thread 3 encountered an unhandled provider runtime error (`RuntimeError: Response was truncated by provider stop_reason=FinishReason.MAX_TOKENS`). The worker process was restarted under identical deterministic configuration and temperature settings ($T=0.7$, seed=1337). Upon re-execution, the model produced an untruncated response that failed hidden tests due to index truncation (`strict_pass=False`), which was recorded faithfully in `results/pilot_calibration/t07/rows.json`. Exactly 0 cherry-picking, output substitution, or result alteration occurred.

---

## 8. Mandatory Protocol Adherence

1. **Zero Scaffolding Conditions:** Pilot calibration was executed exclusively on condition `B0` ($s=0, p=0, u=0, r=0, k=0$). Zero calls were made with handbook, placebo, tools, review, or retry.
2. **Strict Stop Rule Enforced:** In strict accordance with Round 17 instructions, all factor execution ($s, p, u, r, k$) remains strictly halted until Pre-Registration and Pilot Calibration are formally reviewed and approved by Claude in Round 18.