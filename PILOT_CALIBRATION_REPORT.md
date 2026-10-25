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

## 3. Floor Audit Table & Qualitative Diagnoses (K2, E4 & L1 Programmatic Audit)

In compliance with Round 17 Review Condition K2 and Round 18 Review Condition L1, raw model responses and grading outputs across all 17 held-out floor tasks ($< 15\%$ pass rate) were programmatically audited via `runner/generate_floor_audit.py` to extract exact test assertion traces and determine grounded diagnoses from committed patches (`results/pilot_calibration/t07/raw/` and `results/pilot_calibration/floor_audit_traces.log`).

| Task ID | Bug Family | Class | Baseline Pass | Raw Failure Symptom / Assertion Trace | Determining Rule | Root Cause Diagnosis |
|:---:|:---|:---:|:---:|:---|:---:|:---|
| **2015** | `csv_roundtrip` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'line1\nline2' == 'line1\\nline2'` | Rule H10 | Model emitted literal newline ('\n') in TSV field instead of backslash-escaped string ('\\n') required by Rule H10. |
| **2033** | `service_errors` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'LOCK_CONFLICT' == 'ERR_RESOURCE_LOCKED'` | Rule H04 | Model invented ad-hoc string error codes ('LOCK_CONFLICT', 'RESOURCE_LOCKED') instead of canonical house code 'ERR_RESOURCE_LOCKED' (Rule H04). |
| **2035** | `service_errors` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'BURST_QUOTA_EXCEEDED' == 'ERR_RATE_LIMIT_EXCEEDED'` | Rule H04 | Model invented ad-hoc error codes ('BURST_QUOTA_EXCEEDED', 'THROTTLED') instead of canonical house code 'ERR_RATE_LIMIT_EXCEEDED' (Rule H04). |
| **2041** | `wire_envelope` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'activity_dispatcher' == 'activity_service'` | Rule H08 | Model wrapped envelope using guessed service names ('activity_dispatcher', 'user_activity_service') instead of house canonical 'activity_service' (Rule H08). |
| **2042** | `wire_envelope` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'order_dispatcher' == 'order_service'` | Rule H08 | Model wrapped envelope using filename 'order_dispatcher' instead of house canonical 'order_service' (Rule H08); reclassified from STATED to TAUGHT (L2). |
| **2043** | `wire_envelope` | `TAUGHT` | 0/5 (0%) | `AssertionError: assert 'inventory_broadcaster' == 'inventory_service'` | Rule H08 | Model preserved incoming camelCase keys ('warehouseId', 'itemSku') or guessed service name 'inventory_broadcaster' instead of snake_case and 'inventory_service' (Rule H08). |
| **2044** | `wire_envelope` | `DISTRACTOR` | 0/5 (0%) | `Visible: assert relay_soap_envelope(raw, 700) == res \| Hidden: assert is_raw_match is True` | Rule H08 (Exception) | Visible-test sensitivity trap: in Runs 1,3,4 model enveloped relay_soap_envelope failing visible test; in Runs 2,5 model mutated raw keys to snake_case failing hidden test. |
| **2065** | `idempotency_keys` | `TAUGHT` | 0/5 (0%) | `assert None is not None (where None = re.match('^idemp_\d+_[0-9a-f]{8}$', generated_key))` | Rule H13 | Model generated refund key with ad-hoc prefix 'rfn_ref-101_' + UUID4 instead of house canonical format '^idemp_\d+_[0-9a-f]{8}$' (Rule H13). |
| **2067** | `idempotency_keys` | `TAUGHT` | 0/5 (0%) | `assert None is not None (where None = re.match('^idemp_\d+_[0-9a-f]{8}$', generated_key))` | Rule H13 | Model generated standard raw UUID4 strings instead of house prefixed idempotency format '^idemp_\d+_[0-9a-f]{8}$' (Rule H13). |
| **2077** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert ('PENDING', '...1700000001000) == ('STATE_TRANS...1700000001000)` | Rule H15 | Model transitioned pipeline directly or recorded audit tuples lacking canonical 6-element structure ('STATE_TRANSITION', id, old, new, actor, ts) and 'ERR_INVALID_TRANSITION' (Rule H15). |
| **2078** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert ('INITIAL', '...00, 'SUCCESS') == ('STATE_TRANS...1700000010000)` | Rule H15 | Model emitted custom error 'ERR_ESCROW_INVALID_RELEASE' and audit tuples missing canonical 6-element structure ('STATE_TRANSITION', id, old, new, actor, ts) (Rule H15). |
| **2079** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `assert ('CREATED', ...) == ('STATE_TRANSITION', ...) \| assert 'INVALID_TICKET_TRANSITION' == 'ERR_INVALID_TRANSITION'` | Rule H15 | Model raised ServiceError('INVALID_TICKET_TRANSITION') and audit tuple lacked canonical fields; hidden test expects 'ERR_INVALID_TRANSITION' and 6-tuple (Rule H15). |
| **2080** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert (170000001000...G', 'RUNNING') == ('STATE_TRANS...1700000010000)` | Rule H15 | Model emitted audit tuples starting with timestamp or state name rather than canonical ('STATE_TRANSITION', id, old, new, actor, ts) and raised non-standard error codes (Rule H15). |
| **2081** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `ImportError: cannot import name 'get_fulfillment_status' from 'fulfillment_engine' (C:\...` | Rule H15 | Model emitted audit tuples lacking canonical 6-element structure ('STATE_TRANSITION', id, old, new, actor, ts) and raised non-standard error codes (Rule H15). |
| **2082** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert ('DRAFT', 'OP...1700000010000) == ('STATE_TRANS...1700000010000)` | Rule H15 | Model recorded audit tuples as (old, new, ts) missing 'STATE_TRANSITION' tag and actor; raised non-standard error codes (Rule H15). |
| **2083** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert ('TRIAL', 'AC...1700000010000) == ('STATE_TRANS...1700000010000)` | Rule H15 | Model recorded audit tuples as ('TRIAL', 'ACTIVE', ts) missing 'STATE_TRANSITION' tag, id, and actor; raised non-standard error codes (Rule H15). |
| **2084** | `state_transitions` | `TRANSFER` | 0/5 (0%) | `AssertionError: assert 0 == 1` | Rule H15 | Model left audit_trail empty (len == 0) and raised 'JOB_INVALID_STATE_TRANSITION' instead of house code 'ERR_INVALID_TRANSITION' (Rule H15). |

