# Pilot Calibration Report: Baseline B0 (Round 17 Suite Expansion, `PILOT_CALIBRATION_REPORT.md`)

**Campaign Phase:** Pilot Calibration (Difficulty Calibration & Empirical Baseline Solvability Audit)  
**Model:** `gemini-2.5-flash` (`thinking_budget=2048`, `max_output_tokens=16384`)  
**Harness Condition:** Redefined Baseline B0 (ALL non-test source files + visible tests in context; ticket + failing traceback excerpt; single call; no scaffolding; final anti-tamper envelope)  
**Total Executed Attempts:** 504 attempts (84 at T=0.0, 420 at T=0.7 across 5 runs)  
**Total Billed Tokens:** 1,362,999 tokens (Input: 433,806, Output: 223,601, Thinking: 705,592)  
**Total Cost:** $0.3113 USD  
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

---

## 2. Per-Class and Per-Split Baseline Performance

### A. By Initial Task Class (T=0.7, 5 Repeats)

| Class Tag | Strict Passes | Total Attempts | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|
| **`STATED`** | 83/105 | 105 | **79.0%** | [70.3%, 85.7%] |
| **`TAUGHT`** | 74/175 | 175 | **42.3%** | [35.2%, 49.7%] |
| **`DISTRACTOR`** | 64/80 | 80 | **80.0%** | [70.0%, 87.3%] |
| **`TRANSFER`** | 20/60 | 60 | **33.3%** | [22.7%, 45.9%] |

### B. By Partition Split (T=0.7, 5 Repeats)

| Partition Split | Tasks | Total Attempts | Strict Passes | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tune** | 42 | 210 | 135/210 | **64.3%** | [57.6%, 70.5%] |
| **Held-Out** | 42 | 210 | 106/210 | **50.5%** | [43.8%, 57.2%] |

### C. Comparison between T=0.0 (Deterministic Single) and T=0.7 (Repeats)

| Metric | T=0.0 (Single Run, 84 Tasks) | T=0.7 (5 Repeats, 420 Attempts) |
|:---|:---:|:---:|
| **Overall Strict Pass Rate** | 50/84 (**59.5%**) | 241/420 (**57.4%**) |
| **Tune Split Pass Rate** | 27/42 (**64.3%**) | 135/210 (**64.3%**) |
| **Held-Out Split Pass Rate** | 23/42 (**54.8%**) | 106/210 (**50.5%**) |

---

## 3. Qualitative Diagnoses of Specific Baseline Results (E4)

- **Task 2002 (Invoice Discount Allocation, `TAUGHT`, 0% pass):** *Diagnosis:* The unassisted model uses Python's default banker's rounding (`ROUND_HALF_EVEN`) or floating-point truncation, directly failing the house-mandated `ROUND_HALF_UP` specification required by Handbook Rule H02.
- **Task 2037 / 2042 (Audit / Order Wire Dispatcher, `STATED`, 0% pass):** *Diagnosis:* The ticket reported wire dispatch payload corruption; unassisted models fixed payload serializations but failed to wrap payloads in the house wire envelope schema (`_v: 2`, `trace_id`, `data`), which was not explicitly stated in the bug report.
- **Task 2062 / 2065 (Order RPC / Customer Refund, `TAUGHT`, 0% pass):** *Diagnosis:* Unassisted models generated network retry loops or token refreshes without injecting the house `Idempotency-Key` UUID header mandated by Rule H13.
- **Tasks 2077–2084 (State Transition Lifecycle Family, `TRANSFER`, 0% pass):** *Diagnosis:* Unassisted models implemented direct status jumps (e.g., `DRAFT -> ACTIVE` or `PENDING -> DEPLOYED`) without honoring the house state-machine lifecycle (`DRAFT -> PENDING_REVIEW -> APPROVED -> DEPLOYING -> LIVE`), confirming that Rule H15 constitutes a genuine transfer test.

---

## 4. Run-to-Run Noise Estimate & Paired-by-Task Power Analysis (E5)

- **Between-Task Variance ($\sigma^2_{\text{between}}$):** `0.1945`
- **Mean Within-Task Variance across Repeats at T=0.7 ($\sigma^2_{\text{within}}$):** `0.0524`
- **Total Variance ($\sigma^2_{\text{total}}$):** `0.2469`
- **Intraclass Correlation (ICC):** `0.788`  
  - *Interpretation:* Sampling at $T=0.7$ introduces genuine within-task stochasticity (within-task variance = `0.0524`).

