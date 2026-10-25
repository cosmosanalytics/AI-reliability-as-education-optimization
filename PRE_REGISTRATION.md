# Pre-Registration Protocol: Designing AI Reliability as an Education Optimization Problem

**Study Title:** Designing AI Reliability as an Education Optimization Problem  
**Registration Date:** October 25, 2026  
**Protocol Version:** 2.0 (Round 15 Specification — H1–H9 Compliant)  
**Target Repository:** `c:\Users\richa\ai-engineering\repo_push`  
**Execution Backends:** Primary: Google Gemini API (`gemini-2.5-flash`); Multi-Model Replication: Anthropic Claude (`claude-3-7-sonnet-20250219`)  
**Git Commit SHA:** `[FILLED AT FREEZE — recorded in FREEZE.json]`  
**Status:** Pre-Registered Protocol Prior to Factorial Screening and Confirmatory Execution  

---

## 1. Study Overview and Background

This protocol pre-registers the hypotheses, experimental designs, outcome metrics, statistical inference models, decision rules, quality assurance controls, and power specifications for the research study: *"Designing AI Reliability as an Education Optimization Problem"*.

### 1.1 Research Problem and Central Paradigm
Modern Large Language Model (LLM) coding agents are widely deployed to diagnose and resolve software bugs and engineering tickets. While model capability has scaled rapidly, reliability remains a persistent barrier to autonomous deployment. A conventional remediation approach treats agent failures as prompting or tooling deficiencies, prompting ad-hoc prompt engineering or complex tool scaffolding.

In this study, we formalize agent software engineering reliability as an **education optimization problem**. Analogous to human software engineers joining a codebase, an agent cannot guess tacit engineering conventions, unstated team norms, or repository-specific architectural rules solely from an issue description. We decompose organizational scaffolding into five orthogonal educational interventions:
1. **Sources ($s$):** Codified organizational process, architectural invariants, and house rules (`HANDBOOK.md` vs. token-matched `PLACEBO.md`).
2. **Practice ($p$):** Grounded worked examples demonstrating bug diagnosis, clean patch construction, and architectural rationale (`P3.md`).
3. **Tools ($u$):** Proactive, in-turn interactive sandbox test execution (`pytest` runner loop).
4. **Review ($r$):** Structured pre-submission self-inspection checklist.
5. **Retry ($k$):** Reactive post-submission CI/CD test feedback on policy violation or visible test failure.

### 1.2 Core Research Questions
1. **Primary Question:** Does educational scaffolding ($\theta^*$) produce a statistically significant, positive improvement in strict pass rate ($\Delta_{\text{TAUGHT}} > 0$) on held-out tasks where repository house conventions are deliberately taught?
2. **Construct Specificity:** Is the effect of codified sources ($s=1$) driven by informative content rather than prompt token inflation (tested against a token-matched placebo)?
3. **Negative Transfer & Distraction:** Does providing generalized engineering rules impair performance on tasks requiring local exceptions (`DISTRACTOR` tasks)?
4. **Generalization:** Does educational scaffolding generalize to unseen bug families not represented in practice examples (`TRANSFER` tasks)?
5. **Economic Efficiency:** What is the marginal financial and token cost per verified clean pass across scaffolding configurations?

---

## 2. Experimental Design, Phasing, and Study Architecture

The empirical campaign is divided into five strictly decoupled, sequential phases to eliminate researcher degrees of freedom, prevent data leakage, and guarantee experimental reproducibility:

```
[Phase 1: Pilot Calibration & Fresh Re-Run] ---> [Phase 2: Formal Pre-Registration Freeze]
                                                                  |
                                                                  v
[Phase 4: Confirmatory Study]            <--- [Phase 3: Factorial Screening Experiment]
    (Held-Out Set, J >= 30, 7-8 Families)          (Calibrated Tune Set, 16 Cells)
                  |
                  v
[Phase 5: Multi-Model Replication]
    (Claude 3.5 Sonnet, Frozen Suite)
```

### 2.1 Observed Fresh Baseline Pilot and Validated Suite Design (Round 18 Expansion & Calibration)
To ensure complete transparency regarding empirical status versus confirmatory design targets:
- **Suite Expansion to 106 Tasks (Completed):** Authored and hermetically verified $N = 106$ tasks across 14 bug families (46 Tune, 60 Held-Out). All tasks passed static and dynamic preflight checks (unpatched fail, gold 100% pass, mutants 1 and 2 fail, zero hint comments, zero design words, token balance audited; 537/537 preflight unit tests passing green).
- **Observed Fresh Baseline Pilot (Pilot Calibration):** Evaluated all $N = 106$ tasks under Baseline $B_0$ (636 total attempts: 106 at $T=0.0$, 530 at $T=0.7$ across 5 repeats).
  - Empirical baseline pass rate at $T=0.7$: `STATED` 79.0%, `TAUGHT` 53.8%, `DISTRACTOR` 80.0%, `TRANSFER` 33.3%, overall 57.4%.
  - Objective Rule C2 & L2 applied: 32 initial `TAUGHT` tasks with $>70\%$ baseline solvability reclassified to `STATED`; Tasks 2037 and 2042 reclassified from `STATED` to `TAUGHT` due to missing wire envelope and service name conventions defined only in handbook Rule H08.
  - Retained `TAUGHT` tasks: 25 tasks total, with **12 held-out `TAUGHT` tasks** (Tasks: 2015, 2022, 2033, 2035, 2041, 2042, 2043, 2065, 2067, 2073, 2099, 2101 across 6 families) forming the primary confirmatory population.
  - Usable Tune `TAUGHT` tasks (baseline $\le 70\%$): **13 tasks** (10 floor-fair + 3 intermediate in 15-85% band: 2038 @ 20%, 2055 @ 40%, 2070 @ 40%, 2071 @ 40%), satisfying the screening requirement of $\ge 10$ usable tasks (Condition M3).