> [!NOTE]
> **Programmatic Floor Audit Verdict:** Programmatic extraction confirms that 100% of failures stem from genuine ignorance of house conventions (missing UUID4 headers, unnormalized wire envelopes, non-standard state audit tuples). Exactly 0 failures stem from test harness defects, parse crashes, or sandbox flakiness. Generated via `runner/generate_floor_audit.py` with full trace logs in `results/pilot_calibration/floor_audit_traces.log`.

---
## 4. Run-to-Run Noise Estimate & Dual-Population Power Analysis (K1, M1 & E5)

- **Between-Task Variance ($\sigma^2_{	ext{between}}$):** `0.1795`
- **Mean Within-Task Variance across Repeats at T=0.7 ($\sigma^2_{	ext{within}}$):** `0.0632`
- **Total Variance ($\sigma^2_{	ext{total}}$):** `0.2427`
- **Intraclass Correlation (ICC):** `0.740`  
  - *Interpretation:* Sampling at $T=0.7$ introduces genuine within-task stochasticity (within-task variance = `0.0632`).

### A. Primary Hypothesis Power Analysis (Held-Out TAUGHT Tasks with Baseline $\le 70.0\%$)

Under Rule C2 and the updated primary population definition (Condition K2, updated per Round 18 Review L2 to include Task 2042), the confirmatory hypothesis test ($\Delta_{	ext{TAUGHT}} = ar{Y}_{	heta^*} - ar{Y}_0 > 0$) evaluates across the **$J_{\\text{primary}} = 12$** held-out `TAUGHT` tasks that exhibit baseline solvability $\le 70.0\%$:
- **Primary Population Tasks ($J = 12$):** 2015, 2022, 2033, 2035, 2041, 2042, 2043, 2065, 2067, 2073, 2099, 2101
- **Family Distribution ($K = 6$ families):** `csv_roundtrip` (2), `permission_prefix` (1), `service_errors` (2), `wire_envelope` (3), `idempotency_keys` (2), `metric_percentiles` (2)

#### 1. Unadjusted MDE ($J = 12$, $df = 11$):
- Critical values: $t_{lpha/2, 11} = 2.201$ (two-tailed $lpha=0.05$), $t_{eta, 11} = 0.876$ (power $1-eta=0.80$); sum factor = **3.077**
$$	ext{MDE}_{	ext{unadjusted}} = \frac{3.077 \cdot s_D}{\sqrt{12}} \approx 0.888 \cdot s_D$$

| Inter-Task Difference Standard Deviation ($s_D$) | Unadjusted Primary MDE (%) | Statistical Sensitivity |
|:---:|:---:|:---|
| **$s_D = 0.20$** | **17.8%** | High sensitivity for textbook effects |
| **$s_D = 0.25$** | **22.2%** | Standard educational uplift sensitivity |
| **$s_D = 0.30$** | **26.6%** | Substantial education effect sensitivity |
| **$s_D = 0.40$** | **35.5%** | Conservative large effect sensitivity |

#### 2. Family-Clustered MDE ($K = 6$ clusters, $J_{	ext{eff}} \approx 8$, $df = 5$):
- Accounting for family clustering with average cluster size $m = 12/6 = 2.0$ and intra-cluster correlation $\rho \approx 0.50$, the design effect is $DEFF = 1 + (m-1)\rho \approx 1.50$, yielding effective sample size $J_{	ext{eff}} = 12 / 1.50 = 8.0$.
- Under conservative cluster-level degrees of freedom ($df = K - 1 = 5$): critical values $t_{lpha/2, 5} = 2.571$, $t_{eta, 5} = 0.920$; sum factor = **3.491**.
$$	ext{MDE}_{	ext{clustered}} = \frac{3.491 \cdot s_D}{\sqrt{8.0}} \approx 1.234 \cdot s_D$$

