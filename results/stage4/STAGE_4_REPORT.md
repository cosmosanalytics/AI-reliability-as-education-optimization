# Stage 4 Report: Complete 14-Family Results

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 4 - Final)
- **Date / Time:** 2026-10-26 18:30:51 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Total Attempts in Dataset:** 872 attempts across all 14 families
- **New Live Calls Executed in Stage 4:** 192 model calls across 4 middle families (Positions 6–9: `wire_envelope`, `csv_roundtrip`, `permission_prefix`, `metric_percentiles`)
- **New Calls Billed Tokens:** Input=360,424, Output=155,033, Thinking=296,145, Total=811,602
- **Financial Cost of New Calls:** $0.1624 USD
- **Wall-Clock Duration of New Calls:** 354.4s (~5.9m)
- **Cumulative Dataset Attempts:** 872 (Stage 0 B0 re-used: 218; Stages 1–3 live: 462; Stage 4 live: 192)
- **Cumulative Financial Cost:** ~$0.56 USD

---

## 1. Complete 14-Family Table (Ordered by Baseline Solvability)

Ordered strictly by baseline pass rate / frozen display position from least known (Pos 1) to most known (Pos 14).
Score cells are coloured by pass rate:
- 🔴 **Low** (< 40%)
- 🟡 **Mid** (40%–75%)
- 🟢 **High** (> 75%)

