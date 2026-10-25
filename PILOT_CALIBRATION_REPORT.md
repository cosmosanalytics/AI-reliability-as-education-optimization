# Pilot Calibration Report: Baseline B0 (Round 13 Re-run, `PILOT_CALIBRATION_REPORT.md`)

**Campaign Phase:** Pilot Calibration (Difficulty Calibration & Empirical Baseline Solvability Audit)  
**Model:** `gemini-2.5-flash` (`thinking_budget=2048`, `max_output_tokens=16384`)  
**Harness Condition:** Redefined Baseline B0 (Round 13 E1: ALL non-test source files + visible tests in context; ticket + failing traceback excerpt; single call; no scaffolding)  
**Total Executed Attempts:** 168 attempts (28 at T=0.0, 140 at T=0.7 across 5 runs)  
**Total Billed Tokens:** 424,972 tokens (Input: 136,356, Output: 65,241, Thinking: 223,375)  
**Total Cost:** $0.0968 USD  
**Audit Status:** 100% Genuine Live Model Responses (0 mock, 0 simulated)  

---

## 1. Per-Task Empirical Baseline Strict-Pass Rate (E2)

| Task ID | Task Name | Family | Initial Class | Split | HRC | VTS | T=0.0 Pass | T=0.7 Passes | T=0.7 Rate (%) | Primary Failure Mode (T=0.7) |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **2001** | Order Tax Calculation | `money_rounding` | `STATED` | Tune | Yes | No | 1/1 | 2/5 | **40.0%** | protected_mod (2/3) |
| **2002** | Invoice Discount Allocation | `money_rounding` | `TAUGHT` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (3/5) |
| **2003** | Multi-Currency Fee Conversion | `money_rounding` | `TAUGHT` | Held-Out | Yes | No | 0/1 | 1/5 | **20.0%** | wrong_fix (4/4) |
| **2004** | Legacy Payroll Tax Ceiling | `money_rounding` | `DISTRACTOR` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2005** | Tenant Routing Configuration | `config_merge` | `STATED` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | protected_mod (5/5) |
| **2006** | Database Pool Settings | `config_merge` | `TAUGHT` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2007** | Pipeline Step Definition | `config_merge` | `STATED` | Held-Out | Yes | No | 0/1 | 2/5 | **40.0%** | wrong_fix (3/3) |
| **2008** | Live Session State Accumulator | `config_merge` | `DISTRACTOR` | Tune | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2009** | Billing Period Interval Calculator | `calendar_recurrence` | `STATED` | Tune | No | No | 1/1 | 4/5 | **80.0%** | protected_mod (1/1) |
| **2010** | Subscription Active Window Evaluator | `calendar_recurrence` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2011** | Maintenance Window Scheduler | `calendar_recurrence` | `STATED` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2012** | Audit Log Retention Window | `calendar_recurrence` | `TAUGHT` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2013** | Customer Profile CSV Exporter | `csv_roundtrip` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2014** | Order Item CSV Serializer | `csv_roundtrip` | `TAUGHT` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2015** | Batch Metric CSV Downloader | `csv_roundtrip` | `TAUGHT` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2016** | Shell TSV Command Log | `csv_roundtrip` | `DISTRACTOR` | Held-Out | No | Yes | 0/1 | 0/5 | **0.0%** | wrong_fix (5/5) |
| **2017** | API Route Authorization Guard | `permission_prefix` | `STATED` | Tune | No | Yes | 1/1 | 0/5 | **0.0%** | protected_mod (4/5) |
| **2018** | Document Store RBAC Filter | `permission_prefix` | `TAUGHT` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2019** | Asset Storage Prefix Validator | `permission_prefix` | `STATED` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2020** | Webhook Subscription Scope Enforcer | `permission_prefix` | `TAUGHT` | Tune | Yes | No | 0/1 | 0/5 | **0.0%** | wrong_fix (3/5) |
| **2021** | Priority Job Queue Dispatcher | `event_ordering` | `STATED` | Tune | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2022** | Notification Batch Sorter | `event_ordering` | `TAUGHT` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2023** | Task Scheduler Queue Rebalancer | `event_ordering` | `STATED` | Tune | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2024** | Event Stream Ingestion Sequencer | `event_ordering` | `TAUGHT` | Tune | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2025** | In-Memory Token Cache | `cache_ttl` | `TRANSFER` | Held-Out | No | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2026** | API Rate Limit Session Store | `cache_ttl` | `TRANSFER` | Held-Out | Yes | No | 1/1 | 4/5 | **80.0%** | wrong_fix (1/1) |
| **2027** | Distributed Lease Expiry Guard | `cache_ttl` | `TRANSFER` | Held-Out | Yes | No | 1/1 | 5/5 | **100.0%** | None (100% pass) |
| **2028** | DNS Cache TTL Resolver | `cache_ttl` | `TRANSFER` | Held-Out | No | Yes | 1/1 | 5/5 | **100.0%** | None (100% pass) |