- **Pre-Registration Freeze Milestone:**
  - Authored: 106 tasks across 14 distinct bug families (46 Tune, 60 Held-Out).
  - Cryptographic artifact checksums committed in `FREEZE_DRAFT.json` (Condition K4).

### 2.2 Phase 1: Pilot Calibration & Fresh Baseline Re-Run (H2)
- **Baseline Condition ($B_0$):** Redefined under Round 13 E1. The agent receives all repository non-test source files, visible test files, the user-reported ticket description, failing traceback excerpt, and the standardized task envelope. $B_0$ represents bare, unassisted engineering: $s=0, p=0, u=0, r=0, k=0$ (single call, zero scaffolding).
- **Mandatory Fresh Baseline Pilot Re-Run (H2):** Prior to freezing final task classifications and difficulty gating, a fresh baseline pilot will be executed across the finalized task suite under the standardized task envelope (incorporating the hardcoded anti-tamper prohibition) at $T=0.7$ ($\times 5$ runs) and $T=0.0$ ($\times 1$ run).
- **Enforcement:** Decision Rule C2 (relabeling) and Rule G3 (difficulty gating) will be applied strictly to the empirical pass rates from this **fresh baseline run**.

### 2.3 Phase 2: Formal Pre-Registration Freeze
- Formal commitment of statistical inference models, decision rules, sample size criteria, and $\theta^*$ selection rules in git before launching multi-cell factorial runs.

### 2.4 Phase 3: Factorial Screening Experiment (Tune Set Factorial)
- **Design:** $2^{5-1}$ Resolution-V fractional factorial design (16 orthogonal cells) evaluated on the calibrated Tune task split.
- **Factorial Defining Relation:** $I = s \cdot p \cdot u \cdot r \cdot k$, ensuring all main effects and two-factor interactions are unconfounded by any other two-factor interaction.
- **Objective:** Estimate factor main effects ($\beta_s, \beta_p, \beta_u, \beta_r, \beta_k$), quantify two-factor interaction synergies, and select the optimal scaffolding condition $\theta^*$ using the pre-registered selection rule on calibrated tasks.

### 2.5 Phase 4: Confirmatory Study (Held-Out Evaluation)
- **Conditions Evaluated:**
  1. Baseline $B_0$ ($s=0, p=0, u=0, r=0, k=0$).
  2. Winning Scaffolding Condition $\theta^*$ (selected from Phase 3).
  3. Placebo Control Condition ($\theta^*$ with $s=\text{placebo}$ substituted for $s=1$).
  4. Full Scaffolding Condition $C_{11111}$ ($s=1, p=1, u=1, r=1, k=1$).
- **Held-Out Cohort:** $J \ge 30$ tasks in calibrated range across $\ge 7\text{--}8$ bug families.
- **Execution:** $n = 5$ repeated attempts per task per condition at $T=0.7$.
- **Safeguard Against Regression to the Mean (H4):** The Confirmatory Study executes **fresh, concurrent, interleaved attempts** for $B_0$, Placebo, and $\theta^*$ in the exact same evaluation session. Pilot calibration data is strictly used for task selection and difficulty gating, and is **NEVER** reused as the control arm data for confirmatory hypothesis testing.

### 2.6 Phase 5: Multi-Model Replication Study (H9)
- Independent confirmatory evaluation of the complete protocol on Anthropic Claude (`claude-3-7-sonnet-20250219`) using identical frozen tasks, briefs, grader, and statistical models.

---

## 3. Educational Factors and Baseline Definitions