### Paired-by-Task Power Analysis (J = 42 Held-Out Tasks):

In a paired comparison across $J = 42$ held-out tasks ($D_j = Y_{\theta^*, j} - Y_{0, j}$, $df = 41$, $\alpha = 0.05$ two-tailed, $1 - \beta = 0.80$):

$$\text{MDE} = \frac{(t_{\alpha/2} + t_{\beta}) \cdot s_D}{\sqrt{J}} = \frac{2.862 \cdot s_D}{\sqrt{42}} \approx 0.442 \cdot s_D$$

- **Minimum Detectable Effect (MDE) by response variation:**
  - If $s_D = 0.20$ (low cross-task response variance): $\text{MDE} = **8.8\%**$
  - If $s_D = 0.30$ (moderate cross-task response variance): $\text{MDE} = **13.2\%**$
  - If $s_D = 0.40$ (high cross-task response variance): $\text{MDE} = **17.7\%**$
- **Power Assessment:** With $J = 42$ held-out tasks, the minimum detectable effect size at $s_D = 0.30$ is **13.2 percentage points** (well within the $\le 15.0$ percentage point target). The confirmatory study is adequately powered.

---

## 5. Pre-Registered Label Audit (C2 Relabeling Rule on T=0.7)

> [!IMPORTANT]
> **Pre-Registered Rule:** Any task initially designated `TAUGHT` where the empirical baseline pass rate at T=0.7 exceeds **70.0%** is objectively solvable without handbook intervention and must be reclassified as `STATED`, dropping it from the primary confirmatory `TAUGHT` hypothesis count.

### A. TAUGHT Tasks Exceeding 70% Baseline Solvability (14 tasks):

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

### B. Validated Retained TAUGHT Tasks (21 tasks):

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

### C. Resulting Held-Out TAUGHT Count:
- **Held-Out TAUGHT Tasks Retained:** **9** (Tasks: 2015, 2022, 2033, 2035, 2041, 2043, 2065, 2067, 2073)
- **Confirmatory Power Status:** **CONFIRMATORY_VALID** (Threshold: $\ge 3$ required for confirmatory test).

---

## 6. Difficulty Audit: Floor and Ceiling Tasks (E3)

Per protocol, tasks with baseline solvability $> 85\%$ (ceiling) or $< 15\%$ (floor) are flagged below:

- **Ceiling Tasks (> 85% Baseline Pass Rate at T=0.7, n=35):**
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
- **Calibrated Range Tasks (15% - 85% Baseline Pass Rate at T=0.7, n=23):**
  - **23 / 84 tasks (27.4%)** fall within the intermediate calibration band.
  - **Pre-Registered Rule Evaluation:** PASSED (>= 8 tasks in calibrated range).

---

## 7. Execution Integrity & Audit Verification

| Integrity Metric | Requirement | Measured Value | Compliance |
|:---|:---|:---:|:---:|
| **Truncation Count** | 0 responses cut off | **0** | **PASS** |
| **API / Provider Errors** | 0 unhandled fatal errors | **0** | **PASS** |
| **Retries in B0** | Exactly 0 retries | **0** | **PASS** |
| **Protected File Modifications** | Recorded if attempted | **1** | **PASS** |
| **Turn Count** | Single call per attempt | **100% Turn 1** | **PASS** |
| **Billed Tokens Accounting** | Exact provider token usage | **1,362,999 tokens** | **PASS** |
| **Financial Cost** | Tracked vs credit budget | **$0.3113 USD** | **PASS** |

---

## 8. Mandatory Protocol Adherence

1. **Zero Scaffolding Conditions:** Pilot calibration was executed exclusively on condition `B0` ($s=0, p=0, u=0, r=0, k=0$). Zero calls were made with handbook, placebo, tools, review, or retry.
2. **Strict Stop Rule Enforced:** In strict accordance with Round 16 instructions, all factor execution ($s, p, u, r, k$) remains strictly halted until Pre-Registration and Pilot Calibration are formally reviewed and approved by Claude in Round 17.