# Pilot Calibration Report: Baseline B0 (`PILOT_CALIBRATION_REPORT.md`)

**Campaign Phase:** Pilot Calibration (Difficulty Calibration & Empirical Baseline Solvability Audit)  
**Model:** `gemini-2.5-flash` (`temperature=0.0`, `thinking_budget=2048`, `max_output_tokens=16384`)  
**Harness Condition:** Baseline B0 ONLY (single call; ticket + failing traceback excerpt + traceback file; no scaffolding)  
**Total Executed Attempts:** 140 / 140 (28 tasks $\times$ 5 runs)  
**Total Billed Tokens:** 284,629 tokens (Input: 57,440, Output: 55,568, Thinking: 171,621)  
**Total Actual Cost:** $0.0725 USD  
**Audit Status:** 100% Genuine Provider Responses Verified (0 mock, 0 simulated)  

---

## 1. Per-Task Empirical Baseline Strict-Pass Rate & Failure Modes

| Task ID | Task Name | Family | Class Tag | Split | Strict Passes | Pass Rate (%) | Primary Failure Mode |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| **2001** | Order Tax Calculation | `money_rounding` | `STATED` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2002** | Invoice Discount Allocation | `money_rounding` | `TAUGHT` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2003** | Multi-Currency Fee Conversion | `money_rounding` | `TAUGHT` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2004** | Legacy Payroll Tax Ceiling | `money_rounding` | `DISTRACTOR` | Held-Out | 5/5 | **100.0%** | None (100% pass) |
| **2005** | Tenant Routing Configuration | `config_merge` | `STATED` | Tune | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2006** | Database Pool Settings | `config_merge` | `TAUGHT` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2007** | Pipeline Step Definition | `config_merge` | `STATED` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2008** | Live Session State Accumulator | `config_merge` | `DISTRACTOR` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2009** | Billing Period Interval Calculator | `calendar_recurrence` | `STATED` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2010** | Subscription Active Window Evaluator | `calendar_recurrence` | `TAUGHT` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2011** | Maintenance Window Scheduler | `calendar_recurrence` | `STATED` | Held-Out | 5/5 | **100.0%** | None (100% pass) |
| **2012** | Audit Log Retention Window | `calendar_recurrence` | `TAUGHT` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2013** | Customer Profile CSV Exporter | `csv_roundtrip` | `STATED` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2014** | Order Item CSV Serializer | `csv_roundtrip` | `TAUGHT` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2015** | Batch Metric CSV Downloader | `csv_roundtrip` | `TAUGHT` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2016** | Shell TSV Command Log | `csv_roundtrip` | `DISTRACTOR` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2017** | API Route Authorization Guard | `permission_prefix` | `STATED` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2018** | Document Store RBAC Filter | `permission_prefix` | `TAUGHT` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2019** | Asset Storage Prefix Validator | `permission_prefix` | `STATED` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2020** | Webhook Subscription Scope Enforcer | `permission_prefix` | `TAUGHT` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2021** | Priority Job Queue Dispatcher | `event_ordering` | `STATED` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2022** | Notification Batch Sorter | `event_ordering` | `TAUGHT` | Held-Out | 5/5 | **100.0%** | None (100% pass) |
| **2023** | Task Scheduler Queue Rebalancer | `event_ordering` | `STATED` | Tune | 5/5 | **100.0%** | None (100% pass) |
| **2024** | Event Stream Ingestion Sequencer | `event_ordering` | `TAUGHT` | Tune | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2025** | In-Memory Token Cache | `cache_ttl` | `TRANSFER` | Held-Out | 5/5 | **100.0%** | None (100% pass) |
| **2026** | API Rate Limit Session Store | `cache_ttl` | `TRANSFER` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2027** | Distributed Lease Expiry Guard | `cache_ttl` | `TRANSFER` | Held-Out | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2028** | DNS Cache TTL Resolver | `cache_ttl` | `TRANSFER` | Held-Out | 5/5 | **100.0%** | None (100% pass) |

---

## 2. Per-Class and Per-Split Baseline Performance

### A. By Task Class

