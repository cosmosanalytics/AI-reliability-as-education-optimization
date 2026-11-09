# SWE-2 results: ontology + knowledge harness + confidence harness

Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp, CPU). Strict pass on hidden tests.

## Arm totals

| Arm | strict pass | rate | 95% CI | gain vs B0 (pp) |
|---|---|---|---|---|
| B0 | 19/56 | 33.9% | 23-47% | +0.0 |
| PLACEBO | 18/56 | 32.1% | 21-45% | -1.8 |
| KNOW | 46/56 | 82.1% | 70-90% | +48.2 |
| SURE | 22/56 | 39.3% | 28-52% | +5.4 |
| KNOW_SURE | 47/56 | 83.9% | 72-91% | +50.0 |

## Familiarity ranking (before education) and per-family strict pass

Familiarity = mean of the ranks of closed-book quiz accuracy and B0 debugging pass rate (1 = least familiar).

| Pos | Family | Rule | Quiz acc | Quiz consistency | Quiz conf | B0 | PLACEBO | KNOW | SURE | KNOW_SURE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | service_errors | H04 | 0.40 | 0.80 | 0.92 | 0% (4) | 0% (4) | 100% (4) | 0% (4) | 100% (4) |
| 2 | config_lists | H12 | 0.60 | 0.93 | 0.94 | 0% (4) | 0% (4) | 100% (4) | 0% (4) | 100% (4) |
| 3 | idempotency_keys | H13 | 0.60 | 0.80 | 0.91 | 0% (4) | 0% (4) | 75% (4) | 0% (4) | 75% (4) |
| 4 | wire_envelope | H08 | 0.60 | 0.93 | 0.92 | 0% (4) | 0% (4) | 100% (4) | 0% (4) | 100% (4) |
| 5 | csv_roundtrip | H10 | 0.00 | 1.00 | 0.95 | 50% (4) | 25% (4) | 75% (4) | 25% (4) | 100% (4) |
| 6 | metric_percentiles | H14 | 0.27 | 0.87 | 0.92 | 75% (4) | 25% (4) | 100% (4) | 75% (4) | 100% (4) |
| 7 | event_ordering | H07 | 0.47 | 0.80 | 0.85 | 50% (4) | 50% (4) | 100% (4) | 75% (4) | 75% (4) |
| 8 | money_rounding | H02 | 0.60 | 0.67 | 0.97 | 25% (4) | 50% (4) | 50% (4) | 50% (4) | 25% (4) |
| 9 | timestamp_iso | H09 | 0.60 | 0.73 | 0.92 | 25% (4) | 50% (4) | 75% (4) | 50% (4) | 100% (4) |
| 10 | config_merge | H03 | 0.73 | 0.87 | 0.95 | 0% (4) | 25% (4) | 50% (4) | 25% (4) | 75% (4) |
| 11 | state_transitions | H15 | 0.73 | 0.93 | 0.94 | 0% (4) | 0% (4) | 100% (4) | 0% (4) | 100% (4) |
| 12 | cache_ttl | H11 | 0.67 | 0.67 | 0.94 | 100% (4) | 100% (4) | 100% (4) | 100% (4) | 100% (4) |
| 13 | calendar_recurrence | H05 | 0.67 | 1.00 | 0.95 | 100% (4) | 100% (4) | 75% (4) | 100% (4) | 100% (4) |
| 14 | permission_prefix | H06 | 0.87 | 0.87 | 0.93 | 50% (4) | 25% (4) | 50% (4) | 50% (4) | 25% (4) |

## Familiarity vs gain (Spearman rho across families, permutation p)

Quiz accuracy is the primary predictor: it is measured independently of debugging. B0 pass rate (and the composite) shares B0 sampling noise with the gain (arm - B0), which biases rho negative (regression to the mean).

| Gain of arm over B0 | vs quiz accuracy | vs B0 pass rate | vs composite familiarity | vs quiz consistency |
|---|---|---|---|---|
| PLACEBO (n=14) | +0.29 (p=0.315) | -0.39 (p=0.164) | +0.09 (p=0.749) | -0.45 (p=0.110) |
| KNOW (n=14) | -0.18 (p=0.535) | -0.89 (p=0.000) | -0.71 (p=0.007) | +0.08 (p=0.784) |
| SURE (n=14) | +0.19 (p=0.502) | -0.12 (p=0.692) | +0.20 (p=0.479) | -0.59 (p=0.031) |
| KNOW_SURE (n=14) | -0.19 (p=0.499) | -0.84 (p=0.001) | -0.67 (p=0.012) | +0.25 (p=0.383) |
| KNOW - PLACEBO (n=14) | | | -0.75 (p=0.003) | |
| KNOW_SURE - KNOW (n=14) | | | +0.05 (p=0.855) | |
| SURE - B0 (n=14) | | | +0.20 (p=0.479) | |

## Harness diagnostics

- PLACEBO: retrieval contained the family's rule in 0% of attempts; `know` tool used in 0%.
- KNOW: retrieval contained the family's rule in 100% of attempts; `know` tool used in 7%.
- KNOW_SURE: retrieval contained the family's rule in 100% of attempts; `know` tool used in 54%.
- SURE: revised 56/56 (conflict 4); revision fixed 1, broke 0; first-draft pass 21/56 -> final 22/56.
- KNOW_SURE: revised 56/56 (conflict 3); revision fixed 4, broke 1; first-draft pass 44/56 -> final 47/56.
- B0 stated confidence (post-hoc probe) mean 0.94 vs actual pass 0.34 (n=56).
- Attempts using at least one tool: 166/280; tampering: 0.
