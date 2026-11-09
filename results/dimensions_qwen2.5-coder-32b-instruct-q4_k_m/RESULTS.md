| Pos | Family | Rule | Baseline | PLACEBO | RULE | FULL | PRACTICE | TOOLS | REVIEW | RETRY |
|:-:|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | `config_lists` | H12 | 0/4 | 0/4 (+0) | 4/4 (+100) | 0/4 (+0) | 0/4 (+0) | 1/4 (+25) | 0/4 (+0) | 0/4 (+0) |
| 2 | `config_merge` | H03 | 0/4 | 0/4 (+0) | 0/4 (+0) | 2/4 (+50) | 0/4 (+0) | 1/4 (+25) | 0/4 (+0) | 0/4 (+0) |
| 3 | `csv_roundtrip` | H10 | 0/4 | 0/4 (+0) | 4/4 (+100) | 3/4 (+75) | 2/4 (+50) | 0/4 (+0) | 0/4 (+0) | 0/4 (+0) |
| 4 | `event_ordering` | H07 | 0/4 | 0/4 (+0) | 1/4 (+25) | 2/4 (+50) | 2/4 (+50) | 0/4 (+0) | 0/4 (+0) | 0/4 (+0) |
| 5 | `idempotency_keys` | H13 | 0/4 | 0/4 (+0) | 3/4 (+75) | 0/4 (+0) | 0/4 (+0) | 0/4 (+0) | 0/4 (+0) | 3/4 (+75) |
| 6 | `service_errors` | H04 | 0/4 | 0/4 (+0) | 4/4 (+100) | 4/4 (+100) | 1/4 (+25) | 0/4 (+0) | 0/4 (+0) | 4/4 (+100) |
| 7 | `state_transitions` | H15 | 0/4 | 0/4 (+0) | 4/4 (+100) | 4/4 (+100) | 2/4 (+50) | 0/4 (+0) | 0/4 (+0) | 4/4 (+100) |
| 8 | `cache_ttl` | H11 | 1/4 | 1/4 (+0) | 1/4 (+0) | 2/4 (+25) | 1/4 (+0) | 2/4 (+25) | 1/4 (+0) | 4/4 (+75) |
| 9 | `metric_percentiles` | H14 | 1/4 | 0/4 (-25) | 4/4 (+75) | 4/4 (+75) | 4/4 (+75) | 0/4 (-25) | 1/4 (+0) | 1/4 (+0) |
| 10 | `money_rounding` | H02 | 1/4 | 1/4 (+0) | 3/4 (+50) | 3/4 (+50) | 2/4 (+25) | 1/4 (+0) | 1/4 (+0) | 1/4 (+0) |
| 11 | `permission_prefix` | H06 | 1/4 | 1/4 (+0) | 1/4 (+0) | 0/4 (-25) | 0/4 (-25) | 1/4 (+0) | 0/4 (-25) | 2/4 (+25) |
| 12 | `timestamp_iso` | H09 | 1/4 | 3/4 (+50) | 2/4 (+25) | 1/4 (+0) | 1/4 (+0) | 0/4 (-25) | 1/4 (+0) | 2/4 (+25) |
| 13 | `calendar_recurrence` | H05 | 2/4 | 2/4 (+0) | 4/4 (+50) | 4/4 (+50) | 2/4 (+0) | 0/4 (-50) | 0/4 (-50) | 4/4 (+50) |
| 14 | `wire_envelope` | H08 | 3/4 | 1/4 (-50) | 4/4 (+25) | 3/4 (+0) | 4/4 (+25) | 0/4 (-75) | 1/4 (-50) | 2/4 (-25) |
|  | **All families** (14) |  | 10/56 | 9/56 (-2) | 39/56 (+52) | 32/56 (+39) | 21/56 (+20) | 6/56 (-7) | 5/56 (-9) | 27/56 (+30) |
|  | **Baseline 0%** (7) |  | 0/28 | 0/28 (+0) | 20/28 (+71) | 15/28 (+54) | 7/28 (+25) | 2/28 (+7) | 0/28 (+0) | 11/28 (+39) |
|  | **Baseline > 0%** (7) |  | 10/28 | 9/28 (-4) | 19/28 (+32) | 17/28 (+25) | 14/28 (+14) | 4/28 (-21) | 5/28 (-18) | 16/28 (+21) |
|  | **Spearman rho (gain vs baseline)** |  |  | -0.30 | -0.46 | -0.36 | -0.20 | -0.64 | -0.71 | -0.21 |

The "All families", "Baseline 0%" and "Baseline > 0%" rows compare each arm with B0 on the same families.

## Robustness: pooled baseline

