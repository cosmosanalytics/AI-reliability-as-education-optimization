# Phase 3 Factorial Screening (Screening A) — Exploratory Report

**Evaluation of Generic Process Book (W01–W16) & Generic Examples (Not Pre-Registered Handbook)**

- **Generated:** 2026-10-25 22:02:28 UTC (Amended 2026-10-25 22:45:00 UTC per Round 25 Review)  
- **Design:** $2^{5-1}$ Fractional Factorial (Resolution V, Defining Relation $I = spurk$)  
- **Scope:** Tune Task Split (46 Tasks across 14 Bug Families)  
- **Execution Status:** 2,208 / 2,208 attempts (100.0% completed)  
- **Financial Audit:** $22.7661 USD spent (60.1% of $37.85 USD cap)  
- **Commit:** [`bc9b326`](https://github.com/cosmosanalytics/AI-reliability-as-education-optimization/commit/bc9b326)

---

> [!WARNING]
> ### Critical Audit Finding & Data Relabeling Disclosure (Round 25 Review Finding B1)
> **The screening result from Screening A is NOT accepted for $\theta^*$ selection. Confirmatory Phase 4 is NOT authorized.**
> 
> In Round 25 Review, inspection of the 2,208 attempt transcripts revealed that the 16 cell brief files (`briefs/C*.md`) utilized during this run were legacy briefs dating from Phase 0 (2026-10-24). Specifically:
> 1. Factor $s=1$ briefs contained a generic **PROCESS BOOK (Rules W01–W16)** ("read the whole issue", "make the smallest change", etc.), and contained **zero** codified house-convention rules (Rules H01–H16 such as monetary rounding, wire envelope, or `ERR_RESOURCE_LOCKED`).
> 2. Factor $p=1$ briefs contained generic worked examples (`parse_duration`), rather than the pre-registered `briefs/P3.md` practice brief.
> 
> **Data Status:** All 2,208 executed rows ($22.77 USD) are real empirical data and are preserved under `results/screening/`. However, they are honestly re-labeled as **"Screening A: Generic Process Book and Generic Worked Examples"**. 
> 
> **Scientific Finding:** None of the five factor main effects is distinguishable from zero (effects range from -1.81 pp to +1.63 pp; all 95% confidence intervals include zero). Generic process advice provides no detectable accuracy benefit on software engineering repair tasks. This campaign did not test the codified handbook hypothesis.

---

## 1. Executive Summary & Exploratory Candidate Cell

- **Best Observed Empirical Cell in Screening A:** `C0101` ($s=0, p=1, u=0, r=1, k=1$)  
- **Calibrated Tune Pass Rate:** **76.9%** (30 / 39 attempts, Wilson 95% CI: [61.7%, 87.4%])  
- **Cognitive Load ($\sum x_i$):** **3** active interventions  
- **Token Cost Efficiency (Calibrated Tasks):** **11,519 billed tokens / pass** (30 passes on 13 calibrated Tune tasks)  
- **Token Cost Efficiency (All Tune Tasks):** **11,696 billed tokens / pass** (101 passes on all 46 Tune tasks) *(Reconciled per Reviewer Item R1)*  

> [!NOTE]
> **Winner's Curse Disclosure (Reviewer Item R3):**  
> Cell `C0101` (73.2% overall) is only 2.9 percentage points above the lightest baseline-like cell `C0000` (70.3%), with heavily overlapping confidence intervals ([65.2%, 79.9%] vs [62.2%, 77.3%]). In an experiment across 16 noisy cells subject to between-task variance, selecting the maximum cell inevitably captures stochastic noise. `C0101` is designated strictly as the "best observed empirical cell" under generic advice, not a proven winning architecture.

---

## 2. 16-Cell Factorial Performance Table ($N=138$ per cell)

*Note: In Screening A, factor $s$ indicates the generic Process Book (W01–W16), and factor $p$ indicates generic worked examples.*

| Cell | $s$ | $p$ | $u$ | $r$ | $k$ | Attempts | Passes | Strict Pass Rate (%) | Std Error | Wilson 95% CI | Mean Tokens In | Mean Tokens Out | Mean Thinking | Mean Billed | Mean Cost ($) | Tokens / Pass |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0000** | 0 | 0 | 0 | 0 | 1 | 138 | 97 | **70.3%** | 3.9% | [62.2%, 77.3%] | 975 | 449 | 1,457 | 2,881 | $0.0051 | 4,099 |
| **C0001** | 0 | 0 | 0 | 1 | 0 | 138 | 95 | **68.8%** | 3.9% | [60.7%, 76.0%] | 2,459 | 710 | 2,680 | 5,850 | $0.0092 | 8,498 |
| **C0010** | 0 | 0 | 1 | 0 | 0 | 138 | 92 | **66.7%** | 4.0% | [58.4%, 74.0%] | 2,636 | 594 | 2,597 | 5,827 | $0.0088 | 8,741 |
| **C0011** | 0 | 0 | 1 | 1 | 1 | 138 | 93 | **67.4%** | 4.0% | [59.2%, 74.6%] | 5,139 | 930 | 4,293 | 10,362 | $0.0146 | 15,376 |
| **C0100** | 0 | 1 | 0 | 0 | 0 | 138 | 94 | **68.1%** | 4.0% | [59.9%, 75.3%] | 2,163 | 369 | 1,369 | 3,901 | $0.0050 | 5,727 |
| **C0101** | 0 | 1 | 0 | 1 | 1 | 138 | 101 | **73.2%** | 3.8% | [65.2%, 79.9%] | 5,009 | 705 | 2,845 | 8,560 | $0.0104 | 11,696 |
| **C0110** | 0 | 1 | 1 | 0 | 1 | 138 | 89 | **64.5%** | 4.1% | [56.2%, 72.0%] | 5,208 | 515 | 2,864 | 8,587 | $0.0100 | 13,314 |
| **C0111** | 0 | 1 | 1 | 1 | 0 | 138 | 96 | **69.6%** | 3.9% | [61.4%, 76.6%] | 8,609 | 797 | 4,321 | 13,728 | $0.0154 | 19,734 |
| **C1000** | 1 | 0 | 0 | 0 | 0 | 138 | 90 | **65.2%** | 4.1% | [57.0%, 72.7%] | 1,799 | 335 | 1,465 | 3,599 | $0.0050 | 5,519 |
| **C1001** | 1 | 0 | 0 | 1 | 1 | 138 | 95 | **68.8%** | 3.9% | [60.7%, 76.0%] | 4,559 | 889 | 2,974 | 8,422 | $0.0110 | 12,234 |
| **C1010** | 1 | 0 | 1 | 0 | 1 | 138 | 93 | **67.4%** | 4.0% | [59.2%, 74.6%] | 4,383 | 545 | 2,935 | 7,863 | $0.0100 | 11,668 |
| **C1011** | 1 | 0 | 1 | 1 | 0 | 138 | 91 | **65.9%** | 4.0% | [57.7%, 73.3%] | 7,554 | 1,100 | 4,312 | 12,966 | $0.0158 | 19,663 |
| **C1100** | 1 | 1 | 0 | 0 | 1 | 138 | 95 | **68.8%** | 3.9% | [60.7%, 76.0%] | 3,245 | 403 | 1,546 | 5,194 | $0.0058 | 7,545 |
| **C1101** | 1 | 1 | 0 | 1 | 0 | 138 | 90 | **65.2%** | 4.1% | [57.0%, 72.7%] | 6,781 | 750 | 2,907 | 10,439 | $0.0112 | 16,006 |
| **C1110** | 1 | 1 | 1 | 0 | 0 | 138 | 90 | **65.2%** | 4.1% | [57.0%, 72.7%] | 6,788 | 596 | 2,933 | 10,317 | $0.0109 | 15,820 |
| **C1111** | 1 | 1 | 1 | 1 | 1 | 138 | 93 | **67.4%** | 4.0% | [59.2%, 74.6%] | 11,396 | 953 | 4,402 | 16,752 | $0.0168 | 24,857 |

---

## 3. Orthogonal Factor Main Effects & Retraction of Speculative Claims

Standard errors are computed via the **Huber-White / Liang-Zeger task-clustered sandwich covariance estimator** clustered across the 46 Tune tasks:

| Factor | Component in Screening A | Active $\bar{Y}(1)$ | Inactive $\bar{Y}(0)$ | Main Effect (pp) | Clustered SE | 95% Confidence Interval | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **s** | Generic Process Book (W01-W16) | 66.8% | 68.6% | **-1.81 pp** | 1.45 pp | [-4.73 pp, +1.11 pp] | -1.25 | 0.218 |
| **p** | Generic Worked Examples | 67.8% | 67.6% | **+0.18 pp** | 0.87 pp | [-1.57 pp, +1.94 pp] | 0.21 | 0.836 |
| **u** | Pytest Execution Tools | 66.8% | 68.6% | **-1.81 pp** | 1.56 pp | [-4.96 pp, +1.34 pp] | -1.16 | 0.253 |
| **r** | Self-Review Checklist | 68.3% | 67.0% | **+1.27 pp** | 1.06 pp | [-0.87 pp, +3.41 pp] | 1.19 | 0.239 |
| **k** | Policy Retry Mechanism | 68.5% | 66.8% | **+1.63 pp** | 1.27 pp | [-0.93 pp, +4.19 pp] | 1.28 | 0.206 |

> [!NOTE]
> **Retraction of Speculative Mechanisms (Reviewer Item R2):**  
> Prior informal hypotheses regarding "context dilution" explaining factor $s$ or models "modifying test assertions" explaining factor $u$ are retracted. The empirical facts are:
> 1. The handbook was never delivered in Screening A, so no conclusions regarding house-convention knowledge transmission can be drawn from these data.
> 2. Tamper attempts were rare (exactly 2 attempts out of 138 in cell `C0010` attempted modifying `tests/`, both caught by the tamper harness).
> 3. All five main effects are statistically indistinguishable from zero at $\alpha = 0.05$.

---

## 4. Descriptive Breakdown on Tune TAUGHT Tasks (13 Tasks, $N=39$ per cell)

Evaluated across the 13 Tune TAUGHT tasks ($Y_{B0} \le 70.0\%$):

| Cell | $s$ | $p$ | $u$ | $r$ | $k$ | Attempts | Passes | TAUGHT Pass Rate (%) | Wilson 95% CI | Billed Tokens / Pass |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0101** | 0 | 1 | 0 | 1 | 1 | 39 | 9 | **23.1%** | [12.6%, 38.3%] | 39,610 |
| **C0000** | 0 | 0 | 0 | 0 | 1 | 39 | 7 | **17.9%** | [9.0%, 32.7%] | 19,991 |
| **C0001** | 0 | 0 | 0 | 1 | 0 | 39 | 7 | **17.9%** | [9.0%, 32.7%] | 33,962 |
| **C0011** | 0 | 0 | 1 | 1 | 1 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 73,928 |
| **C0100** | 0 | 1 | 0 | 0 | 0 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 26,256 |
| **C0110** | 0 | 1 | 1 | 0 | 1 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 59,641 |
| **C1100** | 1 | 1 | 0 | 0 | 1 | 39 | 5 | **12.8%** | [5.6%, 26.7%] | 43,609 |
| **C0111** | 0 | 1 | 1 | 1 | 0 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 139,264 |
| **C1001** | 1 | 0 | 0 | 1 | 1 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 92,653 |
| **C1101** | 1 | 1 | 0 | 1 | 0 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 106,766 |
| **C1111** | 1 | 1 | 1 | 1 | 1 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 181,589 |
| **C0010** | 0 | 0 | 1 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 84,370 |
| **C1000** | 1 | 0 | 0 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 46,699 |
| **C1010** | 1 | 0 | 1 | 0 | 1 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 113,150 |
| **C1110** | 1 | 1 | 1 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 141,694 |
| **C1011** | 1 | 0 | 1 | 1 | 0 | 39 | 2 | **5.1%** | [1.4%, 16.9%] | 279,852 |

As expected when house rules are withheld, pass rates across all cells on TAUGHT tasks remained low (5.1% to 23.1%), confirming that these tasks cannot be solved through generic engineering intuition alone.

---

## 5. Statistical Power Warning for Phase 4 Confirmatory Study

The confirmatory primary population is pre-registered as **12 Held-Out TAUGHT tasks** across 6 bug families. 

Under cluster-correlated task heterogeneity ($\rho_{\text{task}} \in [0.15, 0.25]$), the minimum detectable effect (MDE) for a two-sample cluster-adjusted test at $\alpha = 0.05$ and power $\beta = 0.80$ is approximately:
$$\text{MDE} \approx 25\text{ to }37\text{ percentage points}$$

**Operational Requirement for Screening B:**  
Before expending budget on the confirmatory Phase 4 held-out evaluation, the corrected Screening B experiment must demonstrate an empirical effect size of **at least +25 to +30 percentage points** on the 13 Tune TAUGHT tasks under the candidate condition $\theta^*$ relative to the baseline control. If Screening B shows only small single-digit lifts, the honest scientific decision will be to report the screening findings and halt, rather than expending resources on an underpowered confirmatory run.

---

## 6. Execution Integrity & Audit Telemetry

| Audit Metric | Bound / Limit | Measured Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Completed Attempts** | 2,208 scheduled | **2,208** | **COMPLETE** |
| **Cumulative Spend** | Hard-Stop Cap: $37.85 USD | **$22.7661 USD** | **PASS** |
| **50% Spend Threshold** | Max $18.93 before attempt 883 | **$9.14 USD** | **PASS** |
| **Total Billed Tokens** | 18,664,336 tokens | **10.86M in, 1.47M out, 6.33M thoughts** | **PASS** |
| **MAX_TOKENS Truncations** | Exactly 0 allowable | **0** | **PASS** |
| **Unhandled API Errors** | Exactly 0 allowable | **0** | **PASS** |
| **Tamper Violations** | Isolated and scored failure | **2** (C0010, Tickets 2037 & 2039) | **PASS (ISOLATED)** |