---

## 2. Per-Class and Per-Split Baseline Performance

### A. By Initial Task Class (T=0.7, 5 Repeats)

| Class Tag | Strict Passes | Total Attempts | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|
| **`STATED`** | 32/50 | 50 | **64.0%** | [50.1%, 75.9%] |
| **`TAUGHT`** | 41/55 | 55 | **74.5%** | [61.7%, 84.2%] |
| **`DISTRACTOR`** | 5/15 | 15 | **33.3%** | [15.2%, 58.3%] |
| **`TRANSFER`** | 19/20 | 20 | **95.0%** | [76.4%, 99.1%] |

### B. By Partition Split (T=0.7, 5 Repeats)

| Partition Split | Tasks | Total Attempts | Strict Passes | Mean Strict Pass (%) | Wilson 95% Confidence Interval |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tune** | 15 | 75 | 46/75 | **61.3%** | [50.0%, 71.5%] |
| **Held-Out** | 13 | 65 | 51/65 | **78.5%** | [67.0%, 86.7%] |

### C. Comparison between T=0.0 (Deterministic Single) and T=0.7 (Repeats)

| Metric | T=0.0 (Single Run, 28 Tasks) | T=0.7 (5 Repeats, 140 Attempts) |
|:---|:---:|:---:|
| **Overall Strict Pass Rate** | 21/28 (**75.0%**) | 97/140 (**69.3%**) |
| **Tune Split Pass Rate** | 11/15 (**73.3%**) | 46/75 (**61.3%**) |
| **Held-Out Split Pass Rate** | 10/13 (**76.9%**) | 51/65 (**78.5%**) |

---

## 3. Qualitative Diagnoses of Specific Odd Results (E4)

- **Task 2001 (Order Tax Calculation, `STATED`, 0% pass):** *Diagnosis:* The docstring in `pricing.py` explicitly specifies banker's rounding, but the ticket reported 'line item discount calculation produces fractional cent rounding errors'. The model attempted to recalculate tax per item in `pricing.py` instead of fixing `tax_engine.py` (which housed the actual rounding bug in `calculate_vat`). With full repository context under redefined B0, the model can inspect `tax_engine.py` directly.
- **Task 2004 (Legacy Payroll Tax Ceiling, `DISTRACTOR`, 100% pass):** *Diagnosis:* In Baseline B0, no handbook is provided, so the agent experiences zero distraction. The local docstring explicitly mandates ceiling rounding (`MUST round fractional cents UP ... Do NOT use banker's rounding`), and the unassisted model correctly followed the local specification directly.
- **Task 2008 (Live Session State Accumulator, `DISTRACTOR`, 0% pass):** *Diagnosis:* The model attempted in-place mutation using shallow `.update(deltas)` on the top-level dictionary, which overwrote nested mapping keys (`counters`) rather than performing a recursive dictionary update, failing the hidden nested-identity contract.
- **Task 2016 (Shell TSV Command Log, `DISTRACTOR`, 0% pass):** *Diagnosis:* The model correctly implemented backslash escaping (`replace('"', '\"')`) and tab delimiters per the docstring, but the hidden test assertion in `test_cmd_log_cases.py` used an unescaped single-quoted string literal (`'3\techo \"hello\"'` evaluating to `'3\techo "hello"'`), creating an over-strict string-literal mismatch.