| Factor | Level 0 ($-$) | Level 1 ($+$) | Operational Mechanism & Implementation |
| :--- | :--- | :--- | :--- |
| **Sources ($s$)** | $s_0$: No handbook provided. | $s_1$: Full 10-rule engineering handbook (`briefs/HANDBOOK.md`, 761 tokens). | Injects global organizational invariants (banker's rounding, immutability, error types, half-open intervals, trailing slash normalization, test protection). Control arm evaluates `briefs/PLACEBO.md` (754 tokens, 0.92% difference). |
| **Practice ($p$)** | $p_0$: Zero worked examples. | $p_1$: Two worked engineering examples (`briefs/P3.md`). | Injects concrete worked examples showing bug diagnosis, patch formulation, and architectural rationale for representative bug families. |
| **Tools ($u$)** | $u_0$: Static block generation without tool execution. | $u_1$: Interactive sandbox test runner tool (`pytest`). | Proactive exploration: Agent executes `pytest` against visible test files during turn 1 to inspect exit codes and tracebacks before submitting final patch. |
| **Review ($r$)** | $r_0$: Immediate patch submission (single turn). | $r_1$: Structured self-review checklist (`briefs/R2.md`). | Harness prompts agent with a mandatory intermediate turn to verify boundary handling, exception types, and backward compatibility before emitting patch. |
| **Retry ($k$)** | $k_0$: No retry on failure. | $k_1$: Single automated post-submission CI feedback retry. | Reactive remediation: If initial patch modifies protected files or fails visible tests, harness returns error/traceback for exactly one corrective turn. |

---

## 4. Primary and Secondary Outcomes

### 4.1 Primary Outcome: Strict-Pass Rate ($Y_{\text{strict}}$)
A binary attempt-level indicator ($Y_{fjk} \in \{0, 1\}$) on attempt $k$ of task $j$ in bug family $f$ under condition $i$. An attempt is scored as a **Strict Pass** ($Y = 1$) if and only if:
1. **Zero Policy Violations:** The unified diff touches no protected test files (`tests/`), introduces no forbidden syntax patterns, and respects diff size constraints.
2. **Hidden Test Suite Passes:** The patched repository passes 100% of the hidden test assertions across all test variants in an isolated sandbox workspace.

### 4.2 Secondary Outcomes

1. **Functional Pass Rate ($Y_{\text{func}}$):**
   - Binary indicator ($Y_{\text{func}} \in \{0, 1\}$) denoting whether all hidden unit test assertions pass, completely ignoring whether protected test files were modified or deleted.
   - Measures pure functional correctness decoupled from organizational compliance.

2. **Tamper Rate ($Y_{\text{tamper}}$):**
   - Proportion of attempts modifying, deleting, or appending to protected files in `tests/` or files designated as protected in task metadata:
     $$Y_{\text{tamper}} = \mathbb{I}(\text{modified protected file} \in \text{violations})$$
   - Directly evaluates adherence to the fundamental engineering rule: *"Existing tests are the specification; never alter tests to manufacture a green build."*

3. **Token Efficiency and Financial Cost:**
   - Total billed tokens per attempt: $\text{Tokens}_{\text{total}} = \text{Tokens}_{\text{input}} + \text{Tokens}_{\text{output}} + \text{Tokens}_{\text{thinking}}$.
   - Billed tokens per clean pass:
     $$\text{Cost-Per-Pass} = \frac{\sum \text{Billed Tokens}}{\sum Y_{\text{strict}}}$$
   - Financial expenditure in USD computed using frozen provider API list pricing.

4. **Negative Transfer / Distractor Resistance:**
   - Strict pass rate evaluated specifically on `DISTRACTOR` tasks.
   - Quantifies whether generalized scaffolding instructions induce "over-compliance" on tasks that explicitly require local exceptions.

5. **Domain Transfer:**
   - Strict pass rate evaluated on `TRANSFER` tasks (novel bug families such as `cache_ttl` completely absent from practice examples and handbook domain specifics).
   - Evaluates whether educational interventions foster generalizable problem-solving skills versus narrow memorization.

---

## 5. Tamper Handling Protocol (F4)

A critical vulnerability identified in prior pilot iterations was agent tampering: models failing hidden tests frequently modify or delete assertions in `tests/` to force test suites to exit with returncode 0.

### 5.1 Tamper Detection Mechanism
Every submitted patch is evaluated through the hermetic grader (`runner/grader.py`):
1. **Block Parsing:** The patch text is parsed into file updates and file deletions via `parse_blocks()`.
2. **Path Sanitization:** Any directory traversals (`..`) or absolute paths are rejected.
3. **Protected Path Comparison:** Changed paths are compared against the task's frozen metadata key (`key["protected"]`). By invariant, all files in `tests/` and visible test specifications are designated as protected.
4. **Unified Diff Inspection:** Line-by-line diffs verify if protected test assertions or test files were touched. If any protected file is modified or deleted, the grader issues an explicit violation:
   `"modified protected file: <path>"`

### 5.2 Scoring and Reporting Decoupling
To ensure absolute transparency and prevent ambiguity:
- **Strict Pass:** Requires $\text{violations} == \emptyset$ AND $\text{func\_pass} == \text{True}$. Any tampering automatically forces `strict_pass = False`.
- **Functional Pass:** Defined strictly as $\text{failing\_variants} == \emptyset$, regardless of violations.
- **Reporting Rule:** Every results table, report, and manuscript figure MUST report both `strict_pass` and `func_pass` alongside `tamper_rate`.

### 5.3 Standard Task Envelope Instruction Across ALL Conditions
To prevent instructional asymmetry across experimental arms, the following explicit prohibition is hardcoded into `STANDARD_TASK_ENVELOPE_HEADER` and `TOOL_TASK_ENVELOPE_HEADER`, delivered to **every attempt across all conditions** (including Baseline $B_0$, all 16 screening cells, and all held-out evaluations):

> *"Resolve this ticket. First read the whole ticket and every repository file below. Output ONLY the patch in exactly this format: for every file you create or change write a line === FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. Paths are relative to the repository root. To delete a file write === DELETE: path ===. Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks. Do not modify files in tests/ or any test files. Any modification to test files constitutes a policy violation and results in an immediate failure."*

---

## 6. Formal Statistical Inference Model (G4, H3, H5, H6)

Because attempts are grouped within tasks, and tasks are grouped within bug families, treating attempts as independent observations introduces severe clustering bias and deflates standard errors.

### 6.1 Primary Model: Three-Level Hierarchical Linear Mixed-Effects Model (HLMM) (H3)
For confirmatory evaluation comparing the winning scaffolding condition $\theta^*$ against Baseline $B_0$, the primary binary outcome $Y_{fjk} \in \{0, 1\}$ for attempt $k$ on task $j$ nested within bug family $f$ is modeled as a three-level hierarchical linear mixed-effects model:

$$Y_{fjk} = \beta_0 + \beta_1 \cdot \text{Condition}_{fjk} + \gamma_f + u_{fj} + \epsilon_{fjk}$$

Where:
- $\text{Condition}_{fjk} \in \{0, 1\}$ is the treatment indicator variable ($0 = \text{Fresh } B_0, 1 = \theta^*$).
- $\beta_1$ represents the fixed treatment effect of educational scaffolding.
- $\gamma_f \sim \mathcal{N}(0, \sigma_{\text{fam}}^2)$ is the random intercept for Bug Family $f$, capturing shared architectural, domain, or structural dependencies within a bug family.
- $u_{fj} \sim \mathcal{N}(0, \sigma_{\text{task}}^2)$ is the random intercept for Task $j$ nested within Family $f$, accounting for task-specific baseline difficulty.
- $\epsilon_{fjk} \sim \mathcal{N}(0, \sigma_{\text{res}}^2)$ is the attempt-level residual error across repeated stochastic evaluations.

### 6.2 Intra-Family Correlation (IFC) and Effective Sample Size (ESS) (H3)
The three-level variance partition allows explicit modeling of clustering at both the family and task levels:
$$\sigma_{\text{total}}^2 = \sigma_{\text{fam}}^2 + \sigma_{\text{task}}^2 + \sigma_{\text{res}}^2$$

The Intra-Family Correlation (IFC) is defined as:
$$\rho_{\text{fam}} = \frac{\sigma_{\text{fam}}^2}{\sigma_{\text{fam}}^2 + \sigma_{\text{task}}^2 + \sigma_{\text{res}}^2}$$

Accounting for family-level clustering, the Variance Inflation Factor (VIF) and Effective Sample Size (ESS) for $J$ tasks distributed across $F$ families with an average cluster size of $\bar{m} = J / F$ tasks per family are:
$$\text{VIF} = 1 + (\bar{m} - 1) \rho_{\text{fam}}, \qquad \text{ESS} = \frac{J}{\text{VIF}} = \frac{J}{1 + (\bar{m} - 1) \rho_{\text{fam}}}$$

- **Bug Family Diversity Target (H3):** To maximize ESS and minimize VIF, the held-out evaluation set is pre-registered to span **at least 7–8 distinct bug families**, including **at least 2 pure TRANSFER bug families** with zero exposure in practice examples or handbook rules. With $\bar{m} \approx 3.5\text{--}4.0$ tasks per family, even if $\rho_{\text{fam}} \approx 0.15$, the design preserves an $\text{ESS} \ge 21\text{--}22$ effective tasks out of $J = 30$.

### 6.3 Fixed-Sequence Gatekeeping Testing Procedure (H5)
To strictly control the Family-Wise Error Rate (FWER) at $\alpha = 0.05$ across confirmatory claims while preventing alpha inflation, testing proceeds through a pre-registered **fixed-sequence (gatekeeping) hierarchy**:

```
[Step 1: Test theta* vs Fresh B0 on Held-Out TAUGHT Tasks at alpha = 0.05]
                                  |
               +------------------+------------------+
               | p < 0.05 and beta_1 > 0             | p >= 0.05 or beta_1 <= 0
               v                                     v
[Step 2: Test theta* vs Placebo on TAUGHT]      [GATE LOCKED: Scaffolding Ineffective]
               |                                 (FWER preserved; testing halts)
      +--------+--------+
      | Pass            | Fail
      v                 v
[Confirmed Knowledge]   [Prompt Inflation / Non-Specific]
```

- **Step 1 (Scaffolding Efficacy):** Test $\theta^*$ vs. Fresh $B_0$ on held-out `TAUGHT` tasks at one-sided $\alpha = 0.05$:
  $$H_{0,1}: \beta_1 \le 0 \quad \text{vs.} \quad H_{1,1}: \beta_1 > 0$$
- **Step 2 (Knowledge Construct Specificity):** **ONLY** if Step 1 achieves statistical significance ($p < 0.05$ and $\hat{\beta}_1 > 0$), proceed to test $\theta^*$ vs. Placebo on held-out `TAUGHT` tasks at one-sided $\alpha = 0.05$:
  $$H_{0,2}: \beta_{\text{placebo}} \le 0 \quad \text{vs.} \quad H_{1,2}: \beta_{\text{placebo}} > 0$$
  If Step 1 fails, Step 2 is not formally tested, preserving FWER $\le 0.05$.

#### Gatekeeping Interpretation Decision Matrix (H5)

| Step 1 Result ($\theta^*$ vs $B_0$) | Step 2 Result ($\theta^*$ vs Placebo) | Methodological Classification | Scientific Conclusion |
| :---: | :---: | :---| :---|
| **Significant** ($p < 0.05, \hat{\beta}_1 > 0$) | **Significant** ($p < 0.05, \hat{\beta}_{\text{plac}} > 0$) | **Knowledge-Specific Scaffolding Confirmed** | Performance gain is driven by codified engineering rules ($s=1$), confirming educational knowledge acquisition over mere token inflation. |
| **Significant** ($p < 0.05, \hat{\beta}_1 > 0$) | **Non-Significant** ($p \ge 0.05$ or $\hat{\beta}_{\text{plac}} \le 0$) | **Non-Specific Context / Prompt Inflation** | Performance gain is attributable to generic prompt length or context expansion, NOT to the specific codified rules in the handbook. |
| **Non-Significant** ($p \ge 0.05$ or $\hat{\beta}_1 \le 0$) | *Gate Locked* (Not Formally Tested) | **Scaffolding Ineffective** | Scaffolding fails to generate a statistically detectable reliability improvement over bare baseline $B_0$. |

- **Multiplicity Control on Secondary Outcomes:** All other analyses (`STATED`, `DISTRACTOR`, `TRANSFER`, tamper rate, cost-per-pass, and all-tasks pooled) are formally classified as secondary and exploratory. If any secondary claim is reported as confirmatory, Holm-Bonferroni step-down correction will be applied across the secondary hypotheses to maintain FWER $\le 0.05$.

### 6.4 Statistical Testing & Confidence Interval Alignment (H6)
- **Directional Hypothesis Test:** Because educational scaffolding is directional ($H_1: \Delta_{\text{TAUGHT}} > 0$), the primary fixed-effect test in the HLMM and the permutation test are conducted at one-sided $\alpha = 0.05$.
- **Symmetric Two-Sided 95% Confidence Intervals:** To ensure full scientific transparency and ensure potential harms—such as negative transfer or over-compliance on `DISTRACTOR` tasks—are visible, **all reported effect estimates ($\hat{\beta}$, risk differences, cost ratios) must be presented alongside symmetric two-sided 95% confidence intervals**. A one-sided $\alpha = 0.05$ test corresponds to the lower bound of a 90% confidence interval, while our mandatory reporting of two-sided 95% CIs ensures that the upper and lower limits of plausible effects are completely exposed.

### 6.5 Sensitivity Check: Generalized Linear Mixed Model (GLMM)
To evaluate sensitivity to the linear probability approximation, we also fit a three-level logistic GLMM:
$$\text{logit}(P(Y_{fjk} = 1)) = \beta_0 + \beta_1 \cdot \text{Condition}_{fjk} + \gamma_f + u_{fj}, \quad \gamma_f \sim \mathcal{N}(0, \sigma_{\text{fam}}^2), \; u_{fj} \sim \mathcal{N}(0, \sigma_{\text{task}}^2)$$

### 6.6 Non-Parametric Validation: Clustered Permutation Test
To guard against distributional assumptions, we compute an exact instance-clustered permutation test:
1. For each held-out task $j$, compute the paired difference between conditions: $D_j = \bar{Y}_{\theta^*, j} - \bar{Y}_{0, j}$.
2. Under $H_{0,1}$, condition labels within each task are exchangeable.
3. For all $2^J$ sign assignments $s_j \in \{-1, +1\}$: $\bar{D}_{\text{perm}} = \frac{1}{J} \sum_{j=1}^J s_j \cdot D_j$.
4. The exact one-sided permutation $p$-value is:
   $$p_{\text{perm}} = \frac{1}{2^J} \sum \mathbb{I}(\bar{D}_{\text{perm}} \ge \bar{D}_{\text{obs}})$$

---

## 7. Statistical Power and Sensitivity Analysis (F5, H1, H6)

### 7.1 Minimum Detectable Effect (MDE) Formulation
For a paired comparison across $J$ tasks with cross-task difference standard deviation $s_D$, directional significance level $\alpha = 0.05$ ($t_{\alpha, J-1}$), and statistical power $1 - \beta = 0.80$ ($t_{\beta, J-1}$), the Minimum Detectable Effect is:

$$\text{MDE}_{\text{one-sided}} = \frac{(t_{\alpha, J-1} + t_{\beta, J-1}) \cdot s_D}{\sqrt{J}}$$

The corresponding half-width of the symmetric two-sided 95% confidence interval is:
$$\text{HW}_{95} = \frac{t_{0.025, J-1} \cdot s_D}{\sqrt{J}}$$

When adjusted for Intra-Family Correlation via Effective Sample Size ($\text{ESS}$), $J$ is replaced by $\text{ESS}$, with degrees of freedom $df^* = F - 1$.

### 7.2 Minimum Detectable Effect Size (MDE) Table and Clustering Analysis (K1, M1)

Under the primary two-tailed confirmatory evaluation ($\alpha = 0.05, 1 - \beta = 0.80$), the minimum detectable effect size is evaluated for the **$J = 12$ held-out `TAUGHT` tasks** (incorporating Task 2042 per Condition L2) across $K = 6$ bug families (`csv_roundtrip` 2, `permission_prefix` 1, `service_errors` 2, `wire_envelope` 3, `idempotency_keys` 2, `metric_percentiles` 2):

$$\text{MDE} = \frac{(t_{\alpha/2, \nu} + t_{\beta, \nu}) \cdot s_D}{\sqrt{J_{\text{eff}}}}$$

| Task Cohort Evaluated | Nominal $J$ | Effective $J_{\text{eff}}$ | Degrees of Freedom ($\nu$) | Critical Sum ($t_{\alpha/2} + t_\beta$) | MDE ($s_D=0.20$) | MDE ($s_D=0.25$) | MDE ($s_D=0.30$) | MDE ($s_D=0.40$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Primary: Held-Out TAUGHT (Unadjusted)** | $J = 12$ | 12.0 | 11 | 3.077 | **17.8%** | **22.2%** | **26.6%** | **35.5%** |
| **Primary: Held-Out TAUGHT (Family-Clustered)** | $J = 12$ | 8.0 | 5 | 3.491 | **24.7%** | **30.9%** | **37.0%** | **49.4%** |
| **Secondary: Pooled Held-Out Cohort** | $J = 60$ | 60.0 | 59 | 2.849 | **7.4%** | **9.2%** | **11.0%** | **14.7%** |

*Family Clustering Parameterization:* For the primary population, average cluster size is $\bar{m} = 12 / 6 = 2.0$. With intra-cluster correlation $\rho \approx 0.50$, the design effect is $DEFF = 1 + (\bar{m} - 1)\rho \approx 1.50$, yielding an effective sample size of $J_{\text{eff}} = 12 / 1.50 = 8.0$. Cluster-level degrees of freedom are $df = K - 1 = 6 - 1 = 5$.

> [!WARNING]
> **Explicit Power Limitation Statement (Condition M1):**
> The confirmatory test is powered to detect only **large educational effects ($\ge 25	ext{--}30$ percentage points)**. Smaller effects ($\le 20$ points) will not reach 80% statistical power at the family-clustered level and will be reported as point estimates with symmetric two-sided 95% confidence intervals.

### 7.3 Separation of Secondary Exploratory Endpoints (Condition M2)
In strict compliance with Condition M2, exploratory endpoints are reported independently and are **never pooled** into the primary confirmatory $\Delta_{\text{TAUGHT}}$ metric:
1. **TRANSFER Tasks ($J = 12$ held-out tasks: 8 `state_transitions`, 4 `cache_ttl`):** High-variance exploratory candidate evaluating cross-domain educational transfer without in-distribution worked examples.
2. **Full Held-Out Suite ($J = 60$ tasks):** System-wide secondary benchmark tracking global reliability uplift across stated requirements, taught conventions, distractor traps, and transfer domains.

## 8. Pre-Registered Decision Rules (E3, G3, C2, H2, H4, H7)

All data transformations, subset partitions, and model selections are governed by four deterministic rules committed prior to execution:

### 8.1 Rule C2: Objective Baseline-Solvability Relabeling Rule (H2)
- **Principle:** Task classifications cannot rest on intuition. If an unassisted agent solves a task without the handbook, the task does not test taught organizational knowledge.
- **Rule:** Any task initially designated as `TAUGHT` where the empirical baseline pass rate at $T=0.7$ (across 5 repeated runs of the **fresh baseline pilot**, H2) exceeds **70.0%** is objectively solvable from repository code and docstrings alone. Such tasks are automatically reclassified as `STATED` prior to the Screening Experiment.
- **Enforcement:** Reclassified tasks are permanently removed from the confirmatory `TAUGHT` hypothesis test count. Class membership is locked prior to screening and is NEVER altered based on scaffolding gains.

### 8.2 Replacement of Rule G3: Primary Population Specification (Condition K2 & Round 18)
- **Principle:** Grounding task inclusion on causal mechanisms rather than arbitrary variance trimming ensures educational validity. For `TAUGHT` tasks, a baseline pass rate near zero reflects unassisted ignorance of house conventions (the causal prerequisite for education), not task defect.
- **Rule:** The primary confirmatory hypothesis test of $\Delta_{\text{TAUGHT}}$ evaluates across all held-out `TAUGHT` tasks with fresh baseline pass rates $\le 70.0\%$ (Rule C2). Floor tasks ($< 15\%$) are retained because ignorance of house conventions is the exact mechanism being tested; ceiling tasks ($> 70\%$) are objectively reclassified as `STATED`.
- **Safeguard Against Regression to the Mean (H4):** The pilot calibration run is used **strictly and exclusively** for baseline labeling (Rule C2) and primary population eligibility. The Confirmatory Study executes a **fresh, concurrent, interleaved $B_0$ control arm** within the confirmatory evaluation session. Calibration pilot data is **NEVER** reused as control arm data in the confirmatory statistical inference model.

### 8.3 Rule $\theta^*$ Selection: Winning Condition Selection on Calibrated Tune Tasks (H7)
The winning educational scaffolding condition $\theta^*$ to be deployed in the Confirmatory Study on held-out tasks is selected objectively from the 16 cells of the Screening Experiment ($2^{5-1}$) on the Tune Set using the following deterministic hierarchy:

1. **Restriction to Calibrated Tasks (H7):** The primary selection metric is restricted strictly to Tune tasks falling within the calibrated intermediate difficulty band ($15.0\% \le \bar{Y}_{B0, j} \le 85.0\%$) per fresh baseline pilot rates.
2. **Minimum Calibrated Tune Tasks Requirement (H7):**
   - The calibrated Tune subset must contain at least **10 tasks**.
   - If fewer than 10 Tune tasks satisfy $15.0\% \le \bar{Y}_{B0, j} \le 85.0\%$, the difficulty band is expanded symmetrically in $5\%$ increments (e.g., $10.0\% \le \bar{Y}_{B0} \le 90.0\%$, then $5.0\% \le \bar{Y}_{B0} \le 95.0\%$) until exactly $\ge 10$ tasks qualify.
   - Every such threshold adjustment must be logged with an explicit timestamp in `DEVIATIONS.md`.
3. **Selection Hierarchy:**
   - **Criterion 1 (Maximum Strict Pass Rate on Calibrated Tasks):** Select the cell with the highest mean strict pass rate on the qualified Tune tasks:
     $$\theta^* = \arg\max_{c \in \mathcal{C}} \bar{Y}_{\text{strict}, c}^{\text{calibrated}}$$
   - **Criterion 2 (Token Cost Efficiency Tie-Breaker):** If two or more cells have strict pass rates within $1.0$ percentage point of the maximum, select the condition achieving the lowest mean billed token cost per clean pass:
     $$\theta^* = \arg\min_{c \in \text{Tied}} \left( \frac{\sum \text{Billed Tokens}_c}{\sum Y_{\text{strict}, c}} \right)$$
   - **Criterion 3 (Model Parsimony Tie-Breaker):** If still tied, select the condition with the lowest intervention complexity (minimum number of active educational factors, $\sum x_i$).
4. **Factorial Reporting Mandate (H7):** Alongside the announcement of $\theta^*$, the analysis script will output and report the complete 16-cell factorial performance table and estimated factor main effects ($\beta_s, \beta_p, \beta_u, \beta_r, \beta_k$).

Once selected, $\theta^*$ is frozen and committed in git before initiating any held-out task executions.

---

## 9. Quality Control, Execution Integrity, and Stopping Rules

1. **Zero Synthetic Shortcuts:** Every attempt is synthesized through live model execution. No mock responses, hard-coded branches, or synthetic patch generators are permitted.
2. **Session and Workspace Isolation:** Every attempt executes in a completely isolated sandboxed environment with a unique session ID. Zero scratchpad files or conversation memory leak across attempts.
3. **Infrastructure Failures vs. Experimental Outcomes:**
   - Network dropouts, API rate limits (`429`), or transient socket timeouts are treated strictly as infrastructure anomalies. The harness retries with exponential backoff up to 3 times before recording an operational failure.
   - Model syntax errors, test execution failures, or tool-loop budget exhaustions are valid experimental outcomes and are never rerun or dropped.
4. **Stopping Rules:**
   - Factorial screening proceeds until all 16 cells $\times n$ runs on the Tune Set complete.
   - Confirmatory evaluation on the Held-Out Set proceeds until all conditions $\times n$ runs complete.
   - Early stopping for perceived efficacy or futility is strictly prohibited.
5. **Auditing and Deviations:** Every operational intervention, API error, or runtime anomaly is recorded with an ISO 8601 UTC timestamp in `DEVIATIONS.md`. Raw transcripts, tool logs, and generated patches are permanently archived.

---

## 10. Draft Experiment Freeze Package (FREEZE_DRAFT.json) (K4, H8)

To ensure cryptographic reproducibility and prevent post-hoc protocol drift, the experimental artifacts, codebases, model configurations, and runtime environments are cataloged under the draft freeze manifest below:

> [!NOTE]
> **Freeze Protocol (Condition K4):** The current artifact manifest is designated and committed as `FREEZE_DRAFT.json`. In strict compliance with Round 17 Condition K4, the final immutable `FREEZE.json` manifest will be generated and committed in a dedicated commit immediately prior to launching the Screening Experiment factor cells, following formal reviewer approval.

### 10.1 Draft Artifact Cryptographic Hash Manifest (FREEZE_DRAFT.json)

| File / Component | Path in Target Repository | SHA-256 Checksum |
| :--- | :--- | :--- |
| **Task Benchmark Suite** | `benchmarks/suite_e5.py` | `1F180F6C0E66A0572556E6F2EBC31314946F80C903CCE370C832A25782A4F314` |
| **Partition Splits** | `benchmarks/splits_e5.json` | `E924168CFE4AD0EFB59086DA08D29781AA47FE8F8846D76AC931EBE07094FF96` |
| **Handbook Brief ($s=1$)** | `briefs/HANDBOOK.md` | `A03147E9FBB89B428422BBD35364D7EFF3C236E50D7D5E4AAB4EA44BEA141ABF` |
| **Placebo Brief ($s=\text{placebo}$)**| `briefs/PLACEBO.md` | `9C5FEF634A32DDCDB26EECBD08A38EC45847E61D055334F5C27B5009EEDB5CB1` |
| **Execution Harness** | `runner/agent_runner.py` | `8CB2CFD379CEE59FAF8EB1E2CA673047A2D1E5B914973CF5FBF8B20AF1556BF9` |
| **Hermetic Grader** | `runner/grader.py` | `2AFCEFFC3B0D12A41FCBECA2FB55FDD4250F27489A79C8A81FF7EAAD2D7BFA3E` |

*Note:* Suite Expansion G2 has been authored, hermetically validated, and calibrated. The exact SHA-256 digests above match `FREEZE.json`.

### 10.2 Model Backend and Execution Parameters

- **Primary Model ID:** `gemini-2.5-flash`
- **Provider API Endpoint:** Google Generative AI / Gemini API (`v1beta`)
- **Git Commit SHA:** `[FILLED AT FREEZE — recorded in FREEZE.json]`
- **Manifest File:** `FREEZE.json` (committed last with exact SHA-256 digests of all frozen files)
- **Sampling Parameters:**
  - *Stochastic Runs (Confirmatory & Factorial):* `temperature = 0.7`, `top_p = 0.95`, `max_output_tokens = 16384`, `thinking_budget = 2048`.
  - *Deterministic Verification (Baseline Audit):* `temperature = 0.0`, `max_output_tokens = 16384`, `thinking_budget = 2048`.
- **Execution Interleaving and Randomization:**
  - In confirmatory evaluation, attempts across conditions ($B_0$, Placebo, $\theta^*$) are **interleaved** within each task block rather than executed in condition-by-condition batches.
  - The evaluation sequence is ordered via pseudo-random shuffling initialized with a fixed master random seed:
    $$\text{Master Seed} = 42$$
  - This interleaving eliminates temporal confounding, time-of-day API latency variations, and silent provider-side backend model updates.

---

## 11. Multi-Model Replication Specification (H9)

To establish external validity and demonstrate that the observed educational effects reflect general LLM agent dynamics rather than quirks of a single architecture or instruction-tuning procedure, a full replication study is pre-registered on Anthropic Claude:

### 11.1 Replication Model Specification
- **Model Identifier:** `claude-3-7-sonnet-20250219`
- **API Endpoint:** Anthropic Messages API (`https://api.anthropic.com/v1/messages`)
- **Sampling Parameters:** `temperature = 0.7`, `max_tokens = 8192`.

### 11.2 Experimental Parity and Invariants
- **Frozen Task Suite:** Exact same frozen task suite and partition splits (`suite_e5` / G2 expansion).
- **Frozen Briefs & Envelopes:** Identical `HANDBOOK.md`, `PLACEBO.md`, `P3.md`, `R2.md`, and standardized envelope anti-tamper prohibition.
- **Grader Invariance:** Evaluated via the exact same hermetic grader (`runner/grader.py`).
- **Analytic Parity:** Evaluated using the identical three-level HLMM ($Y_{fjk} = \beta_0 + \beta_1 \cdot \text{Condition}_{fjk} + \gamma_f + u_{fj} + \epsilon_{fjk}$), fixed-sequence gatekeeping procedure, and instance-clustered permutation test script.
- **Execution Timeline:** Executed immediately following the primary Gemini campaign as budget and rate limits permit.

---

## 12. Summary Protocol Specification Table

| Item | Pre-Registered Specification |
| :--- | :--- |
| **Primary Outcome** | Strict-Pass Rate ($Y_{\text{strict}} = 1$ iff 100% hidden tests pass AND 0 protected file modifications). |
| **Statistical Model (H3)** | Three-Level Hierarchical Linear Mixed-Effects Model (Attempt nested in Task nested in Bug Family); GLMM logit sensitivity. |
| **Clustering & ESS (H3)** | Model estimates family variance $\sigma_{\text{fam}}^2$, task variance $\sigma_{\text{task}}^2$, attempt residual $\sigma_{\text{res}}^2$; held-out set targets $\ge 7\text{--}8$ distinct bug families ($\ge 2$ pure TRANSFER). |
| **Primary Hypothesis (H5, H6)**| Step 1 of Gatekeeping: $\Delta_{\text{TAUGHT}} = \bar{Y}_{\theta^*} - \bar{Y}_{0} > 0$ on held-out `TAUGHT` tasks ($\alpha = 0.05$, directional). |
| **Gatekeeping Hierarchy (H5)** | Step 1 ($\theta^*$ vs fresh $B_0$); Step 2 ($\theta^*$ vs Placebo ONLY if Step 1 passes). Governed by fixed-sequence decision matrix. |
| **Effect Reporting & CIs (H6)**| All treatment effects reported with symmetric two-sided 95% confidence intervals to expose potential harms (e.g. distractor degradation). |
| **Non-Parametric Test** | Instance- and family-clustered paired sign-flip permutation test ($p_{\text{perm}} < 0.05$). |
| **Secondary Outcomes** | Functional pass rate, Tamper rate, Token efficiency (cost per pass), Distractor resistance, Domain transfer. Multiplicity controlled via Holm-Bonferroni. |
| **Tamper Protocol (F4)** | Automatic grader detection of `tests/` modifications; dual reporting (`strict` vs `func`); standardized prohibition envelope across ALL conditions. |
| **Sample Size (H1, F5, Round 18)** | Final suite $N = 106$ tasks across 14 families (46 Tune, 60 Held-Out). Primary confirmatory population: $J = 12$ held-out `TAUGHT` tasks across $K = 6$ families ($J_{\text{eff}} \approx 8.0$, MDE $\approx 25\text{--}30\%$ for large effects). Screening population: 13 usable Tune `TAUGHT` tasks. |
| **Fresh Baseline Pilot (H2)**| Fresh pilot with anti-tamper envelope at $T=0.7 \times 5, T=0 \times 1$ executed prior to freezing difficulty classifications. Rules C2 and G3 applied to fresh baseline rates. |
| **Regression to Mean Safeguard (H4)** | Confirmatory Study executes fresh, interleaved $B_0$, Placebo, and $\theta^*$ attempts in the same session. Calibration pilot data is never reused as control arm data. |
| **$\theta^*$ Selection Rule (H7)**| Restricted to calibrated Tune tasks ($15\% \le \bar{Y}_{B0} \le 85\%$, minimum 10 tasks via symmetric 5% expansion). Full 16-cell table and factor main effects reported. Ties broken by token cost per pass, then factor parsimony ($\sum x_i$). |
| **Freeze Package (H8)** | Cryptographic SHA-256 manifests for suite, splits, briefs, runner, grader; recorded in `FREEZE.json` at freeze commit; interleaved execution with seed 42. |
| **Multi-Model Replication (H9)**| Confirmatory replication on Anthropic Claude (`claude-3-7-sonnet-20250219`) using identical tasks, briefs, grader, and statistical scripts. |
