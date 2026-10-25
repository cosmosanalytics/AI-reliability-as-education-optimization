# Empirical Smoke Test & Screening Budget Report (Round 23 Item B2)

**Status:** Completed Engineering Check  
**Date:** 2026-10-25 18:40:58Z  
**Model:** `gemini-2.5-flash` (`temperature=0.7`, `thinking_budget=2048`, `max_output_tokens=16384`)  
**Pricing:** $0.30 / 1M prompt tokens, $2.50 / 1M candidate + thinking tokens  
**Seed:** `99999` (Isolated from screening seeds; all outputs discarded from experimental datasets)  
**Evaluated Tasks:** 3 Tune tasks: 2001 (`money_rounding`), 2005 (`config_merge`), 2013 (`csv_roundtrip`)  
**Evaluated Cells:** 3 cells: `C0000` (lightest), `C1001` (mid), `C1111` (heaviest) — 9 total live attempts  

---

## 1. Empirical Results Across 9 Smoke Test Attempts

| Cell Code | Scaffolding Level | Mean Tokens In | Mean Tokens Out | Mean Thinking | Total Billed Tokens | Mean Calls / Att | Mean Wall Time (s) | Mean Cost / Attempt ($ USD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`C0000`** | Lightest (Baseline format, all factors off) | 1038.3 | 589.3 | 1469.3 | 3097.0 | 1.00 | 12.79s | **$0.00546** |
| **`C1001`** | Mid ($s=1, p=0, u=0, r=1, k=1$) | 4511.3 | 802.0 | 3007.0 | 8320.3 | 2.00 | 24.40s | **$0.01088** |
| **`C1111`** | Heaviest (All factors on: $s=p=u=r=k=1$) | 11485.0 | 732.0 | 4850.3 | 17067.3 | 3.00 | 35.27s | **$0.01740** |

### Per-Attempt Execution Audit

| Cell | Task ID | Task Name | Strict Pass | Calls | Tokens In | Tokens Out | Thinking | Wall Time (s) | Cost ($ USD) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `C0000` | 2001 | Order Tax Calculation | True | 1 | 1069 | 347 | 1572 | 12.10s | $0.00512 |
| `C0000` | 2005 | Tenant Routing Configuration | True | 1 | 959 | 415 | 1488 | 11.83s | $0.00505 |
| `C0000` | 2013 | Customer Profile TSV Exporter | True | 1 | 1087 | 1006 | 1348 | 14.44s | $0.00621 |
| `C1001` | 2001 | Order Tax Calculation | True | 2 | 4581 | 825 | 2881 | 23.75s | $0.01064 |
| `C1001` | 2005 | Tenant Routing Configuration | True | 2 | 4284 | 666 | 3072 | 23.84s | $0.01063 |
| `C1001` | 2013 | Customer Profile TSV Exporter | True | 2 | 4669 | 915 | 3068 | 25.62s | $0.01136 |
| `C1111` | 2001 | Order Tax Calculation | True | 3 | 11291 | 484 | 4650 | 33.50s | $0.01622 |
| `C1111` | 2005 | Tenant Routing Configuration | True | 3 | 11061 | 688 | 4786 | 34.03s | $0.01700 |
| `C1111` | 2013 | Customer Profile TSV Exporter | True | 3 | 12103 | 1024 | 5115 | 38.27s | $0.01898 |

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

---

## 3. Budget Limits, Cap Setting, and Trade-Off Analysis

### Primary Screening Design ($N = 5$ Runs Per Cell)
- **Total Attempts:** 3,680 attempts
- **Projected Experiment Cost:** **$42.06 USD**
- **Hard-Stop Budget Cap (1.5x Total):** **$63.09 USD**
- **Conservative Worst-Case Bound (if 100% attempts matched C1111):** $64.04 USD (1.5x Cap: $96.05 USD)

### Evaluation Against the $50 Threshold
- Projected cost for $N=5$ (**UNDER** the $50 threshold at $42.06).
- If strict budget preservation is required:
  - **Cheaper Design Option ($N = 3$ Runs Per Cell):**
    - **Total Attempts:** 2,208 attempts
    - **Projected Cost:** **$25.24 USD** (1.5x Cap: **$37.85 USD**)
    - **Savings:** $16.82 USD (40.0% reduction in API spend)
    - **Statistical Trade-off:**
      - At N=5 runs per cell across 46 tasks (n = 230 observations per cell), standard error on cell pass rate is SE = sqrt(p(1-p)/230) ≈ 3.3%. Main effect contrasts (8 cells vs 8 cells, n = 1,840 per contrast) have SE ≈ 1.16%, providing β >= 0.90 power to detect a Δ >= 4.0% main effect.
      - At N=3 runs per cell across 46 tasks (n = 138 observations per cell), standard error on cell pass rate increases to SE = sqrt(p(1-p)/138) ≈ 4.2%. Main effect contrasts (n = 1,104 per contrast) have SE ≈ 1.50%, maintaining adequate power (β >= 0.80) for main effects Δ >= 5.0%, but reducing statistical power to resolve subtle two-way interaction terms (p x u, s x r) below 7%.

---

## 4. Operational Invariant Verification

1. **Isolation from Screening Data:** All raw transcripts, traces, and patches stored strictly under `results/smoke_test_b2/raw/`. Outputs are labeled engineering checks and discarded from all evaluation matrices.
2. **Seed Independence:** Smoke test ran under `seed=99999`. Screening runs will use independently registered seeds.
3. **No Freeze Invalidation:** Neither `benchmarks/suite_e5.py`, `benchmarks/splits_e5.json`, `briefs/HANDBOOK.md`, `briefs/PLACEBO.md`, nor `runner/agent_runner.py` was modified.