---

## 4. Run-to-Run Noise Estimate & Paired-by-Task Power Analysis (E5)

- **Between-Task Variance ($\sigma^2_{\text{between}}$):** `0.1792`
- **Mean Within-Task Variance across Repeats at T=0.7 ($\sigma^2_{\text{within}}$):** `0.0400`
- **Total Variance ($\sigma^2_{\text{total}}$):** `0.2192`
- **Intraclass Correlation (ICC):** `0.818`  
  - *Interpretation:* Sampling at $T=0.7$ introduces genuine within-task stochasticity (within-task variance = `0.0400`).

### Paired-by-Task Power Analysis (J = 13 Held-Out Tasks):

In a paired comparison across $J = 13$ held-out tasks ($D_j = Y_{\theta^*, j} - Y_{0, j}$, $df = 12$, $\alpha = 0.05$ two-tailed, $t_{\alpha/2} = 2.179$, $1 - \beta = 0.80$, $t_{\beta} = 0.873$):

$$\text{MDE} = \frac{(t_{\alpha/2} + t_{\beta}) \cdot s_D}{\sqrt{J}} = \frac{3.052 \cdot s_D}{\sqrt{13}} \approx 0.846 \cdot s_D$$

- **Minimum Detectable Effect (MDE) by response variation:**
  - If $s_D = 0.20$ (low cross-task response variance): $\text{MDE} = **16.9\%**$
  - If $s_D = 0.30$ (moderate cross-task response variance): $\text{MDE} = **25.4\%**$
  - If $s_D = 0.40$ (high cross-task response variance): $\text{MDE} = **33.9\%**$
- **Plain Reality Assessment:** With $J = 13$ held-out tasks, the minimum detectable effect size is approximately **25.4 percentage points**. If the expected educational scaffolding benefit is $+15.0$ percentage points, a 13-task held-out study is **modestly underpowered** unless task-to-task response variance is small ($s_D \le 0.177$). To reliably detect a $+15.0$ percentage point effect at $s_D = 0.30$, a sample size of **$J \ge 38$ tasks** would be required.

---

## 5. Pre-Registered Label Audit (C2 Relabeling Rule on T=0.7)

> [!IMPORTANT]
> **Pre-Registered Rule:** Any task initially designated `TAUGHT` where the empirical baseline pass rate at T=0.7 exceeds **70.0%** is objectively solvable without handbook intervention and must be reclassified as `STATED`, dropping it from the primary confirmatory `TAUGHT` hypothesis count.

### A. TAUGHT Tasks Exceeding 70% Baseline Solvability (8 tasks):

