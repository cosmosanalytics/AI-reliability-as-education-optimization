# Stage 3 Report: Updated 10-Family Table

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 3)
- **Date / Time:** 2026-10-26 17:59:04 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Total Attempts in Stage 3 Dataset:** 616 across 10 families
- **New Calls Executed in Stage 3:** 174 live model calls
- **New Calls Billed Tokens:** Input=320,332, Output=117,659, Thinking=255,985, Total=693,976
- **Financial Cost of New Calls:** $0.1361 USD
- **Wall-Clock Duration of New Calls:** 293.4s (~4.9m across 8 parallel workers)

## 1. Updated 10-Family Summary & Gains Table

Ordered by baseline pass rate / display position (Positions 1–5: Unknown end; Positions 10–11: Mid-baseline; Positions 12–14: Ceiling end).

| Pos | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) | Confidence / Category Note |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Pos 1** | `state_transitions` | H15 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Unknown end |
| **Pos 2** | `idempotency_keys` | H13 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Unknown end |
| **Pos 3** | `service_errors` | H04 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 16/16 (100.0%) | **+100.0** | **+100.0** | Unknown end |
| **Pos 4** | `config_merge` | H03 | 1/8 (12.5%) | 5/8 (62.5%) | 1/8 (12.5%) | 4/8 (50.0%) | **+0.0** | **+37.5** | **Low Confidence** (1 task, n=8; misapplied-rule harm) |
| **Pos 5** | `event_ordering` | H07 | 4/16 (25.0%) | 4/16 (25.0%) | 16/16 (100.0%) | 16/16 (100.0%) | **+75.0** | **+75.0** | Unknown end |
| **Pos 10** | `money_rounding` | H02 | 11/18 (61.1%) | 8/18 (44.4%) | 12/18 (66.7%) | 12/18 (66.7%) | **+5.6** | **+5.6** | Mid-baseline (noise floor ±25 pts) |
| **Pos 11** | `config_lists` | H12 | 10/16 (62.5%) | 6/16 (37.5%) | 16/16 (100.0%) | 14/16 (87.5%) | **+37.5** | **+25.0** | Mid-baseline |
| **Pos 12** | `timestamp_iso` | H09 | 15/16 (93.8%) | 12/16 (75.0%) | 16/16 (100.0%) | 14/16 (87.5%) | **+6.2** | **-6.2** | Ceiling end |
| **Pos 13** | `cache_ttl` | H11 | 16/16 (100.0%) | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | **-6.2** | **+0.0** | Ceiling end |
| **Pos 14** | `calendar_recurrence` | H05 | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | 16/16 (100.0%) | **+0.0** | **+0.0** | Ceiling end |

*Pattern summary: Unknown-end families (Pos 1–5) exhibit large educational gains under the full handbook (mean +75.0 pts, range +37.5 to +100.0 pts). Mid-baseline families (Pos 10–11) average +15.3 pts gain, while true ceiling-end families (Pos 12–14) exhibit zero net headroom (mean -2.1 pts).*

## 2. Per-Task Breakdown Table (All 10 Families)

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
| `config_merge` | 2006 | Database Pool Settings | `TAUGHT` | 1/8 | 5/8 | 1/8 | 4/8 |
| `event_ordering` | 2022 | Notification Batch Sorter | `TAUGHT` | 4/8 | 3/8 | 8/8 | 8/8 |
| `event_ordering` | 2024 | Event Stream Ingestion Sequencer | `TAUGHT` | 0/8 | 1/8 | 8/8 | 8/8 |
| `money_rounding` | 2002 | Invoice Discount Allocation | `TAUGHT` | 0/6 | 0/6 | 0/6 | 0/6 |
| `money_rounding` | 2003 | Multi-Currency Fee Conversion | `TAUGHT` | 5/6 | 3/6 | 6/6 | 6/6 |
| `money_rounding` | 2102 | Merchant Settlement Fee Calculator | `TAUGHT` | 6/6 | 5/6 | 6/6 | 6/6 |
| `config_lists` | 2054 | Cloud Infrastructure Cluster Specification Merge | `TAUGHT` | 3/4 | 1/4 | 4/4 | 4/4 |
| `config_lists` | 2055 | CI/CD Pipeline Step Arguments Merger | `TAUGHT` | 1/4 | 1/4 | 4/4 | 2/4 |
| `config_lists` | 2057 | Application Feature Gate Setting Aggregator | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
| `config_lists` | 2059 | Service Mesh Route Matcher Configurator | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
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

## 3. Arm Below Rule-Only or Baseline Analysis (Patch-Level Verification)

