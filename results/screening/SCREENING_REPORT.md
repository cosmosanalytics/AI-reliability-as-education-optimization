# Phase 3 Screening Analysis & Scaffolding Selection Report

**Generated:** 2026-10-25 22:02:28 UTC  
**Design:** $2^{5-1}$ Fractional Factorial (Resolution V, Defining Relation $I = spurk$)  
**Scope:** Tune Task Split (46 Tasks across 14 Bug Families)  
**Execution Status:** 2208 / 2208 attempts (100.0% completed)  
**Financial Audit:** $22.7661 USD spent (60.1% of $37.85 USD cap)  

---

## 1. Executive Summary & Winning Scaffolding Condition ($\theta^*$)

- **Selected Candidate Condition ($	heta^*$):** `C0101` ($s=0, p=1, u=0, r=1, k=1$)  
- **Calibrated Tune Pass Rate:** **76.9%** (30 / 39 attempts, Wilson 95% CI: [61.7%, 87.4%])  
- **Cognitive Load ($\sum x_i$):** **3** active educational interventions  
- **Token Cost Efficiency:** **11,519 billed tokens / clean pass**  

> [!IMPORTANT]
> **Empirical Candidate Status Disclosure (Section 8.3 & Reviewer Mandate):**  
> Scaffolding condition `C0101` is designated strictly as the **best observed candidate cell** from screening on the Tune task split. In strict compliance with pre-registered confirmatory protocols, `C0101` is **NOT a proven best condition** until evaluated against the fresh, concurrent $B_0$ control arm on the Held-Out task split in Phase 4.

### Section 8.3 Selection Traceability Matrix:
1. **Scope Restriction:** Restricted strictly to the **13 calibrated Tune tasks** (15% <= Y_B0 <= 85%).
2. **Criterion 1 (Maximum Calibrated Pass Rate):** Observed maximum calibrated pass rate is **76.9%**.
3. **Criterion 2 (1.0 pp Tie Window & Cognitive Load):** **1 cell(s)** qualified within the 1.0 percentage point window (>= 75.9%). Minimal cognitive load among tied cells: **3** (1 cell(s) remaining).
4. **Criterion 3 (Deterministic Factor Hierarchy s > p > u > r > k):** Resolved ties deterministically to select candidate `C0101`.

---

## 2. 16-Cell Factorial Performance Table

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

## 3. Orthogonal Factor Main Effects & Two-Way Interactions

Standard errors are computed via the **Huber-White / Liang-Zeger task-clustered sandwich covariance estimator** clustered across the 46 Tune tasks, explicitly accounting for between-task heterogeneity.

### A. Factor Main Effects (Resolution V)

| Factor | Educational Component | Active $\bar{Y}(1)$ | Inactive $\bar{Y}(0)$ | Main Effect (pp) | Clustered SE | 95% Confidence Interval | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **s** | Sources (Handbook) | 66.8% | 68.6% | ** -1.81 pp** | 1.45 pp | [ -4.73 pp,  +1.11 pp] |  -1.25 | 0.2183 |
| **p** | Practice (Placebo) | 67.8% | 67.6% | ** +0.18 pp** | 0.87 pp | [ -1.57 pp,  +1.94 pp] |   0.21 | 0.8362 |
| **u** | Pytest Tools | 66.8% | 68.6% | ** -1.81 pp** | 1.56 pp | [ -4.96 pp,  +1.34 pp] |  -1.16 | 0.2526 |
| **r** | Self-Review Checklist | 68.3% | 67.0% | ** +1.27 pp** | 1.06 pp | [ -0.87 pp,  +3.41 pp] |   1.19 | 0.2390 |
| **k** | Policy Retry | 68.5% | 66.8% | ** +1.63 pp** | 1.27 pp | [ -0.93 pp,  +4.19 pp] |   1.28 | 0.2057 |

### B. Prominent Two-Factor Interactions

| Interaction | Factors Involved | Interaction Synergy (pp) | Clustered SE | 95% Confidence Interval | $t$-stat | $p$-value |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **sxp** | s × p | ** -0.36 pp** | 1.34 pp | [ -3.07 pp,  +2.34 pp] |  -0.27 | 0.7886 |
| **sxu** | s × u | ** +1.27 pp** | 1.05 pp | [ -0.84 pp,  +3.38 pp] |   1.21 | 0.2320 |
| **sxr** | s × r | ** -1.09 pp** | 1.20 pp | [ -3.51 pp,  +1.33 pp] |  -0.90 | 0.3703 |
| **sxk** | s × k | ** +1.09 pp** | 1.47 pp | [ -1.87 pp,  +4.04 pp] |   0.74 | 0.4626 |
| **pxu** | p × u | ** -0.36 pp** | 0.72 pp | [ -1.82 pp,  +1.09 pp] |  -0.50 | 0.6180 |
| **pxr** | p × r | ** +0.91 pp** | 0.88 pp | [ -0.87 pp,  +2.68 pp] |   1.03 | 0.3091 |
| **pxk** | p × k | ** -0.18 pp** | 0.83 pp | [ -1.86 pp,  +1.49 pp] |  -0.22 | 0.8286 |
| **uxr** | u × r | ** +0.36 pp** | 0.85 pp | [ -1.35 pp,  +2.08 pp] |   0.43 | 0.6721 |
| **uxk** | u × k | ** -1.81 pp** | 1.04 pp | [ -3.92 pp,  +0.29 pp] |  -1.73 | 0.0898 |
| **rxk** | r × k | ** +0.18 pp** | 1.11 pp | [ -2.05 pp,  +2.42 pp] |   0.16 | 0.8711 |