- **Task 2006 (Database Pool Settings, `config_merge`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2010 (Subscription Active Window Evaluator, `calendar_recurrence`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2012 (Audit Log Retention Window, `calendar_recurrence`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2014 (Order Item CSV Serializer, `csv_roundtrip`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2015 (Batch Metric CSV Downloader, `csv_roundtrip`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2018 (Document Store RBAC Filter, `permission_prefix`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2022 (Notification Batch Sorter, `event_ordering`, Held-Out):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**
- **Task 2024 (Event Stream Ingestion Sequencer, `event_ordering`, Tune):** Baseline Pass Rate = **100.0%** (5/5) -> **RECLASSIFIED TO `STATED`**

### B. Validated Retained TAUGHT Tasks (3 tasks):

- **Task 2002 (Invoice Discount Allocation, `money_rounding`, Tune):** Baseline Pass Rate = **0.0%** (0/5)
- **Task 2003 (Multi-Currency Fee Conversion, `money_rounding`, Held-Out):** Baseline Pass Rate = **20.0%** (1/5)
- **Task 2020 (Webhook Subscription Scope Enforcer, `permission_prefix`, Tune):** Baseline Pass Rate = **0.0%** (0/5)

### C. Resulting Held-Out TAUGHT Count:
- **Held-Out TAUGHT Tasks Retained:** **1** (Tasks: 2003)
- **Confirmatory Power Status:** **EXPLORATORY** (Threshold: $\ge 3$ required for confirmatory test).

---

## 6. Difficulty Audit: Floor and Ceiling Tasks (E3)

Per protocol, tasks with baseline solvability $> 85\%$ (ceiling) or $< 15\%$ (floor) are flagged below:

- **Ceiling Tasks (> 85% Baseline Pass Rate at T=0.7, n=16):**
  - **Task 2004 (Legacy Payroll Tax Ceiling, `DISTRACTOR`, Held-Out):** 100.0% (5/5)
  - **Task 2006 (Database Pool Settings, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2010 (Subscription Active Window Evaluator, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2011 (Maintenance Window Scheduler, `STATED`, Held-Out):** 100.0% (5/5)
  - **Task 2012 (Audit Log Retention Window, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2013 (Customer Profile CSV Exporter, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2014 (Order Item CSV Serializer, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2015 (Batch Metric CSV Downloader, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2018 (Document Store RBAC Filter, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2021 (Priority Job Queue Dispatcher, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2022 (Notification Batch Sorter, `TAUGHT`, Held-Out):** 100.0% (5/5)
  - **Task 2023 (Task Scheduler Queue Rebalancer, `STATED`, Tune):** 100.0% (5/5)
  - **Task 2024 (Event Stream Ingestion Sequencer, `TAUGHT`, Tune):** 100.0% (5/5)
  - **Task 2025 (In-Memory Token Cache, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2027 (Distributed Lease Expiry Guard, `TRANSFER`, Held-Out):** 100.0% (5/5)
  - **Task 2028 (DNS Cache TTL Resolver, `TRANSFER`, Held-Out):** 100.0% (5/5)
- **Floor Tasks (< 15% Baseline Pass Rate at T=0.7, n=6):**
  - **Task 2002 (Invoice Discount Allocation, `TAUGHT`, Tune):** 0.0% (0/5)
  - **Task 2005 (Tenant Routing Configuration, `STATED`, Tune):** 0.0% (0/5)
  - **Task 2008 (Live Session State Accumulator, `DISTRACTOR`, Tune):** 0.0% (0/5)
  - **Task 2016 (Shell TSV Command Log, `DISTRACTOR`, Held-Out):** 0.0% (0/5)
  - **Task 2017 (API Route Authorization Guard, `STATED`, Tune):** 0.0% (0/5)
  - **Task 2020 (Webhook Subscription Scope Enforcer, `TAUGHT`, Tune):** 0.0% (0/5)
- **Calibrated Range Tasks (15% - 85% Baseline Pass Rate at T=0.7, n=6):**
  - **6 / 28 tasks (21.4%)** fall within the intermediate calibration band.
  - **Pre-Registered Rule (E3) Evaluation:** TRIGGERED (< 8 tasks in calibrated range; requires suite expansion or prompt adjustment per reviewer determination).

---

## 7. Execution Integrity & Audit Verification

| Integrity Metric | Requirement | Measured Value | Compliance |
|:---|:---|:---:|:---:|
| **Truncation Count** | 0 responses cut off | **0** | **PASS** |
| **API / Provider Errors** | 0 unhandled fatal errors | **0** | **PASS** |
| **Retries in B0** | Exactly 0 retries | **0** | **PASS** |
| **Protected File Modifications** | Recorded if attempted | **17** | **PASS** |
| **Turn Count** | Single call per attempt | **100% Turn 1** | **PASS** |
| **Billed Tokens Accounting** | Exact provider token usage | **424,972 tokens** | **PASS** |
| **Financial Cost** | Tracked vs credit budget | **$0.0968 USD** | **PASS** |

---

## 8. Mandatory Protocol Adherence

1. **Zero Scaffolding Conditions:** Pilot calibration was executed exclusively on condition `B0` ($s=0, p=0, u=0, r=0, k=0$). Zero calls were made with handbook, placebo, tools, review, or retry.
2. **Strict Stop Rule Enforced:** In strict accordance with Round 13 instructions, all execution halts upon completion of this report. No factor conditions will be evaluated until Pre-Registration is formally approved in Round 14.