| Class Tag | Strict Passes | Total Attempts | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|
| **`STATED`** | 32/50 | 50 | **64.0%** | [50.1%, 75.9%] |
| **`TAUGHT`** | 15/55 | 55 | **27.3%** | [17.3%, 40.2%] |
| **`DISTRACTOR`** | 5/15 | 15 | **33.3%** | [15.2%, 58.3%] |
| **`TRANSFER`** | 10/20 | 20 | **50.0%** | [29.9%, 70.1%] |

### B. By Partition Split

| Partition Split | Tasks | Total Attempts | Strict Passes | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tune** | 15 | 75 | 37/75 | **49.3%** | [38.3%, 60.4%] |
| **Held-Out** | 13 | 65 | 25/65 | **38.5%** | [27.6%, 50.6%] |

### C. Class $\times$ Split Interaction

| Class Tag | Split | Passes / Total | Pass Rate (%) | Wilson 95% CI |
|:---|:---:|:---:|:---:|:---:|
| `STATED` | Tune | 27/35 | **77.1%** | [61.0%, 87.9%] |
| `STATED` | Held-Out | 5/15 | **33.3%** | [15.2%, 58.3%] |
| `TAUGHT` | Tune | 10/35 | **28.6%** | [16.3%, 45.1%] |
| `TAUGHT` | Held-Out | 5/20 | **25.0%** | [11.2%, 46.9%] |
| `DISTRACTOR` | Tune | 0/5 | **0.0%** | [0.0%, 43.4%] |
| `DISTRACTOR` | Held-Out | 5/10 | **50.0%** | [23.7%, 76.3%] |
| `TRANSFER` | Held-Out | 10/20 | **50.0%** | [29.9%, 70.1%] |

---

## 3. Run-to-Run Noise Estimate & Power Analysis

- **Between-Task Variance ($\sigma^2_{\text{between}}$):** `0.2470`
- **Mean Within-Task Variance across Repeats ($\sigma^2_{\text{within}}$):** `0.0086`
- **Total Variance ($\sigma^2_{\text{total}}$):** `0.2556`
- **Intraclass Correlation (ICC = $\frac{\sigma^2_{\text{between}}}{\sigma^2_{\text{total}}}$):** `0.966`  
  - *Interpretation:* 96.6% of total outcome variance is driven by inherent task differences, while 3.4% is run-to-run sampling noise.
- **Required Sample Size for Confirmatory Power:**
  - Target Effect Size: $\Delta = 15.0\%$ percentage points
  - Statistical Power: $1 - \beta = 80\%$ (at $\alpha = 0.05$, two-tailed)
  - Formula: $n = \frac{2 (z_{\alpha/2} + z_{\beta})^2 \sigma^2_{\text{within}}}{\Delta^2} = \frac{2 (1.96 + 0.842)^2 (0.0086)}{(0.15)^2}$
  - **Recommended Runs Per Cell:** **$n \ge 6$ runs** per cell/task combination.

---

## 4. Pre-Registered Label Audit (C2 Relabeling Rule)

> [!IMPORTANT]
> **Pre-Registered Rule:** Any task initially designated `TAUGHT` where the empirical baseline pass rate in Pilot Calibration exceeds **70.0%** is objectively solvable without handbook intervention and must be reclassified as `STATED`, dropping it from the primary confirmatory `TAUGHT` hypothesis count.

### A. TAUGHT Tasks Exceeding 70% Baseline Solvability (3 tasks):

