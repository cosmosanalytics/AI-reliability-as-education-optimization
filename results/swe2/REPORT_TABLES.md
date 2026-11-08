# SWE-2 results: ontology + knowledge harness + confidence harness

Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp, CPU). Strict pass on hidden tests.

## Arm totals

| Arm | strict pass | rate | 95% CI | gain vs B0 (pp) |
|---|---|---|---|---|
| B0 | 19/56 | 33.9% | 23-47% | +0.0 |
| PLACEBO | 4/13 | 30.8% | 13-58% | -3.2 |
| KNOW | 12/15 | 80.0% | 55-93% | +46.1 |
| SURE | 4/14 | 28.6% | 12-55% | -5.4 |
| KNOW_SURE | 10/14 | 71.4% | 45-88% | +37.5 |

## Familiarity ranking (before education) and per-family strict pass

Familiarity = mean of the ranks of closed-book quiz accuracy and B0 debugging pass rate (1 = least familiar).

| Pos | Family | Rule | Quiz acc | Quiz consistency | Quiz conf | B0 | PLACEBO | KNOW | SURE | KNOW_SURE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | service_errors | H04 | 0.40 | 0.80 | 0.92 | 0% (4) | 0% (1) | 100% (2) | 0% (1) | 100% (1) |
| 2 | config_lists | H12 | 0.60 | 0.93 | 0.94 | 0% (4) | 0% (1) | 100% (1) | 0% (1) | 100% (1) |
| 3 | idempotency_keys | H13 | 0.60 | 0.80 | 0.91 | 0% (4) | 0% (1) | 100% (1) | 0% (1) | 0% (1) |
| 4 | wire_envelope | H08 | 0.60 | 0.93 | 0.92 | 0% (4) | 0% (1) | 100% (1) | 0% (1) | 100% (1) |
| 5 | csv_roundtrip | H10 | 0.00 | 1.00 | 0.95 | 50% (4) | 0% (1) | 100% (1) | 0% (1) | 100% (1) |
| 6 | metric_percentiles | H14 | 0.27 | 0.87 | 0.92 | 75% (4) | - | 100% (1) | 100% (1) | 100% (1) |
| 7 | event_ordering | H07 | 0.47 | 0.80 | 0.85 | 50% (4) | 100% (1) | 100% (1) | 100% (1) | 100% (1) |
| 8 | money_rounding | H02 | 0.60 | 0.67 | 0.97 | 25% (4) | 0% (1) | 0% (1) | 0% (1) | 0% (1) |
| 9 | timestamp_iso | H09 | 0.60 | 0.73 | 0.92 | 25% (4) | 100% (1) | 100% (1) | 0% (1) | 100% (1) |
| 10 | config_merge | H03 | 0.73 | 0.87 | 0.95 | 0% (4) | 0% (1) | 0% (1) | 0% (1) | 0% (1) |
| 11 | state_transitions | H15 | 0.73 | 0.93 | 0.94 | 0% (4) | 0% (1) | 100% (1) | 0% (1) | 100% (1) |
| 12 | cache_ttl | H11 | 0.67 | 0.67 | 0.94 | 100% (4) | 100% (1) | 100% (1) | 100% (1) | 100% (1) |
| 13 | calendar_recurrence | H05 | 0.67 | 1.00 | 0.95 | 100% (4) | 100% (1) | 100% (1) | 100% (1) | 100% (1) |
| 14 | permission_prefix | H06 | 0.87 | 0.87 | 0.93 | 50% (4) | 0% (1) | 0% (1) | 0% (1) | 0% (1) |

## Familiarity vs gain (Spearman rho across families, permutation p)

Quiz accuracy is the primary predictor: it is measured independently of debugging. B0 pass rate (and the composite) shares B0 sampling noise with the gain (arm - B0), which biases rho negative (regression to the mean).

| Gain of arm over B0 | vs quiz accuracy | vs B0 pass rate | vs composite familiarity | vs quiz consistency |
|---|---|---|---|---|
| PLACEBO (n=13) | -0.12 (p=0.690) | -0.15 (p=0.636) | -0.14 (p=0.648) | -0.27 (p=0.377) |
| KNOW (n=14) | -0.35 (p=0.220) | -0.67 (p=0.012) | -0.75 (p=0.004) | +0.21 (p=0.468) |
| SURE (n=14) | -0.20 (p=0.512) | -0.01 (p=0.986) | -0.20 (p=0.482) | -0.02 (p=0.942) |
| KNOW_SURE (n=14) | -0.38 (p=0.182) | -0.50 (p=0.074) | -0.60 (p=0.026) | +0.31 (p=0.276) |
| KNOW - PLACEBO (n=13) | | | -0.73 (p=0.007) | |
| KNOW_SURE - KNOW (n=14) | | | +0.31 (p=0.501) | |
| SURE - B0 (n=14) | | | -0.20 (p=0.482) | |

## Harness diagnostics

- PLACEBO: retrieval contained the family's rule in 0% of attempts; `know` tool used in 0%.
- KNOW: retrieval contained the family's rule in 100% of attempts; `know` tool used in 7%.
- KNOW_SURE: retrieval contained the family's rule in 100% of attempts; `know` tool used in 50%.
- SURE: revised 14/14 (conflict 1); revision fixed 1, broke 0; first-draft pass 3/14 -> final 4/14.
- KNOW_SURE: revised 14/14 (conflict 1); revision fixed 0, broke 1; first-draft pass 11/14 -> final 10/14.
- B0 stated confidence (post-hoc probe) mean 0.94 vs actual pass 0.34 (n=56).
- Attempts using at least one tool: 68/112; tampering: 0.