1. **`config_lists` (Rule H12): Full Handbook F (14/16, 87.5%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Task 2055 (CI/CD Pipeline Step Arguments Merger):** R scored 4/4, F scored 2/4 (failing F runs: `r1`, `r4`).
   - **Patch Verification:** Both failing F patches correctly implemented Rule H12 list deduplication, but explicitly added `from errors import ServiceError # Added for H04` at line 6 of `pipeline_composer.py`. Because this repository does not include an `errors` module, pytest test collection crashed immediately (`ModuleNotFoundError: No module named 'errors'`). Under Rule-only R, the model received only Rule H12 and did not touch `ServiceError`, passing 4/4.
2. **`idempotency_keys` (Rule H13): Full Handbook F (13/16, 81.2%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Tasks 2063 (`r1`), 2065 (`r2`), 2067 (`r1`):** R scored 4/4 on each, F scored 3/4 on each.
   - **Patch Verification:** In Task 2063 `r1`, the model added a `ServiceError` class to `errors.py` with type annotation `Dict[str, Any]` without importing `Dict` from `typing`, triggering a test collection `NameError: name 'Dict' is not defined`. In Task 2065 `r2` and 2067 `r1`, similar unrequested error-handling logic caused test collection crashes. Under Rule-only R, the model modified only `X-Idempotency-Key` headers, achieving 16/16.
3. **`state_transitions` (Rule H15): Full Handbook F (13/16, 81.2%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Task 2078 (Payment Escrow Lifecycle):** R scored 4/4, F scored 1/4 (failing F runs: `r1`, `r3`, `r4`).
   - **Patch Verification:** The model incorporated Rule H03 (Container Immutability) concepts from the full handbook into escrow state transitions, altering dictionary copy semantics and breaking assertions. Under Rule-only R, it implemented only the FSM transition validation, scoring 4/4.
4. **`config_merge` (Rule H03): Misapplied-Rule Harm (Low Confidence, $n=8$)**
   - **Task 2006 (Database Pool Settings):** B0=1/8, P=5/8, R=1/8, F=4/8.
   - **Patch Verification:** A run passes if and only if it edits `env_loader.py` (`merge_env_settings`). Under Rule-only R, Rule H03 caused the model to defensively edit `pool.py` or `options.py` instead in 7 of 8 runs (only run 6 touched `env_loader.py`). Under Full Handbook F, runs 2, 5, 6, 8 edited `env_loader.py` (4 passes). Under Placebo P, runs 1, 2, 5, 6, 7 edited `env_loader.py` (5 passes). H03 actively diverts the model to the wrong file. With $n=8$ and a +50-point placebo swing, this family cannot support claims about handbook efficacy and is flagged low-confidence.
5. **Placebo Dips and Noise Floor:**
   - In `money_rounding` (8/18 P vs 11/18 B0), `config_lists` (6/16 P vs 10/16 B0), and `timestamp_iso` (12/16 P vs 15/16 B0), the Placebo arm dips below Baseline.
   - These variations demonstrate that the empirical noise floor at this sample size ($n \approx 16$) is approximately $\pm 25$ points. Consequently, single-family gains under $\sim 25$ points (including `money_rounding` at +5.6 pts and `timestamp_iso` at -6.2 pts) cannot be distinguished from noise.
6. **Task Invariants Unsolved by Rules:**
   - **`money_rounding` Task 2002 (Invoice Discount Allocation):** Scored 0/6 across B0, P, R, and F (0/24 overall).
   - **Patch Verification:** The issue describes an unallocated penny mismatch during checkout settlement. The model attempts custom remainder-rebalancing algorithms or auxiliary error imports across all arms rather than independent Decimal `ROUND_HALF_UP` quantization. The house rule alone is not the missing piece for this task.
7. **`timestamp_iso` (Rule H09) & `cache_ttl` (Rule H11) Differences:**
   - `timestamp_iso` F (14/16) failing runs (`r3` on 2047, `r2` on 2049) represent naive `isoformat` millisecond formatting bugs.
   - `cache_ttl` R (15/16) failing run (`r2` on 2026) added an extraneous quota validation inside `is_active`. Both are within sampling noise.

## 4. Plain-Language Reading (5 Lines)

1. Unknown end (positions 1–5): state_transitions (Pos 1) gained +81.2 (full); idempotency_keys (Pos 2) gained +81.2 (full); service_errors (Pos 3) gained +100.0 (full); config_merge (Pos 4, low-conf n=8) baseline was 1/8 and gained +0.0 (rule) and +37.5 (full); event_ordering (Pos 5) baseline was 4/16 and gained +75.0 (rule) and +75.0 (full).
2. Mid-baseline (positions 10–11) and ceiling end (positions 12–14): money_rounding (Pos 10) baseline was 11/18 and gained +5.6 (full); config_lists (Pos 11) baseline was 10/16 and gained +25.0 (full); timestamp_iso (Pos 12) gained -6.2 (full); cache_ttl (Pos 13) gained +0.0 (full); calendar_recurrence (Pos 14) gained +0.0 (full).
3. Placebo dips: Placebo scored below baseline in money_rounding (8/18 vs 11/18), config_lists (6/16 vs 10/16), and timestamp_iso (12/16 vs 15/16), establishing an empirical noise floor of roughly ±25 points for individual family gains.
4. Across the 10 evaluated families, full handbook gain averages +75.0 pts on the unknown end (Pos 1–5), compared to +15.3 pts on mid-baseline (Pos 10–11) and -2.1 pts on true ceiling (Pos 12–14).
5. Cross-rule interference accounted for the full handbook scoring below rule-only in config_lists (Task 2055 importing unneeded ServiceError), idempotency_keys, and state_transitions; config_merge represents misapplied-rule harm with high placebo sensitivity (n=8); timestamp_iso and cache_ttl differences reflect sampling noise.

## 5. Verification Artifacts & Links

- **Stage 3 Report:** [`results/stage3/STAGE_3_REPORT.md`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/STAGE_3_REPORT.md)
- **Raw Outputs Directory:** [`results/stage3/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/raw) (616 per-attempt JSON records across all 10 families)
- **Consolidated Dataset:** [`results/stage3/results.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/results.json)
- **Schedule File:** [`results/stage3/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/schedule_order.json)
- **Runner Script:** [`runner/run_stage3.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage3.py)
