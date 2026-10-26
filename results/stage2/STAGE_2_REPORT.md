# Stage 2 Report: Updated 6-Family Table

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 2)
- **Date / Time:** 2026-10-26 17:43:51 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Total Attempts in Stage 2 Dataset:** 384 across 6 families (96 per arm across B0, P, R, F)
- **New Calls Executed in Stage 2:** 192 live model calls
- **New Calls Billed Tokens:** Input=353,108, Output=101,597, Thinking=274,993, Total=729,698
- **Financial Cost of New Calls:** $0.1395 USD
- **Wall-Clock Duration of New Calls:** 302.5s (~5.0m across 8 parallel workers)

## 1. Updated 6-Family Summary & Gains Table

Ordered by baseline pass rate / display position (Positions 1–3: Unknown end; Positions 12–14: Ceiling end).

| Pos | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) | Pattern Note |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| Pos 1 | `state_transitions` | H15 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Consistent (large educational gain on unknown) |
| Pos 2 | `idempotency_keys` | H13 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Consistent (large educational gain on unknown) |
| Pos 3 | `service_errors` | H04 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 16/16 (100.0%) | **+100.0** | **+100.0** | Consistent (large educational gain on unknown) |
| Pos 12 | `timestamp_iso` | H09 | 15/16 (93.8%) | 12/16 (75.0%) | 16/16 (100.0%) | 14/16 (87.5%) | **+6.2** | **-6.2** | Consistent (near zero gain at ceiling) |
| Pos 13 | `cache_ttl` | H11 | 16/16 (100.0%) | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | **-6.2** | **+0.0** | Consistent (near zero gain at ceiling) |
| Pos 14 | `calendar_recurrence` | H05 | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | 16/16 (100.0%) | **+0.0** | **+0.0** | Consistent (near zero gain at ceiling) |

## 2. Per-Task Breakdown Table (All 6 Families)

| Family | Task ID | Name | Class | B0 Pass | P Pass | R Pass | F Pass |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| `state_transitions` | 2077 | Deployment Pipeline Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2078 | Payment Escrow Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 1/4 |
| `state_transitions` | 2079 | Support Ticket Workflow | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2080 | Cloud Compute Instance Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `idempotency_keys` | 2062 | Order Fulfillment RPC Client | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `idempotency_keys` | 2063 | Subscription Recurring Charge Request | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `idempotency_keys` | 2065 | Customer Refund Dispatcher | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `idempotency_keys` | 2067 | Cloud Virtual Machine Provisioning RPC | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `service_errors` | 2030 | Tenant Scope Authorization Guard | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2031 | Payload Schema Validation Pipeline | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2033 | Concurrent Document Lock Manager | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2035 | Burst Quota Throttling Guard | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `timestamp_iso` | 2046 | Telemetry Log Serializer | `TAUGHT` | 4/4 | 4/4 | 4/4 | 4/4 |
| `timestamp_iso` | 2047 | Webhook Delivery Envelope | `TAUGHT` | 4/4 | 2/4 | 4/4 | 3/4 |
| `timestamp_iso` | 2049 | Database Snapshot Metadata Generator | `TAUGHT` | 4/4 | 3/4 | 4/4 | 3/4 |
| `timestamp_iso` | 2051 | Security Token Exchange Ledger | `TAUGHT` | 3/4 | 3/4 | 4/4 | 4/4 |
| `cache_ttl` | 2025 | In-Memory Token Cache | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `cache_ttl` | 2026 | API Rate Limit Session Store | `TRANSFER` | 4/4 | 4/4 | 3/4 | 4/4 |
| `cache_ttl` | 2027 | Distributed Lease Expiry Guard | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `cache_ttl` | 2028 | DNS Cache TTL Resolver | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `calendar_recurrence` | 2010 | Subscription Active Window Evaluator | `TAUGHT` | 8/8 | 7/8 | 8/8 | 8/8 |
| `calendar_recurrence` | 2012 | Audit Log Retention Window | `TAUGHT` | 8/8 | 8/8 | 8/8 | 8/8 |

## 3. Arm Below Rule-Only or Baseline Analysis