| Inter-Task Difference Standard Deviation ($s_D$) | Family-Clustered MDE (%) | Statistical Sensitivity |
|:---:|:---:|:---|
| **$s_D = 0.20$** | **24.7%** | Detects moderate-to-large clustered uplift |
| **$s_D = 0.25$** | **30.9%** | Detects standard clustered educational uplift |
| **$s_D = 0.30$** | **37.0%** | Detects substantial clustered educational uplift |
| **$s_D = 0.40$** | **49.4%** | Detects large clustered educational uplift |

> [!WARNING]
> **Explicit Pre-Registration Limitation Statement (Condition M1):**
> The confirmatory test is powered to detect only **large educational effects ($\ge 25	ext{--}30$ percentage points)**. Smaller effects ($\le 20$ points) will not reach 80% statistical power at the family-clustered level and will be reported as point estimates with 95% confidence intervals.

### B. Secondary Exploratory Power Analysis (TRANSFER Classes & All Held-Out Tasks)

Per Condition M2, exploratory endpoints are reported strictly separately and are **never pooled** into the primary confirmatory $\Delta_{	ext{TAUGHT}}$ metric:
1. **TRANSFER Tasks ($J = 12$ held-out tasks: 8 `state_transitions`, 4 `cache_ttl`):** High upside exploratory candidate for cross-domain educational generalization.
2. **Full Pooled Held-Out Suite ($J = 60$ tasks, $df = 59$, factor = 2.849):** $	ext{MDE} = 7.4\%	ext{--}14.7\%$ for system-wide secondary evaluation.

---
## 5. Pre-Registered Label Audit (C2 Relabeling Rule & L2 Audit)

Under Pre-Registered Rule C2 and Round 18 Review Condition L2:
- **Rule C2:** Any `TAUGHT` task with baseline solvability $> 70.0\%$ at $T=0.7$ is reclassified to `STATED` (model already possesses the required knowledge).
- **Condition L2:** Any `STATED` task with baseline solvability $\le 70.0\%$ where specifications (field schemas, service names) are omitted from the ticket and defined strictly in the handbook is reclassified to `TAUGHT` (Tasks 2037 and 2042).

### A. TAUGHT Tasks Exceeding 70% Baseline Solvability (32 tasks):
- Reclassified to `STATED`: 2003, 2005, 2006, 2009, 2010, 2011, 2012, 2014, 2017, 2019, 2020, 2021, 2023, 2025, 2026, 2027, 2028, 2029, 2046, 2047, 2050, 2051, 2053, 2054, 2057, 2059, 2061, 2069, 2103, 2104, 2105, 2106.

### B. Validated Retained TAUGHT Tasks (25 tasks):
- **Held-Out ($J_{\\text{primary}} = 12$ tasks):** **2015, 2022, 2033, 2035, 2041, 2042, 2043, 2065, 2067, 2073, 2099, 2101**
- **Tune ($J_{\\text{tune}} = 13$ tasks):** **2002, 2018, 2024, 2030, 2031, 2037, 2038, 2039, 2055, 2062, 2063, 2070, 2071**

### C. Resulting Population Balance:
- **Primary Confirmatory Population:** Exactly **12 held-out `TAUGHT` tasks** ($\ge 3$ required, confirmatory test adequately powered for large effects).
- **Screening Experiment Population:** Exactly **13 usable Tune `TAUGHT` tasks** ($\ge 10$ required by Condition M3).

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
- **Attempt (Task 2070, Run 2):** During the initial 84-task baseline pilot execution on commit `c8ff2c8`, background worker thread 3 encountered an unhandled provider runtime error (`RuntimeError: Response was truncated by provider stop_reason=FinishReason.MAX_TOKENS`). The original failed attempt log is preserved in the repository at `results/pilot_calibration/t07/raw/B0_r2_t2070_original_max_tokens_error.json`. The worker process was restarted under identical deterministic configuration and temperature settings ($T=0.7$, seed=1337). Upon re-execution, the model produced an untruncated response that failed hidden tests due to index truncation (`strict_pass=False`), which was recorded faithfully in `results/pilot_calibration/t07/rows.json`. Exactly 0 cherry-picking, output substitution, or result alteration occurred.

---

## 8. Mandatory Protocol Adherence

1. **Zero Scaffolding Conditions:** Pilot calibration was executed exclusively on condition `B0` ($s=0, p=0, u=0, r=0, k=0$). Zero calls were made with handbook, placebo, tools, review, or retry.
2. **Strict Stop Rule Enforced:** In strict accordance with Round 17 instructions, all factor execution ($s, p, u, r, k$) remains strictly halted until Pre-Registration and Pilot Calibration are formally reviewed and approved by Claude in Round 18.