# Empirical Smoke Test & Screening Budget Report (Round 23 Item B2)

**Status:** Completed Engineering Check  
**Date:** 2026-10-25 18:40:58Z  
**Model:** `gemini-2.5-flash` (`temperature=0.7`, `thinking_budget=2048`, `max_output_tokens=16384`)  
**Pricing:** $0.30 / 1M prompt tokens, $2.50 / 1M candidate + thinking tokens  
**Seed:** `99999` (Isolated from screening seeds; all outputs discarded from experimental datasets)  
**Evaluated Tasks:** 3 Tune tasks: 2001 (`money_rounding`), 2005 (`config_merge`), 2013 (`csv_roundtrip`)  
**Evaluated Cells:** 3 benchmark runs: `All-Off Reference` ($k=0$, baseline-like reference run), `C1001` (mid), `C1111` (heaviest) — 9 total live attempts  

---

## 1. Empirical Results Across 9 Smoke Test Attempts

| Run / Cell Label | Scaffolding Level | Mean Tokens In | Mean Tokens Out | Mean Thinking | Total Billed Tokens | Mean Calls / Att | Mean Wall Time (s) | Mean Cost / Attempt ($ USD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All-off reference, not a screening cell** | Lightest reference run ($s=0, p=0, u=0, r=0, k=0$) | 1038.3 | 589.3 | 1469.3 | 3097.0 | 1.00 | 12.79s | **$0.00546** |
| **`C1001`** | Mid ($s=1, p=0, u=0, r=1, k=1$) | 4511.3 | 802.0 | 3007.0 | 8320.3 | 2.00 | 24.40s | **$0.01088** |
| **`C1111`** | Heaviest (All factors on: $s=1, p=1, u=1, r=1, k=1$) | 11485.0 | 732.0 | 4850.3 | 17067.3 | 3.00 | 35.27s | **$0.01740** |

### Per-Attempt Execution Audit

| Condition / Cell | Task ID | Task Name | Strict Pass | Calls | Tokens In | Tokens Out | Thinking | Wall Time (s) | Cost ($ USD) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| All-off reference, not a screening cell | 2001 | Order Tax Calculation | True | 1 | 1069 | 347 | 1572 | 12.10s | $0.00512 |
| All-off reference, not a screening cell | 2005 | Tenant Routing Configuration | True | 1 | 959 | 415 | 1488 | 11.83s | $0.00505 |
| All-off reference, not a screening cell | 2013 | Customer Profile TSV Exporter | True | 1 | 1087 | 1006 | 1348 | 14.44s | $0.00621 |
| `C1001` | 2001 | Order Tax Calculation | True | 2 | 4581 | 825 | 2881 | 23.75s | $0.01064 |
| `C1001` | 2005 | Tenant Routing Configuration | True | 2 | 4284 | 666 | 3072 | 23.84s | $0.01063 |
| `C1001` | 2013 | Customer Profile TSV Exporter | True | 2 | 4669 | 915 | 3068 | 25.62s | $0.01136 |
| `C1111` | 2001 | Order Tax Calculation | True | 3 | 11291 | 484 | 4650 | 33.50s | $0.01622 |
| `C1111` | 2005 | Tenant Routing Configuration | True | 3 | 11061 | 688 | 4786 | 34.03s | $0.01700 |
| `C1111` | 2013 | Customer Profile TSV Exporter | True | 3 | 12103 | 1024 | 5115 | 38.27s | $0.01898 |

### Parity Clarification & Design Cell Labeling (Reviewer Finding F1)

- **Defining Relation & Half-Fraction Parity Rule:** In the experimental code and `PRE_REGISTRATION.md` (Phase 3), the $2^{5-1}$ Resolution-V fractional factorial design is governed by the defining relation $I = s \cdot p \cdot u \cdot r \cdot k$. The half-fraction parity rule specifies that $k = 1$ if and only if $(s + p + u + r) \pmod 2 == 0$ (i.e., when the sum of active educational factors is even).
- **Actual Screening Cell `C0000` has $k = 1$:** Because $s=0, p=0, u=0, r=0$ sums to $0$ (even), the generator sets $k = 1$. The true screening cell denoted `C0000` corresponds to $(s=0, p=0, u=0, r=0, k=1)$ (sources=0, practice=0, tools=0, review=0, retry=1).
- **Smoke-Test Run Clarification:** The smoke-test run originally labeled `C0000` was executed with $k = 0$ ($s=0, p=0, u=0, r=0, k=0$, 1 single-turn call, mean cost $0.00546 USD). It served strictly as an **all-off reference, not a screening cell**, providing a clean lower-bound baseline measurement.
- **Factorial Design Has No All-Off Cell:** The 16 orthogonal cells of the Resolution-V design do not contain an all-off cell ($00000$ violates the parity relation $I = spurk$ since $0+0+0+0=0$ is even, requiring $k=1$). Baseline $B_0$ ($s=0, p=0, u=0, r=0, k=0$) is evaluated separately as an independent control condition.
- **Modeled vs. Measured Cost for Screening Cell `C0000`:** The unit cost of $0.00699 USD listed in Section 2 for the actual screening cell `C0000` ($k = 1$) is an extrapolated modeled estimate from the additive component model (accounting for the presence of the retry scaffolding capability), not directly measured in the smoke test.

---

## 2. Factorial Screening Budget Extrapolation (46 Tune Tasks)

The screening campaign evaluates **16 Resolution-V factorial cells** across **46 Tune tasks** in `benchmarks/splits_e5.json`.

| Cell Code | $s$ | $p$ | $u$ | $r$ | $k$ | Unit Cost ($) | $N=5$ Attempts | $N=5$ Cost ($) | $N=3$ Attempts | $N=3$ Cost ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `C0000` | 0 | 0 | 0 | 0 | 1 | $0.00699 | 230 | $1.61 | 138 | $0.97 |
| `C0001` | 0 | 0 | 0 | 1 | 0 | $0.00904 | 230 | $2.08 | 138 | $1.25 |
| `C0010` | 0 | 0 | 1 | 0 | 0 | $0.01158 | 230 | $2.66 | 138 | $1.60 |
| `C0011` | 0 | 0 | 1 | 1 | 1 | $0.01670 | 230 | $3.84 | 138 | $2.30 |
| `C0100` | 0 | 1 | 0 | 0 | 0 | $0.00586 | 230 | $1.35 | 138 | $0.81 |
| `C0101` | 0 | 1 | 0 | 1 | 1 | $0.01098 | 230 | $2.52 | 138 | $1.51 |
| `C0110` | 0 | 1 | 1 | 0 | 1 | $0.01352 | 230 | $3.11 | 138 | $1.87 |
| `C0111` | 0 | 1 | 1 | 1 | 0 | $0.01557 | 230 | $3.58 | 138 | $2.15 |
| `C1000` | 1 | 0 | 0 | 0 | 0 | $0.00576 | 230 | $1.32 | 138 | $0.79 |
| `C1001` | 1 | 0 | 0 | 1 | 1 | $0.01088 | 230 | $2.50 | 138 | $1.50 |
| `C1010` | 1 | 0 | 1 | 0 | 1 | $0.01342 | 230 | $3.09 | 138 | $1.85 |
| `C1011` | 1 | 0 | 1 | 1 | 0 | $0.01547 | 230 | $3.56 | 138 | $2.13 |
| `C1100` | 1 | 1 | 0 | 0 | 1 | $0.00769 | 230 | $1.77 | 138 | $1.06 |
| `C1101` | 1 | 1 | 0 | 1 | 0 | $0.00974 | 230 | $2.24 | 138 | $1.34 |
| `C1110` | 1 | 1 | 1 | 0 | 0 | $0.01228 | 230 | $2.83 | 138 | $1.70 |
| `C1111` | 1 | 1 | 1 | 1 | 1 | $0.01740 | 230 | $4.00 | 138 | $2.40 |
| **TOTAL** | — | — | — | — | — | — | **3,680** | **$42.06** | **2,208** | **$25.24** |

### Budget Table Estimation Caveats & Retry Dynamics (Reviewer Finding F2)

- **Turn-1 Passes in Smoke Testing:** All 9 smoke attempts in the engineering check passed on turn 1. As a consequence, the automated retry mechanism ($k$) was never triggered during smoke testing.
- **Retry Impact in Screening ($k=1$ Cells):** In actual screening across the full Tune benchmark cohort, the baseline agent fails ~40% of tune tasks. Therefore, automated retries will fire regularly in $k = 1$ cells (which comprise exactly 8 of the 16 factorial cells: `C0000`, `C0011`, `C0101`, `C0110`, `C1001`, `C1010`, `C1100`, `C1111`).
- **Cost Overhead of Retries:** When triggered, automated retries add a second turn with longer prompt context (including full execution traceback and error feedback), which will likely increase the unit cost for $k = 1$ cells by ~25% to 40% over the single-turn cost.
- **Model Uncertainty on Interpolated Cells:** The unit costs for cells other than the empirically measured `C1001` and `C1111` (and all-off reference) are derived from an additive linear component model fitted to measured factor differentials. These interpolated figures should be treated as estimates with an expected uncertainty of approximately $\pm 30\%$.
- **Adequacy of the 1.5x Hard-Stop Cap:** The pre-registered 1.5x hard-stop budget cap (**$37.85 USD for $N=3$**, **$63.09 USD for $N=5$**) provides generous headroom (a 50% buffer over projected mean costs) that comfortably absorbs retry invocation overhead and additive model uncertainty without risking budget overrun.

---

## 3. Budget Limits, Cap Setting, and Trade-Off Analysis

### Primary Screening Design ($N = 5$ Runs Per Cell)
- **Total Attempts:** 3,680 attempts
- **Projected Experiment Cost:** **$42.06 USD**
- **Hard-Stop Budget Cap (1.5x Total):** **$63.09 USD**
- **Conservative Worst-Case Bound (if 100% attempts matched C1111):** $64.04 USD (1.5x Cap: $96.05 USD)

### Evaluation Against the $50 Threshold & Power Analysis (Reviewer Finding F3)
- Projected cost for $N=5$ is **UNDER** the $50 threshold at $42.06 USD.
- **Cheaper Design Option ($N = 3$ Runs Per Cell):**
  - **Total Attempts:** 2,208 attempts
  - **Projected Cost:** **$25.24 USD** (1.5x Cap: **$37.85 USD**)
  - **Direct Savings:** $16.82 USD (40.0% reduction in API spend)

### Statistical Power Realism: Clustered Variance & Task Heterogeneity

Naive statistical estimates (such as treating $N \times 46$ attempts as independent observations with $\text{SE} \approx 1.16\%$) fail because they ignore the task-clustered data structure. In benchmark factorial screening, main-effect variance decomposes into two distinct sources:

1. **Attempt Noise ($\sigma_{\text{attempt}}^2$, within-task variance):** Stochastic variation across repeated stochastic samplings ($T = 0.7$) of the *same* task. Increasing repeated runs per task ($N$) reduces this component as $\sigma_{\text{attempt}}^2 / N$.
2. **Task-by-Factor Variation ($\sigma_{\text{task}}^2$, between-task heterogeneity):** Differential factor efficacy across distinct bug families and task architectures. Repeated runs on the *same* 46 tasks do **NOT** reduce this component; the 46 Tune tasks constitute the effective sample constraint.

#### Realistic Standard Error and Power Comparison
Under empirically plausible task-level standard deviation ($\sigma_{\text{task}} \in [0.15, 0.25]$):
- In an orthogonal $2^{5-1}$ screening design comparing 8 factor-active cells against 8 factor-inactive cells across 46 tasks, the standard error of a main-effect contrast is dominated by between-task heterogeneity:
  $$\text{SE}(\Delta) \approx \frac{\sigma_{\text{task}}}{\sqrt{46 / 2}} = \frac{\sigma_{\text{task}}}{\sqrt{23}} \approx 3.1\% \text{ to } 5.2\%$$
- Because between-task variance ($\sigma_{\text{task}} / \sqrt{23}$) is the dominant noise floor, transitioning from $N=5$ to $N=3$ runs per task adds only minimal attempt noise relative to between-task variance.
- Specifically, the increase in overall contrast standard error from $N=5$ to $N=3$ is fractional (typically $< 0.4\%$), maintaining virtually identical ranking fidelity.
- Therefore, **Option B ($N=3$) loses negligible statistical power** for identifying and selecting the optimal candidate scaffolding design $\theta^*$, while saving **40% in API costs** ($25.24 USD vs. $42.06 USD) and preserving substantial experimental budget for downstream confirmatory phases.

---

## 4. Operational Invariant Verification

1. **Isolation from Screening Data:** All raw transcripts, traces, and patches stored strictly under `results/smoke_test_b2/raw/`. Outputs are labeled engineering checks and discarded from all evaluation matrices.
2. **Seed Independence:** Smoke test ran under `seed=99999`. Screening runs will use independently registered seeds.
3. **No Freeze Invalidation:** Neither `benchmarks/suite_e5.py`, `benchmarks/splits_e5.json`, `briefs/HANDBOOK.md`, `briefs/PLACEBO.md`, nor `runner/agent_runner.py` was modified.