The first attempts in Review and Retry use exactly the B0 prompt, which gives 8 more baseline samples per family:

| Baseline source | Strict pass |
|---|---|
| B0 diagnostic | 10/56 (17.9%) |
| Review, first attempt | 5/56 (8.9%) |
| Retry, first attempt | 8/56 (14.3%) |
| **Pooled** | **23/168 (13.7%)** |

The 7 families at 0% stay at 0/12 when pooled. The 7 families above 0% fall to between 2/12 and 5/12. With 4 samples per family, the diagnostic drew high on calendar_recurrence (2/4, 3/12 pooled) and wire_envelope (3/4, 5/12 pooled).

Spearman rho of gain against the **pooled** baseline:

| Arm | PLACEBO | RULE | FULL | PRACTICE | TOOLS | REVIEW | RETRY |
|---|---|---|---|---|---|---|---|
| rho | -0.22 | -0.44 | -0.21 | +0.04 | -0.49 | -0.61 | 0.00 |

## Within-arm effects of Review and Retry

- **Review:** first attempt 5/56, final 5/56. The self-review turn changed the patch in 4 of 56 attempts and the pass/fail outcome in none. Review's lower total compared with B0 (5 vs 10) comes from its first attempt, which is a plain baseline sample. It is sampling noise, not harm from reviewing.
- **Retry:** first attempt 8/56, final 27/56. One round of CI feedback adds about 34 points against the arm's own first attempt.
- **Tools:**
  - 6/56 strict passes (10.7%), against the pooled baseline of 13.7%.
  - The model used tools in nearly every attempt, averaging 3.3 tool turns. Python was used 48 times, pytest 42, grep 24 and lint 1.
  - It mostly verified its patch against the visible tests, which do not check the house rule. The patch then failed the hidden rule tests.
  - 5 of 56 attempts submitted no patch.

## Findings

1. **Books, relevant rule (RULE): largest gain.** 10/56 → 39/56 (+52 points). The gain is +71 on the 0%-baseline half and +32 on the rest.
2. **Books, full handbook (FULL): positive but weaker than the single rule.** +39 points. Some families that the rule alone fixes collapse under the 15-rule handbook: config_lists goes from 4/4 with RULE to 0/4 with FULL, and idempotency_keys from 3/4 to 0/4.
3. **Placebo: no gain** (9/56). The Books gains come from the content of the instruction, not from a longer prompt.
4. **Practice: positive, about half of RULE.** +20 points, +25 on the 0% half.
5. **Retry: the strongest non-Books dimension.** +30 against B0, +34 against its own first attempt. It fully fixes service_errors and state_transitions (0/4 → 4/4), but does nothing on 5 of the 0%-baseline families. Feedback helps when the CI message points the model to the rule.
6. **Tools and Review: no measurable gain with this model.** Their negative totals and rho values are within baseline sampling noise (see the pooled baseline). With 0% baseline families, rho is also biased negative by the floor: those families cannot lose.
7. **Gain vs knowledge gap:**
   - The paper's direction, larger gains where the gap is larger, holds for every dimension that helps at all. RULE, FULL, Practice and Retry all gain more on the 0%-baseline half than on the rest.
   - The rank correlation is much weaker than the paper's Books result (rho about -0.9). For RULE it is -0.46 against the B0 diagnostic and -0.44 against the pooled baseline.
   - Half the families tie at 0/4, and 4 attempts per cell are too few for a stable rank correlation.

## Caveats

- 4 attempts per cell: a single cell commonly moves by ±1–2 passes between runs. The group rows are more reliable than individual cells.
- The ranking has a 7-way tie at 0/4 and a 5-way tie at 1/4. Families with the same score are ordered alphabetically, so which families count as extremes and which as middle is partly arbitrary. Every family received every arm, so the full-ranking table does not depend on that choice.
- The workbook has no non-test practice example for cache_ttl.
- Retry feedback includes the hidden-test failure report, like a real CI run.
- A CPU-served open-weights model is much weaker than the paper's models, so the 0% floor is broader.

## Files

- `ranking.csv` / `ranking.json`: diagnostic ranking.
- `table.csv`, `TABLE.md`, `summary.json`: final table, totals, rho, token counts.
- `raw/`: one JSON record per attempt, with transcripts.
- `../drift_check_32b*/`: extra baseline rechecks on the long-running and on a freshly restarted server. Both scored 2/8 on wire_envelope plus calendar_recurrence, so no server drift.
- `../dimensions_qwen2.5-coder-7b-instruct-q4_k_m/`: an abandoned partial 7B run (diagnostic 4/112). Kept for reference only.