- **Task 2014 (Order Item CSV Serializer, `csv_roundtrip`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2018 (Document Store RBAC Filter, `permission_prefix`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2022 (Notification Batch Sorter, `event_ordering`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**

### B. Validated Retained TAUGHT Tasks (8 tasks):

- **Task 2002 (Invoice Discount Allocation, `money_rounding`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2003 (Multi-Currency Fee Conversion, `money_rounding`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2006 (Database Pool Settings, `config_merge`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2010 (Subscription Active Window Evaluator, `calendar_recurrence`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2012 (Audit Log Retention Window, `calendar_recurrence`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2015 (Batch Metric CSV Downloader, `csv_roundtrip`, Held-Out):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2020 (Webhook Subscription Scope Enforcer, `permission_prefix`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2024 (Event Stream Ingestion Sequencer, `event_ordering`, Tune):** Baseline Pass Rate = **0.0%** (0/5)

### C. Resulting Held-Out TAUGHT Count:
- **Held-Out TAUGHT Tasks Retained:** **3** (Tasks: 2003, 2010, 2015)
- **Confirmatory Power Status:** **CONFIRMATORY_VALID** (Threshold: $\ge 3$ required for confirmatory test).

---

## 5. Difficulty Audit: Floor and Ceiling Tasks

Per protocol, tasks with baseline solvability $> 85\%$ (too easy / ceiling) or $< 15\%$ (too hard / floor) are flagged below for reviewer editorial determination (none removed automatically):

- **Ceiling Tasks (> 85% Baseline Pass Rate, n=12):**
  - **Task 2004 (Legacy Payroll Tax Ceiling, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2009 (Billing Period Interval Calculator, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2011 (Maintenance Window Scheduler, `STATED`, Held-Out):** 100.0% (5/5)
  - **Task 2013 (Customer Profile CSV Exporter, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2014 (Order Item CSV Serializer, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2017 (API Route Authorization Guard, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2018 (Document Store RBAC Filter, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2021 (Priority Job Queue Dispatcher, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2022 (Notification Batch Sorter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2023 (Task Scheduler Queue Rebalancer, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2025 (In-Memory Token Cache, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2028 (DNS Cache TTL Resolver, `TRANSFER`, Held-Out):** 100.0% (5/5)
- **Floor Tasks (< 15% Baseline Pass Rate, n=15):**
  - **Task 2001 (Order Tax Calculation, `STATED`, Tune):** 0.0% (0/5)
  - **Task 2002 (Invoice Discount Allocation, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2003 (Multi-Currency Fee Conversion, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2006 (Database Pool Settings, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2007 (Pipeline Step Definition, `STATED`, Held-Out):** 0.0% (0/5)
  - **Task 2008 (Live Session State Accumulator, `DISTRACTOR`, Tune):** 0.0% (0/5)
  - **Task 2010 (Subscription Active Window Evaluator, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2012 (Audit Log Retention Window, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2015 (Batch Metric CSV Downloader, `TAUGHT`, Held-Out):** 0.0% (0/5)
  - **Task 2016 (Shell TSV Command Log, `DISTRACTOR`, Held-Out):** 0.0% (0/5)
  - **Task 2019 (Asset Storage Prefix Validator, `STATED`, Held-Out):** 0.0% (0/5)
  - **Task 2020 (Webhook Subscription Scope Enforcer, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2024 (Event Stream Ingestion Sequencer, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2026 (API Rate Limit Session Store, `TRANSFER`, Held-Out):** 0.0% (0/5)
  - **Task 2027 (Distributed Lease Expiry Guard, `TRANSFER`, Held-Out):** 0.0% (0/5)
- **Calibrated Range Tasks (15% - 85% Baseline Pass Rate, n=1):**
  - **1 / 28 tasks (3.6%)** fall strictly within the desired calibration band.

---

## 6. Execution Integrity & Audit Verification

| Integrity Metric | Requirement | Measured Value | Compliance |
|:---|:---|:---:|:---:|
| **Truncation Count** | 0 responses cut off | **0** | **PASS** |
| **API / Provider Errors** | 0 unhandled fatal errors | **0** | **PASS** |
| **Retries in B0** | Exactly 0 retries | **0** | **PASS** |
| **Protected File Modifications** | Recorded if attempted | **0** | **PASS** |
| **Turn Count** | Single call per attempt | **100% Turn 1** | **PASS** |
| **Billed Tokens Accounting** | Exact provider token usage | **284,629 tokens** | **PASS** |
| **Financial Cost** | Tracked vs credit budget | **$0.0725 USD** | **PASS** |

---

## 7. Mandatory Protocol Adherence

1. **Zero Scaffolding Conditions:** Pilot calibration was executed exclusively on condition `B0` ($s=0, p=0, u=0, r=0, k=0$). Zero calls were made with handbook, placebo, tools, review, or retry.
2. **Strict Stop Rule Enforced:** In strict accordance with Round 12 instructions, all execution halts upon completion of this report. No factor conditions will be evaluated until Pre-Registration is formally approved in Round 13.