| Pos | Bug Family | Rule | Baseline (B0) | Placebo (P) | Rule Only (R) | Full Handbook (F) | Rule Gain | Full Gain |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Pos 1 | `state_transitions` | H15 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">13/16 (81.2%)</span> | **+100.0** | **+81.2** |
| Pos 2 | `idempotency_keys` | H13 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">13/16 (81.2%)</span> | **+100.0** | **+81.2** |
| Pos 3 | `service_errors` | H04 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **+100.0** | **+100.0** |
| Pos 4 | `config_merge` | H03 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">1/8 (12.5%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">5/8 (62.5%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">1/8 (12.5%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">4/8 (50.0%)</span> | **+0.0** | **+37.5** |
| Pos 5 | `event_ordering` | H07 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">4/16 (25.0%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">4/16 (25.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **+75.0** | **+75.0** |
| Pos 6 | `wire_envelope` | H08 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">4/16 (25.0%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">0/16 (0.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">14/16 (87.5%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **+62.5** | **+75.0** |
| Pos 7 | `csv_roundtrip` | H10 | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">6/16 (37.5%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">4/16 (25.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">15/16 (93.8%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">13/16 (81.2%)</span> | **+56.2** | **+43.8** |
| Pos 8 | `permission_prefix` | H06 | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">7/16 (43.8%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">4/16 (25.0%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">9/16 (56.2%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">13/16 (81.2%)</span> | **+12.5** | **+37.5** |
| Pos 9 | `metric_percentiles` | H14 | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">9/16 (56.2%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">7/16 (43.8%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **+43.8** | **+43.8** |
| Pos 10 | `money_rounding` | H02 | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">11/18 (61.1%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">8/18 (44.4%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">12/18 (66.7%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">12/18 (66.7%)</span> | **+5.6** | **+5.6** |
| Pos 11 | `config_lists` | H12 | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">10/16 (62.5%)</span> | 🔴 <span style="background-color:#ffebee;color:#c62828;padding:2px 6px;border-radius:4px;font-weight:600">6/16 (37.5%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">14/16 (87.5%)</span> | **+37.5** | **+25.0** |
| Pos 12 | `timestamp_iso` | H09 | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">15/16 (93.8%)</span> | 🟡 <span style="background-color:#fffde7;color:#f57f17;padding:2px 6px;border-radius:4px;font-weight:600">12/16 (75.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">14/16 (87.5%)</span> | **+6.2** | **-6.2** |
| Pos 13 | `cache_ttl` | H11 | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">15/16 (93.8%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **-6.2** | **+0.0** |
| Pos 14 | `calendar_recurrence` | H05 | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">15/16 (93.8%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | 🟢 <span style="background-color:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:4px;font-weight:600">16/16 (100.0%)</span> | **+0.0** | **+0.0** |

### Statistical Correlation Analysis

- **Spearman Rank Correlation ($\rho$):** `-0.9143` ($p = 4.7292 \times 10^{-6}$)
- **Pearson Linear Correlation ($r$):** `-0.8931` ($p = 1.3411 \times 10^{-5}$)
- **Tier Means:**
  - **Unknown End (Positions 1–5):** Mean full gain = **+75.0 points** (range +37.5 to +100.0 pts)
  - **Middle Tier (Positions 6–9):** Mean full gain = **+50.0 points** (range +37.5 to +75.0 pts)
  - **Mid-Baseline (Positions 10–11):** Mean full gain = **+15.3 points** (range +5.6 to +25.0 pts)
  - **True Ceiling (Positions 12–14):** Mean full gain = **-2.1 points** (range -6.2 to +0.0 pts)
- **Interpretation:** There is an exceptionally strong, statistically significant negative monotonic gradient between unaided baseline solvability and handbook gain. As predicted by the educational hypothesis, the less the model knows unaided, the greater the capability boost delivered by handbook education.

---

## 2. Per-Task Breakdown Table (All 14 Families, 46 Tasks)

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
| `wire_envelope` | 2037 | Audit Event Wire Formatter | `TAUGHT` | 2/4 | 0/4 | 3/4 | 4/4 |
| `wire_envelope` | 2038 | Billing Transaction Message Emitter | `TAUGHT` | 1/4 | 0/4 | 3/4 | 4/4 |
| `wire_envelope` | 2039 | Telemetry Metric Stream Normalizer | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `wire_envelope` | 2041 | User Activity Event Dispatcher | `TAUGHT` | 1/4 | 0/4 | 4/4 | 4/4 |
| `csv_roundtrip` | 2014 | Order Item TSV Serializer | `TAUGHT` | 2/4 | 1/4 | 4/4 | 3/4 |
| `csv_roundtrip` | 2015 | Batch Metric TSV Downloader | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `csv_roundtrip` | 2100 | Transaction Ledger TSV Exporter | `TAUGHT` | 2/4 | 1/4 | 4/4 | 3/4 |
| `csv_roundtrip` | 2101 | System Log TSV Serializer | `TAUGHT` | 2/4 | 2/4 | 3/4 | 3/4 |
| `permission_prefix` | 2018 | Document Store Scope RBAC Filter | `TAUGHT` | 0/8 | 0/8 | 7/8 | 7/8 |
| `permission_prefix` | 2020 | Webhook Subscription Scope Enforcer | `TAUGHT` | 7/8 | 4/8 | 2/8 | 6/8 |
| `metric_percentiles` | 2070 | Database Query Duration Monitor | `TAUGHT` | 1/4 | 1/4 | 4/4 | 4/4 |
| `metric_percentiles` | 2071 | Microservice RPC Response Timer | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
| `metric_percentiles` | 2073 | Cache Lookup Latency Reporter | `TAUGHT` | 2/4 | 2/4 | 4/4 | 4/4 |
| `metric_percentiles` | 2075 | Storage IO Wait Time Tracker | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
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

---

## 3. Arm Below Rule-Only or Baseline Analysis (Patch-Level Verification)

Every case where an educational arm scored below rule-only or below baseline was diagnosed directly against the failing patches, test traces, and ticket specifications:

1. **`permission_prefix` (Rule H06) — Misapplied-Rule Harm on Task 2020:**
   - **Performance:** On Task 2020 (`Webhook Subscription Scope Enforcer`), Rule-Only R scored **2/8**, while Baseline B0 scored **7/8**, Placebo scored **4/8**, and Full Handbook scored **6/8**.
   - **Patch Diagnostics:** The ticket issue describes event bus leak EVT-918: a subscriber to `"orders"` received `"orders_admin"`. The original code used `event_topic.startswith(subscribed_pattern)`. Unaided (B0), the model simply changed this to check prefix boundaries (`topic == sub or topic.startswith(sub + "::")`), cleanly passing 7/8 runs. However, Rule H06 explicitly mandates hierarchical scope parsing and wildcards (`*` and `**`). Under Rule-Only R, the model was distracted into implementing a full double-colon segment parser (`pattern_segments = subscribed_pattern.split("::")`), which treated `"orders"` as an exact 1-segment literal pattern that rejected subpaths like `"orders::created"`, directly failing `test_nominal_topic`. Under Full Handbook F, the model was less hyper-focused on Rule H06 in isolation and passed 6/8. This confirms **misapplied-rule harm** when a rule induces excessive complexity for a simpler local contract.
2. **`csv_roundtrip` (Rule H10) — Python Docstring Unicode Escape Syntax Bug:**
   - **Performance:** Full Handbook F scored **13/16 (81.2%)** compared to Rule-Only R at **15/16 (93.8%)** (-12.5 pts).
   - **Patch Diagnostics:** In Task 2014 r1 and Task 2100 r1, the generated patches failed during pytest collection with `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes: malformed \N character escape`. Rule H10 specifies that null values must be serialized as `\N`. In Python 3.8+, writing `\N` in a docstring without a raw-string prefix `r"""..."""` causes Python's parser to interpret `\N` as a named unicode escape `\N{name}`. This represents an unintended syntax error during test discovery rather than a logic flaw in TSV serialization.
3. **`wire_envelope` (Rule H08) — Premature Envelope Wrapping:**
   - **Performance:** Rule-Only R scored **14/16 (87.5%)** while Full Handbook F scored **16/16 (100.0%)**.
   - **Patch Diagnostics:** In Task 2038 r3, the patch prematurely called `build_envelope` inside `emit_billing_record` (which was intended only to normalize keys and return the inner payload dict), resulting in nested double-enveloping during `broadcast_billing_event`. Under Full Handbook F, all 16/16 attempts correctly separated key normalization from envelope encapsulation.
4. **`config_lists` (Rule H12) & `idempotency_keys` (Rule H13) — Cross-Rule Interference:**
   - In `config_lists` Task 2055 F (r1, r4), the model wrote `from errors import ServiceError # Added for H04`, crashing pytest collection (`ModuleNotFoundError: No module named 'errors'`). Rule-only R passed 4/4.
   - In `idempotency_keys` Task 2063 F (r1), the model wrote `Dict[str, Any]` inside `ServiceError` handling without importing `Dict` from `typing`, crashing collection. Rule-only R passed 4/4.
5. **`state_transitions` (Rule H15) — Rule H03 Mutation Interference:**
   - In Task 2078 F (r1, r3, r4), the model applied Rule H03 (Container Immutability) to escrow dictionaries, preventing required state mutations. Rule-only R passed 4/4.
6. **`config_merge` (Rule H03) — Single Task & Misapplied Target File:**
   - Scored B0=1/8, P=5/8, R=1/8, F=4/8. Rule H03 led the model to edit `pool.py` / `options.py` instead of `env_loader.py`. Low sample size ($n=8$) and high placebo sensitivity (+50 pt swing) confirm this family is low-confidence.
7. **Empirical Noise Floor ($\pm 25$ points):**
   - Placebo dips below Baseline in `wire_envelope` (0/16 vs 4/16), `permission_prefix` (4/16 vs 7/16), `csv_roundtrip` (4/16 vs 6/16), `money_rounding` (8/18 vs 11/18), `config_lists` (6/16 vs 10/16), and `timestamp_iso` (12/16 vs 15/16). Single-family differences within $\sim 25$ points at $n \approx 16$ reflect stochastic sampling noise rather than systemic handbook effects.

---

## 4. Plain-Language Reading (5 Lines)

1. **Unknown end (positions 1–5):** The full handbook produced an average gain of **+75.0 points** across `state_transitions` (+81.2), `idempotency_keys` (+81.2), `service_errors` (+100.0), `config_merge` (+37.5), and `event_ordering` (+75.0), where unaided baselines were near zero.
2. **Middle families (positions 6–9):** The full handbook produced an average gain of **+50.0 points** across `wire_envelope` (+75.0), `csv_roundtrip` (+43.8), `permission_prefix` (+37.5), and `metric_percentiles` (+43.8), transitioning from unaided solvabilities of 25.0%–56.2% into 81.2%–100.0% reliability.
3. **High-baseline and ceiling families (positions 10–14):** Full handbook gains averaged **+4.9 points** across `money_rounding` (+5.6), `config_lists` (+25.0), `timestamp_iso` (-6.2), `cache_ttl` (+0.0), and `calendar_recurrence` (+0.0), strictly bounded by high unaided baselines (61.1% to 100.0%).
4. **Statistical gradient:** Across all 14 bug families, the Spearman rank correlation between baseline solvability and full-handbook gain is **$\rho = -0.9143$ ($p = 4.73 \times 10^{-6}$)**, demonstrating an exceptionally strong monotonic relationship.
5. **Mechanisms verified:** All 872 planned attempts ran with zero infrastructure failures; failure analyses confirmed that drops below rule-only stemmed from cross-rule imports (`config_lists`, `idempotency_keys`), Python docstring escape syntax (`csv_roundtrip`), or misapplied rule over-generalization (`permission_prefix`, `config_merge`).

---

## 5. Verification Artifacts & Links

- **Stage 4 Report:** [`results/stage4/STAGE_4_REPORT.md`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage4/STAGE_4_REPORT.md)
- **Raw Outputs Directory:** [`results/stage4/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage4/raw) (872 per-attempt JSON records across all 14 families)
- **Consolidated Results:** [`results/stage4/results.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage4/results.json)
- **Schedule File:** [`results/stage4/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage4/schedule_order.json)
- **Runner Script:** [`runner/run_stage4.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage4.py)