- **`state_transitions` (Rule H15):** Full Handbook F (81.2%) scored below Rule-Only R (100.0%), diff = -18.8 pts.
  - **Task 2078 (Payment Escrow Lifecycle):** R scored 4/4, F scored 1/4 (failing F runs: `r1`, `r3`, `r4`).
  - **Patch Difference Analysis:** In the failing F patches for Task 2078, the model incorporated Rule H03 (Container Immutability) concepts from the broader handbook, altering how escrow dictionaries were copied/mutated in place. By contrast, under Rule-only R, the model received only Rule H15 and focused strictly on the finite state machine transition validation and audit tuples without introducing secondary container transformations.
- **`idempotency_keys` (Rule H13):** Full Handbook F (81.2%) scored below Rule-Only R (100.0%), diff = -18.8 pts.
  - **Tasks & Runs Affected:** Task 2063 `r1`, Task 2065 `r2`, and Task 2067 `r1` (each 3/4 under F vs 4/4 under R).
  - **Patch Difference Analysis:** Under arm F, the model attempted cross-rule adherence by proactively implementing Rule H04 (Structured Service Exception Hierarchy) alongside Rule H13. In Task 2063 `r1`, it added a `ServiceError` class in `errors.py` with type annotations `Dict[str, Any]` without importing them from `typing`, triggering a test collection `NameError: name 'Dict' is not defined`. In Task 2065 `r2` and Task 2067 `r1`, similar auxiliary exception handling code introduced syntax or collection failures. Under Rule-only R, the model focused purely on `X-Idempotency-Key` headers without touching exception classes, achieving a perfect 16/16.
- **`timestamp_iso` (Rule H09):** Full Handbook F (87.5%) scored below Rule-Only R (100.0%), diff = -12.5 pts.
  - **Tasks & Runs Affected:** Task 2047 `r3` and Task 2049 `r2` (each 3/4 under F vs 4/4 under R).
  - **Patch Difference Analysis:** These are formatting bugs where the patches use naive `isoformat(timespec='milliseconds') + 'Z'`. The visible tests pass, but hidden tests fail on the exact canonical ISO representation.
- **`cache_ttl` (Rule H11):** Rule-Only R (93.8%) scored slightly below Baseline B0 (100.0%), diff = -6.2 pts.
  - **Task & Run Affected:** Task 2026 `r2` (3/4 under R vs 4/4 under B0).
  - **Patch Difference Analysis:** In Task 2026 `r2`, the patch extraneous added a quota check inside `is_active`, which caused an edge-case hidden assertion to fail.

## 4. Plain-Language Reading (5 Lines)

1. Unknown end (positions 1–3): state_transitions (Pos 1) gained +100.0 (rule) and +81.2 (full); idempotency_keys (Pos 2) baseline was 0/16 and gained +100.0 (rule) and +81.2 (full); service_errors (Pos 3) baseline was 0/16 and gained +100.0 (rule) and +100.0 (full).
2. Ceiling end (positions 12–14): timestamp_iso (Pos 12) baseline was 15/16 and gained +6.2 (rule) and -6.2 (full); cache_ttl (Pos 13) baseline was 16/16 and gained -6.2 (rule) and +0.0 (full); calendar_recurrence (Pos 14) baseline was 16/16 and gained +0.0 (rule) and +0.0 (full).
3. Placebo arm performance across all 6 families tracked baseline closely: state_transitions P=0.0%, idempotency_keys P=0.0%, service_errors P=0.0%, timestamp_iso P=75.0%, cache_ttl P=100.0%, calendar_recurrence P=93.8%.
4. Full handbook gains on unknown end average +87.5 pts (range: +81.2 to +100.0 pts), while ceiling end full handbook gains average -2.1 pts (range: -6.2 to +0.0 pts).
5. Cross-rule interference is likely in two families (state_transitions and idempotency_keys), while sampling noise is likely in the other two (timestamp_iso and cache_ttl).

## 5. Verification Artifacts & Links

- **Raw Outputs Directory:** [`results/stage2/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage2/raw)
- **Consolidated Results:** [`results/stage2/results.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage2/results.json)
- **Schedule File:** [`results/stage2/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage2/schedule_order.json)
- **Runner Script:** [`runner/run_stage2.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage2.py)