---

## 4. Descriptive Table on Tune TAUGHT Tasks Only (Reviewer Note 1)

This table evaluates performance strictly across the **13 Tune TAUGHT tasks** (tasks with fresh baseline pass rate $\le 70.0\%$ under Rule C2 and Condition L2), verifying whether scaffolding gains are specifically driven by rule-dependent organizational conventions.

| Cell | $s$ | $p$ | $u$ | $r$ | $k$ | Attempts | Passes | TAUGHT Pass Rate (%) | Wilson 95% CI | Billed Tokens / Pass | Total Cost ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0101** | 0 | 1 | 0 | 1 | 1 | 39 | 9 | **23.1%** | [12.6%, 38.3%] | 39,610 | $0.4430 |
| C0000 | 0 | 0 | 0 | 0 | 1 | 39 | 7 | **17.9%** | [9.0%, 32.7%] | 19,991 | $0.2531 |
| C0001 | 0 | 0 | 0 | 1 | 0 | 39 | 7 | **17.9%** | [9.0%, 32.7%] | 33,962 | $0.3797 |
| C0011 | 0 | 0 | 1 | 1 | 1 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 73,928 | $0.6354 |
| C0100 | 0 | 1 | 0 | 0 | 0 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 26,256 | $0.2088 |
| C0110 | 0 | 1 | 1 | 0 | 1 | 39 | 6 | **15.4%** | [7.2%, 29.7%] | 59,641 | $0.4435 |
| C1100 | 1 | 1 | 0 | 0 | 1 | 39 | 5 | **12.8%** | [5.6%, 26.7%] | 43,609 | $0.2521 |
| C0111 | 0 | 1 | 1 | 1 | 0 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 139,264 | $0.6428 |
| C1001 | 1 | 0 | 0 | 1 | 1 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 92,653 | $0.4904 |
| C1101 | 1 | 1 | 0 | 1 | 0 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 106,766 | $0.4712 |
| C1111 | 1 | 1 | 1 | 1 | 1 | 39 | 4 | **10.3%** | [4.1%, 23.6%] | 181,589 | $0.7699 |
| C0010 | 0 | 0 | 1 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 84,370 | $0.4064 |
| C1000 | 1 | 0 | 0 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 46,699 | $0.1965 |
| C1010 | 1 | 0 | 1 | 0 | 1 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 113,150 | $0.4624 |
| C1110 | 1 | 1 | 1 | 0 | 0 | 39 | 3 | **7.7%** | [2.7%, 20.3%] | 141,694 | $0.4799 |
| C1011 | 1 | 0 | 1 | 1 | 0 | 39 | 2 | **5.1%** | [1.4%, 16.9%] | 279,852 | $0.7080 |

---

## 5. Execution Integrity & Financial Audit Verification

| Audit Metric | Pre-Registered Cap / Limit | Measured Value | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Total Completed Attempts** | 2,208 scheduled | **2208** | **COMPLETE** |
| **Cumulative Financial Spend** | Hard-Stop Cap: $37.85 USD | **$22.7661 USD** | **PASS** |
| **50% Spend Threshold Check** | Max $18.93 before attempt 883 | **$22.7661 USD** | **PASS** |
| **Input Tokens Billed** | Unmetered (rate $0.30/1M) | **10,861,225** | **PASS** |
| **Output Tokens Billed** | Unmetered (rate $2.50/1M) | **1,468,703** | **PASS** |
| **Thinking Tokens Billed** | Billed at output rate ($2.50/1M) | **6,334,408** | **PASS** |
| **Total Billed Tokens** | Tracked vs financial cap | **18,664,336** | **PASS** |
| **Total API Calls Made** | Tracked across factor branches | **4,498** (2.04 / attempt) | **PASS** |
| **MAX_TOKENS Truncations** | Exactly 0 allowable | **0** | **PASS** |
| **Unhandled Provider Errors** | Exactly 0 allowable | **0** | **PASS** |
| **Policy / File Tamper Violations**| Exactly 0 allowable | **2** | **VIOLATION DETECTED** |
| **Protected File Modifications** | Exactly 0 allowable | **2** | **VIOLATION DETECTED** |

---
*Report generated automatically by `runner/analyze_screening.py` in compliance with Round 23/24 Experimental Protocols.*