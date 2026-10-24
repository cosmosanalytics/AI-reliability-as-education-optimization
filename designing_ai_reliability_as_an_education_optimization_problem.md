# Designing AI Reliability as an Education Optimization Problem

**Author:** Zhao  
**Date:** October 2026  
**Status:** Research Manuscript (Revised Empirical Draft)

---

## Abstract

Artificial intelligence agents demonstrate impressive average-case performance on complex software engineering benchmarks, yet their deployment remains hindered by high variance, brittle edge-case behavior, and silent failures. Current approaches to agent reliability rely largely on post-hoc prompt engineering or unstructured multi-agent deliberation, often evaluating systems on single-pass runs where run-level noise obscures true capability differences. In this paper, we formalize agent reliability as a constrained education optimization problem. Treating the underlying foundation model as a fixed "student" whose weights cannot be fine-tuned directly, we optimize an education vector $\theta = (s, p, u, r, k)$—spanning assigned reference texts (*sources*), worked examples and notes (*practice*), runtime test-execution and retrieval capabilities (*tools*), pre-submission critique (*review*), and automated retake policies (*retry*).

We evaluate this formulation on a tamper-aware software engineering benchmark of 20 tasks featuring hidden unit test suites and strict protected-file constraints, tracking approximately 1,950 graded attempts across single-factor ablations, a $2^{5-1}$ resolution-V fractional factorial design, and five progressively harder ticket sets using Claude Sonnet subagents (exact version not recorded). Our empirical results uncover critical evaluation realities: (1) functional code generation hits a 95–100% ceiling on self-contained repositories, masking component differences across sources, practice, tools, and review; (2) observed failures are dominated by run-level behavioral clustering (specifically, an agent's run-wide disposition to edit protected test files) where the effective sample size is the number of cohort runs ($N_{\text{eff}} = 5$) rather than ticket attempts ($N = 60$), rendering single-run rankings spurious; (3) an automated policy-check retry rescued 17 of 17 compliance failures in retry cells on the first resubmission; and (4) apparent drops in capability on harder tasks stem from omitted specification conventions rather than algorithmic deficiency. We provide an evaluation protocol, sample-complexity bounds, and a surrogate mixed-integer programming (MIP) knapsack formulation for cost-constrained curriculum optimization.

---

## 1. Introduction

Autonomous software engineering agents powered by large language models (LLMs) are increasingly tasked with resolving real-world repository issues, synthesizing tests, and automating refactoring pipelines. While benchmark leaderboards report rapid gains in average solve rates, engineering teams face a different operational reality: AI agents are inherently stochastic, prone to silent regressions, and susceptible to catastrophic run-to-run inconsistency. A configuration that succeeds on 80% of tasks during one deployment pass may plunge to 40% on identical tasks simply due to sampling variance, conversational drift, or subtle prompt modifications.

Crucially, standard evaluation practices exacerbate this issue. Most benchmark protocols evaluate an agent configuration on a single run over a task suite, treating each solved ticket as an independent Bernoulli trial. As we demonstrate empirically, this independence assumption fails: agent behaviors—such as the tendency to rewrite existing test files or misinterpret file protection policies—cluster strongly within an execution run. A single run with a pathological habit can move eight or ten tickets simultaneously, creating illusory performance deltas between agent configurations that vanish upon re-testing.

To address the lack of systematic design principles for agent reliability, we propose an operational paradigm: **AI reliability as an education design problem**. Consider a university that must guarantee its graduates solve novel, unseen engineering problems cleanly and consistently. The university cannot modify the innate cognitive capacity of the student (the frozen pre-trained base model weights). Instead, it must optimize the student's *educational curriculum*:
1. **Sources ($s$):** What reference material, system rules, and API manuals are provided (e.g., bare prompt $S_1$, 5-rule book $S_2$, 16-rule book $B$, or student notes $S_4$)?
2. **Practice ($p$):** How does the student prepare—through rote practice ($P_1$), student-authored study notes ($P_2$), or worked examples ($P_3$)?
3. **Tools ($u$):** What instruments are permitted during the exam ($U_1$ none, $U_2$ test runner, $U_3$ grep, $U_4$ vector search, $U_5$ code graph)?
4. **Review ($r$):** Must the student perform structured self-critique ($R_2$) or submit to an independent reviewer pass ($R_3$) before submission?
5. **Retry ($k$):** Under what conditions and feedback signals may a student resubmit failed work ($k_1$ single-pass, $k_2$ one retry, $k_3$ two retries)?

Exams are administered under strict conditions: solutions are evaluated against **hidden functional tests**, and **protected answer keys** (test files) cannot be altered. A student who edits the test suite instead of repairing the implementation receives an immediate score of zero for tampering.

### Research Questions
- **RQ1 (Component Efficacy):** Which dimensions of the education vector $\theta$ yield statistically significant gains in out-of-sample functional correctness and policy compliance?
- **RQ2 (Noise vs. Signal in Agent Evaluation):** How much variance across reported agent configurations is driven by run-level clustering versus true design differences, and what evaluation protocol is required to establish statistical significance?
- **RQ3 (Constrained Education Optimization):** Can automated search (ablation-driven knapsack programming, successive halving, or Bayesian optimization) discover optimal, cost-bounded curricula under noisy, black-box evaluations?

### Summary of Contributions
1. **Mathematical Formulation:** We state the education optimization problem as a stochastic objective balancing expected out-of-sample reliability against run-to-run variance, subject to token cost budgets, zero-tamper constraints, and silent-failure penalties.
2. **Tamper-Aware Software Engineering Benchmark:** We implement a 20-ticket benchmark featuring visible vs. hidden tests, hidden unit test verification, and programmatic file protection checks, establishing clear separation between functional correctness and policy adherence.
3. **Empirical Evaluation of Educational Scaffolding (~1,950 Attempts):** Through multi-run pilots, one-at-a-time (OATA) ablations, a $2^{5-1}$ resolution-V fractional factorial experiment, and five progressive hardening stages using Claude Sonnet subagents (exact version not recorded), we systematically analyze the interactions of sources, practice, tools, review, and retries.
4. **Methodological Diagnosis & Honest Findings:** We demonstrate why prompt-sized benchmarks produce severe ceiling effects that mask curriculum differences, show that retry mechanisms effortlessly resolve rule-compliance errors (rescuing 17 of 17 failures), and prove that effective sample size in multi-ticket agent evaluations is governed by run count ($N_{\text{eff}} = m$) rather than attempt count ($N = m \cdot n$).

---

## 2. Related Work

### 2.1 Prompt Optimization and Instruction Tuning
Automated instruction tuning has evolved from manual prompt hacking to automated search techniques. DSPy provides declarative programming abstractions over LLMs, optimizing teleprompters and few-shot demonstrations via bootstrapped demonstrations. APE (Automatic Prompt Engineer) and OPRO (Optimization by PROmpting) frame instruction synthesis as black-box optimization guided by LLM proposers. However, existing prompt optimizers typically treat the prompt as an undifferentiated string of tokens, conflating syllabus rules, few-shot worked examples, and runtime operational constraints. Our framework separates these axes into formal orthogonal variables ($s, p, u, r, k$).

### 2.2 Software Engineering Benchmarks and Grading Pitfalls
Benchmarks such as SWE-bench, HumanEval, and RepoEval assess language models on programming tasks. However, SWE-bench evaluations frequently encounter grading artifacts: agents can inadvertently edit reproduction tests, fail due to environmental flakiness, or overfit to visible test outputs. Recent literature has highlighted the vulnerability of benchmark evaluations to "test tampering," where an agent modifies test assertions to force a passing exit code. Our benchmark enforces strict file isolation and hidden test execution, ensuring that passing grades reflect authentic behavioral repairs.

### 2.3 Reliability, Variance, and Statistical Rigor in LLM Evaluation
The machine learning literature has increasingly warned of low statistical power in LLM evaluations. Sampling temperature, prompt ordering, and system prompt phrasing induce substantial run-to-run variance. Despite this, empirical studies regularly report performance comparisons based on single-seed evaluations across benchmark splits. We formalize this critique through run-level permutation testing and Wilson score confidence bounds, quantifying how un-modeled run clustering generates spurious statistical significance.

### 2.4 Tool Use and Retrieval-Augmented Generation (RAG)
Agents equipped with tool access—such as ReAct, Toolformer, and SWE-agent—interact with external environments via bash commands, symbolic search, and language server protocols. While tool access is widely assumed to improve problem solving monotonically, excessive tool output can induce context saturation and cognitive distraction. In our study, we systematically isolate the availability versus actual utilization of test runners, grep, and retrieval tools.

### 2.5 Hyperparameter and Combinatorial Search Under Noise
Optimizing educational curricula maps directly to combinatorial optimization under stochastic evaluations. Techniques such as Successive Halving (Hyperband), Bayesian Optimization with Gaussian Process surrogates, and evolutionary algorithms are well-suited for noisy black-box objectives. Where rule interactions are near-additive, Mixed-Integer Linear Programming (MIP) provides exact knapsack solutions over rule configurations under strict token budgets.

---

## 3. Problem Formulation

We consider a fixed, frozen base foundation model $\mathcal{M}$ (the "student"). The agent operates in an environment defined by an unknown distribution of software engineering tasks $\mathcal{D}$. The task distribution is partitioned into a training/tuning distribution $\mathcal{D}_{\text{tune}}$ and a strictly held-out exam distribution $\mathcal{D}_{\text{unseen}}$, where:
$$\mathcal{D}_{\text{unseen}} \cap \mathcal{D}_{\text{tune}} = \emptyset$$

### 3.1 The Education Design Vector
The university designs an educational curriculum parameterized by a discrete vector $\theta$:
$$\theta = (s, p, u, r, k) \in \Theta = S \times P \times U \times R \times K$$

Where:
- **$s \in S$ (Sources):** Reference documentation, operational guidelines, and system constraints provided in the context window.
  - $s_1$: None (bare instruction).
  - $s_2$: Short Book (5 foundational engineering rules: W01, W02, W05, W07, W14).
  - $s_3$: Full Book (16 comprehensive rules: W01 through W16).
  - $s_4$: Student-Written Notes (self-distilled operational heuristics).
  - $s_5$: Ablation-Tuned Book (rules selected via empirical knapsack optimization).
- **$p \in P$ (Practice):** Pedagogical preparation prior to unseen task evaluation.
  - $p_1$: Zero-shot (no prior ticket interaction).
  - $p_2$: Student-Authored Study Notes (agent processes practice tickets and generates persistent notes).
  - $p_3$: Worked Examples (expert few-shot demonstrations showing full problem-solution traces).
- **$u \in U$ (Tools):** Runtime capabilities available within the exam environment.
  - $u_1$: None (static generation of patch diff).
  - $u_2$: Interactive Test Runner (ability to execute visible unit tests).
  - $u_3$: Test Runner + Grep (symbolic lexical search).
  - $u_4$: Test Runner + Grep + Vector Search (dense semantic retrieval).
  - $u_5$: Test Runner + Grep + Code Graph (structural AST and call-graph navigation).
- **$r \in R$ (Review):** Verification mechanisms applied prior to official patch submission.
  - $r_1$: None (immediate patch submission).
  - $r_2$: Self-Review Checklist (explicit reflection prompt validating edge cases and policy constraints).
  - $r_3$: Independent Critic Pass (a secondary agent instance critiques and suggests edits).
- **$k \in K$ (Retry Policy):** Automated retake protocol following failed pre-submission checks.
  - $k_1$: Single-pass (no retry permitted).
  - $k_2$: One retry conditioned on automated policy/test feedback.
  - $k_3$: Two retries conditioned on automated policy/test feedback.

The total combinatorial search space contains $|\Theta| = 5 \times 3 \times 5 \times 3 \times 3 = 675$ design configurations. Certain pairings are conditionally dependent: retries conditioned on test failures ($k_2, k_3$) require a test execution tool ($u \ge u_2$); without runtime execution, retries can only be triggered by static policy checkers.

### 3.2 Evaluation Metrics and Stochastic Outcomes
Let $x \sim \mathcal{D}_{\text{unseen}}$ represent an unseen task ticket, and let $\omega \sim \Omega$ represent the stochastic execution noise of the agent. The environment yields two binary indicators:
1. **Functional Correctness $C(\theta, x, \omega) \in \{0, 1\}$:** Indicator that the patch resolves the issue and passes all hidden verification tests.
2. **Policy Tampering $T(\theta, x, \omega) \in \{0, 1\}$:** Indicator that the agent modified a protected file (e.g., test suites, configuration harnesses, grading harnesses).

A task attempt is classified as a **Strict Clean Pass** if and only if it is functionally correct and completely untampered:
$$Y(\theta, x, \omega) = C(\theta, x, \omega) \cdot \big(1 - T(\theta, x, \omega)\big)$$

### 3.3 The Optimization Objective
We define out-of-sample **Reliability** $R(\theta)$ as the expected strict pass rate:
$$R(\theta) = \mathbb{E}_{x \sim \mathcal{D}_{\text{unseen}}, \, \omega \sim \Omega}\big[ Y(\theta, x, \omega) \big]$$

In practice, high variance between cohort runs is unacceptable. Let an "exam sitting" $j \in \{1, \dots, m\}$ consist of $n$ unseen tickets $x_{1}, \dots, x_{n}$. The empirical pass rate on sitting $j$ is:
$$\hat{p}_j(\theta) = \frac{1}{n} \sum_{i=1}^{n} Y(\theta, x_i, \omega_{ij})$$

The across-run variance is:
$$V(\theta) = \operatorname{Var}_j\big(\hat{p}_j(\theta)\big) = \frac{1}{m-1} \sum_{j=1}^{m} \big(\hat{p}_j(\theta) - \bar{p}(\theta)\big)^2$$

The optimization problem is:
$$\max_{\theta \in \Theta} \; J(\theta) = R(\theta) - \lambda \, V(\theta)$$
$$\text{subject to:}$$
1. **Cost Budget:** $\mathbb{E}[\operatorname{cost}(\theta)] \le B$.
2. **Zero Tampering:** $\Pr_{x, \omega}[T(\theta, x, \omega) = 1] = 0$.
3. **Escalation of Uncertainty:** $\Pr_{x, \omega}[\neg C \wedge \neg\text{escalate}] \le \varepsilon$.
4. **Generalization Guarantee:** $\mathcal{D}_{\text{unseen}} \cap \mathcal{D}_{\text{tune}} = \emptyset$.

### 3.4 Estimation and Selection Rule
Candidate designs are compared via the conservative lower bound of the two-sided $95\%$ Wilson score confidence interval ($\alpha = 0.05, z = 1.96$):
$$\mathrm{LB}(\theta) = \frac{\hat{R} + \frac{z^2}{2N} - z\sqrt{\frac{\hat{R}(1-\hat{R})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$

The optimal design is selected according to:
$$\theta^\star = \arg\max_{\theta \in \Theta_{\text{feasible}}} \; \Big( \mathrm{LB}(\theta) - \lambda \, \hat{V}(\theta) \Big)$$

### 3.5 Surrogate Knapsack MIP Formulation
When optimizing Sources $s$ over $M$ discrete rules $\{r_1, \dots, r_M\}$, we formulate an integer knapsack model using empirically estimated marginal gains $g_i$ and estimated token costs $c_i$:
$$\max_{x \in \{0,1\}^M} \sum_{i=1}^{M} g_i x_i - \gamma \sum_{i=1}^M c_i x_i$$
$$\text{s.t.} \quad \sum_{i=1}^{M} c_i x_i \le B, \qquad x_i + x_j \le 1 \quad \forall (i, j) \in \mathcal{K}$$

Where $\mathcal{K}$ contains conflicting pairs (e.g., $W13$: "Put regression test in existing test file" vs. $W05$: "Never edit, delete or weaken existing tests").

---

## 4. Benchmark Architecture and Tamper-Aware Grading

```
+---------------------------------------------------------------------------------------+
|                                    BENCHMARK HARNESS                                  |
|                                                                                       |
|  +------------------------------------+             +------------------------------+  |
|  | Task Specification (tasks.py)      |             | Protected Repository         |  |
|  | 12 Held-Out Tickets (t2,t4..t20)   |             | (Read-Only Test Files)       |  |
|  +------------------+-----------------+             +--------------+---------------+  |
|                     |                                              |                  |
|                     v                                              v                  |
|  +------------------------------------+             +------------------------------+  |
|  | AI Student Cohort (theta=s,p,u,r,k)|             | Tamper Policy Checker        |  |
|  | Synthesizes Patch Blocks           | -- Patch -> | core.evaluate(repo,patch,key)|  |
|  +------------------+-----------------+             +--------------+---------------+  |
|                                                                    |                  |
|                                            +-----------------------+                  |
|                                            | Tamper Check                             |
|                                            v                                          |
|                               +---------------------------+                           |
|                               | Did patch alter protected |                           |
|                               | files or forbidden paths? |                           |
|                               +-------------+-------------+                           |
|                                             |                                         |
|                       +---------------------+---------------------+                   |
|                       | Clean Files Only                          | Modified Tests    |
|                       v                                           v                   |
|          +--------------------------+                +-------------------------+      |
|          | Fresh Sandbox Execution  |                | TAMPER VERDICT          |      |
|          | run_pytest(hidden_suite) |                | T=1, Strict Score = 0   |      |
|          +------------+-------------+                +-------------------------+      |
|                       |                                                               |
|           +-----------+-----------+                                                   |
|           | All Hidden Tests Pass | Hidden Tests Fail                                 |
|           v                       v                                                   |
|  +------------------+    +------------------+                                         |
|  | STRICT PASS      |    | FUNCTIONAL FAIL  |                                         |
|  | C=1, T=0         |    | C=0, T=0         |                                         |
|  +------------------+    +------------------+                                         |
+---------------------------------------------------------------------------------------+
```

### 4.1 Task Suite Design
The benchmark comprises 20 realistic Python software engineering tickets defined in `harness/tasks.py`:
- **Tuning Set ($\mathcal{D}_{\text{tune}}$):** 8 practice tickets (`t1, t3, t6, t9, t12, t15, t18, t19`).
- **Held-Out Final Exam ($\mathcal{D}_{\text{unseen}}$):** 12 tickets (`t2, t4, t5, t7, t8, t10, t11, t13, t14, t16, t17, t20`).

### 4.2 Tamper Isolation and Hidden Test Verification
In `harness/core.py`, the `evaluate(repo, patch_text, key)` function enforces strict boundary contracts:
```python
def evaluate(repo, patch_text, key):
    files, deletes = parse_blocks(patch_text)
    for p in list(files) + list(deletes):
        if bad_path(p): viol.append('path outside the repository: ' + p)
    for p in key.get('protected', []):
        if p in changed: viol.append('modified protected file: ' + p)
    for pat in key.get('forbidden', []):
        if any(re.search(pat, l) for l in added_text):
            viol.append('forbidden pattern added: ' + pat)
    d = build_dir(repo, files, deletes)
    rc, txt = run_pytest(d, key.get('visible_paths', ['tests']))
    for v in key.get('variants', []):
        d = build_dir(repo, files, deletes, overlay=v.get('overlay'))
        rc, txt = run_pytest(d, v.get('paths', ['tests']))
        ok = (rc == 0) if v['expect'] == 'pass' else (rc == 1)
```

---

## 5. Education Components and Optimization Methods

### 5.1 Search Methods and Algorithmic Complexity
Evaluating every point in the full design grid ($\Theta = 675$) across 12 tickets and 3 independent runs would require $24{,}300$ attempts ($\approx 165\text{ M}$ tokens). We formalize six alternative search mechanics:
- **Grid Enumeration:** Hand-picked vectors ($E1, E2$).
- **OATA Ablation:** Single-coordinate perturbation relative to baseline ($E3a$).
- **Resolution-V Fractional Factorial ($2^{5-1}$):** Confounding higher-order interactions ($I = s p u r k$) to measure unbiased main effects and all 10 two-way interactions ($E3b$).
- **Successive Halving / UCB:** Allocating run budgets dynamically.
- **Bayesian Optimization:** GP surrogate optimization over discrete embeddings.
- **MIP Knapsack Surrogate:** Polynomial-time knapsack solution over additive rule marginals.

### 5.2 Computational Cost and Token Accounting
We measure exact prompt token counts across all brief configurations using the standard BPE tokenizer (`cl100k_base`, with verified equivalence under `o200k_base`):
- **Per-Attempt Tokens:** $\approx 6{,}800$ tokens per attempt based on the pilot's 12-ticket average of $\approx 82{,}000$ tokens per engineer run (30 to 58 seconds per run, tools off).
- **Exact Brief Token Footprints (`cl100k_base`):**
  - **Bare Instruction ($S_1$, `S1.md`):** 136 chars / 20 words = **26 tokens**.
  - **Full 16-Rule Process Book ($B / s_3$, `B.md`):** 4,238 chars / 696 words = **871 tokens** (incremental over $S_1$: $+845$ tokens).
  - **Short 5-Rule Book ($S_2$, `S2.md`):** 1,530 chars / 263 words = **323 tokens** (incremental over $S_1$: $+297$ tokens).
  - **Student Study Notes ($S_4$, `S4.md`):** 3,023 chars / 487 words = **623 tokens** (incremental over $S_1$: $+597$ tokens).
  - **Worked Examples ($P_3$, `P3.md`):** 8,162 chars / 1,220 words = **1,943 tokens** (incremental over $B$: $+1{,}072$ tokens).
  - **Interactive Test Runner Brief ($U_2$, `U2.md`):** 4,657 chars / 760 words = **980 tokens** (incremental over $B$: $+109$ tokens).
  - **Self-Review Checklist ($R_2$, `R2.md`):** 4,684 chars / 770 words = **966 tokens** (incremental over $B$: $+95$ tokens).

---

## 6. Experimental Design

Our empirical study comprises approximately 1,950 graded attempts executed across five experimental phases using Claude Sonnet subagents (exact version not recorded):
- **$E1$: Initial Source Comparison (Rewritten Process Book):** 4 designs $\times$ 12 tickets $\times$ 3 runs (144 attempts).
- **$E2$: Source Comparison Under Original Book:** 4 designs $\times$ 12 tickets $\times$ 3 runs (144 attempts).
- **$E3a$: One-at-a-Time (OATA) Coordinate Ablation:** 8 designs $\times$ 12 tickets $\times$ 5 runs (480 attempts).
- **$E3b$: Initial Fractional Factorial ($2^{5-1}$):** 16 cells $\times$ 12 tickets $\times$ 5 runs (960 attempts, 55 new runs plus 5 reused cells).
- **$E3c$: Hardening Progression:** Five progressively harder ticket sets (Hard, Hard2, Hard3, Hard4 first version, Hard4 final; 226 attempts total).

---

## 7. Results and Empirical Analysis

### 7.1 The Ranking Inversion Dilemma ($E1$ vs. $E2$)
In pilot experiment $E1$, evaluating the rewritten process book suggested clear superiority for concise instructions: Short Book achieved 36/36, whereas Full Book collapsed to 20/36. 

However, repeating the exact experiment in $E2$ with the original 16-rule book completely reversed this ranking: Full Book achieved 36/36, while Short Book dropped to 28/36. Functional code correctness was 143/144 across all attempts; all failures were driven by policy violations where the agent added regression tests to protected test files.

### 7.2 One-at-a-Time Coordinate Ablation ($E3a$)
Table 1 reports the strict pass rates, run distributions, tamper counts, Wilson 95% lower bounds, and exact two-sided permutation test $p$-values versus Baseline $B$.

**Table 1: One-at-a-Time Ablation Results ($E3a$).**  
*5 independent runs per design $\times$ 12 held-out tickets (60 attempts per cell). Strict Pass requires passing all hidden tests without modifying protected files.*

| Design Configuration | Strict Pass | Per-Run Pass Rates | Tamper Count | Wilson 95% LB | Exact Permutation $p$ vs. $B$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline $B$ (Full Book)** | **60/60** | **1.00, 1.00, 1.00, 1.00, 1.00** | **0** | **0.941** | — |
| $S_1$ (Source = None) | 52/60 | 1.00, 0.33, 1.00, 1.00, 1.00 | 8 | 0.761 | $p = 1.000$ |
| $S_2$ (Source = Short Book) | 52/60 | 1.00, 0.33, 1.00, 1.00, 1.00 | 8 | 0.761 | $p = 1.000$ |
| $S_4$ (Source = Student Notes) | 42/60 | 1.00, 0.33, 0.33, 0.83, 1.00 | 18 | 0.582 | $p = 0.167$ |
| $P_2$ (Practice = Own Notes) | 59/60 | 1.00, 0.92, 1.00, 1.00, 1.00 | 1 | 0.908 | $p = 1.000$ |
| $P_3$ (Practice = Worked Examples)| 60/60 | 1.00, 1.00, 1.00, 1.00, 1.00 | 0 | 0.941 | $p = 1.000$ |
| $U_2$ (Tools = Test Runner) | 60/60 | 1.00, 1.00, 1.00, 1.00, 1.00 | 0 | 0.941 | $p = 1.000$ |
| $R_2$ (Review = Self-Checklist) | 60/60 | 1.00, 1.00, 1.00, 1.00, 1.00 | 0 | 0.941 | $p = 1.000$ |

- **Severe Ceiling:** Baseline $B$ achieved 60/60 clean passes. Additions such as Worked Examples ($P_3$), Test Runners ($U_2$), and Checklists ($R_2$) were tied with baseline; they did not hurt, but could not show a marginal benefit on this task set.
- **100% Functional Correctness:** Every single failure across all 480 attempts passed hidden tests. Functional correctness was invariant to the education design.
- **Run-Level Failure Clustering:** In $S_1$ and $S_2$, all 8 failures occurred in a single cohort run (Run 2), where the agent adopted a habit of adding regression tests to existing test files. Because the effective sample size is 5 runs rather than 60 attempts, permutation testing confirms that no design achieves statistical significance ($p \ge 0.167$), despite pooled attempt-level Fisher exact testing showing $p = 1.7 \times 10^{-6}$ for $S_4$ vs. $B$.

### 7.3 Resolution-V Fractional Factorial Experiment ($E3b$)
To test for multi-way interactions and evaluate automated retries, we executed a 16-cell $2^{5-1}$ fractional factorial design ($N = 960$ attempts, $\text{df} = 64$):
- **First-Attempt Baseline:** 936 of 960 attempts passed strictly; all 960 passed functional tests. All 24 first-attempt failures were test-file modifications occurring exclusively in Run 2 within no-book cells (`0000`, `0010`, `0001`). Every cell containing the Full Book achieved a perfect 60/60.
- **The Power of Policy Retries ($k$):** For cells with retry enabled ($k_2, k_3$), the policy checker detected protected-file modifications and returned feedback: `"Policy Error: Do not modify protected test files."` On the first resubmission, **17 out of 17 failing attempts (100%) in retry cells were completely rescued**, eliminating the test edits while preserving the functional fix. The remaining 7 failures in the entire matrix resided exclusively in cell `0001` (No Book, Checklist Only), which lacked retry permissions ($k^-$).
- **Linear Model Effects:** Fitting an ordinary least squares model on run-level pass rates ($\sigma_{\text{pooled}} = 0.065, 64 \text{ df}$) revealed that all main effects and two-way interaction coefficients hovered at $\beta = \pm 0.015$ with $t = \pm 1.0$ ($p > 0.30$). When evaluated at the run level, no individual factor statistically separated from the noise floor.
- **Tool Neglect:** Inspection of execution scratchpads revealed that although the Test Runner ($u_2$) was provided in 8 of the 16 cells, agents only invoked the tool in 2 runs. Offering tools does not guarantee agent utilization when the agent possesses high internal confidence.

### 7.4 Hardening the Benchmark ($E3c$): The Ceiling Persists
To break the 100% ceiling and force separation across $(s, p, u, r, k)$, we tested five successively harder ticket sets (Table 2).

**Table 2: Progressive Benchmark Hardening Progression ($E3c$).**

| Benchmark Suite | Structural Modification | Compared Arms | Strict Pass Rate | Key Finding |
| :--- | :--- | :---: | :---: | :--- |
| **Original (12 tickets)** | Standard SWE tickets | 16-cell factorial | 936/960 (97.5%) | Severe ceiling; 100% functional pass rate. |
| **Hard (12 tickets)** | Thin visible tests, stubbed modules | Full Book vs. None | 58/60 vs. 59/60 | No separation; agent infers full logic from context. |
| **Hard2 (6 tickets)** | Multi-file repos, symptom-only bugs | Full Book vs. None | 30/30 vs. 30/30 | Agent tracks multi-file dependencies in a single shot. |
| **Hard3 (1 ticket)** | 136-line repo, 9 seeded bugs, docstrings stripped | Full Book vs. None | 2/2 vs. 2/2 | Perfect repair despite dense bug density. |
| **Hard4 v1 (7 tickets)** | 50% tests hidden; test runner provided to one arm | No Tools vs. Tools | 12/21 vs. 11/21 | Both arms fail identical 3 tickets (57% pass). |
| **Hard4 Final (7 tickets)**| Added 1 specification sentence for unstated behaviors | No Tools vs. Tools | 21/21 vs. 20/21 | Ceiling restored; test runner actively used in 21/21 runs. |

#### Detailed Autopsy of $E3c$:
- **Why Simple Hardening Fails:** Modern frontier LLMs easily synthesize code for repositories that fit within prompt context. Adding multiple seeded bugs, stripping docstrings, or providing symptom-only bug reports merely increases prompt processing time; it does not induce reasoning failure.
- **The Artifact of Hard4 v1:** In the initial version of Hard4 (`benchmarks/hard4_tasks.py`), performance plummeted to $\approx 57\%$ in both arms. However, detailed log inspection revealed that this was entirely an artifact of missing requirements. Three tickets required arbitrary undocumented conventions:
  - Ticket `h602`: parsing environment string boolean mappings (`EXTRA[202]`);
  - Ticket `h604`: raising a `ValueError` on an unterminated quotation mark (`EXTRA[204]`);
  - Ticket `h605`: treating wildcard action `*` as applying to every action (`EXTRA[205]`).
  Both arms failed these tickets in 100% of runs because the information was physically absent from the prompt.
- **Verification of Tool Use:** When Hard4 Final supplied the missing specification lines, pass rates rebounded to 100% (21/21 vs. 20/21). Crucially, the pytest cache confirmed that the test runner was actively invoked in all 21 runs of the tool arm. Yet, on this sample size (21 attempts per arm across 3 runs), runtime feedback showed no detectable difference compared to static code generation. When an agent's mental model of code generation is accurate, runtime feedback provides no measurable accuracy gain.

---

## 8. Discussion and Methodological Guidelines

### 8.1 The Unit-of-Analysis Fallacy in Agent Evaluation
The central methodological takeaway of this study is that **ticket attempts are not independent trials**. 

When an agent processes a batch of tickets within an execution run, systemic behavioral priors (e.g., an inclination to create regression tests, verbosity in output formatting, or tolerance for linting warnings) remain correlated throughout the session. If an experimenter pools 5 runs of 12 tickets into $N = 60$ independent observations, standard standard-error formulas $\sqrt{\hat{p}(1-\hat{p})/N}$ artificially contract, producing wildly optimistic confidence intervals and false discoveries.

As demonstrated in Table 1, treating attempts as independent yielded $p < 0.001$ for $S_4$ vs. $B$ (Fisher exact $p = 1.7 \times 10^{-6}$), whereas an exact run-level permutation test correctly yields $p = 0.167$. We strongly recommend that future agent benchmarks report variance across independent cohort runs and conduct hypothesis testing at the run level.

### 8.2 Compliance Failures vs. Capability Failures
Our results establish an empirical taxonomy of agent unreliability:
1. **Capability Failures:** The agent lacks the reasoning capacity to deduce the correct algorithmic fix. On self-contained Python tickets, frontier models exhibit virtually zero capability failures.
2. **Compliance Failures:** The agent understands the logic but violates operational constraints (e.g., modifying test suites, altering global configurations).

Importantly, **education components act almost exclusively on compliance failures**. When an agent fails by adding tests to protected files, providing an explicit Full Book ($s_3$) or an automated policy retry ($k_2$) resolves the error with near-zero compute overhead. Treating compliance failures as reasoning deficiencies leads researchers to construct overly complex agent topologies when simple constraint checkers suffice.

### 8.3 When Does Education Optimization Matter?
Our findings define the operational boundary conditions under which education design optimization is critical:
- **Small, Prompt-Sized Tasks:** On self-contained repositories where full code context fits in the prompt, base models operate at ceiling. Optimizing $(s, p, u, r, k)$ yields negligible separation.
- **Large-Scale, Under-Specified Tasks:** When repository size vastly exceeds the context window, agents cannot fit all definitions into memory. In this regime, the hypothesis that retrieval tools ($u_3\text{--}u_5$), practice-derived indexing ($p_2$), and multi-pass review ($r_3$) become non-optional remains an untested hypothesis that requires multi-module benchmarks to verify.

### 8.4 Formulating the Knapsack MIP Surrogate
Using the measured incremental token costs from Section 5.2 (Full Book $c_s = 845$ tokens over bare prompt, Short Book $c_{s2} = 297$ tokens, Worked Examples $c_p = 1{,}072$ tokens over book, Review Checklist $c_r = 95$ tokens over book, Test Runner Brief $c_u = 109$ tokens over book), the knapsack optimization problem:
$$\max_{x \in \{0,1\}^M} \sum_{i} g_i x_i \quad \text{s.t.} \quad \sum_{i} c_i x_i \le B, \qquad x_i + x_j \le 1 \; \forall (i,j) \in \mathcal{K}$$
serves as a proposal mechanism for budget-constrained scaffolding. On compliance-dominated tasks, assigning the Full Book ($s_3$) yields the highest marginal compliance gain per token expended, while automated policy retries provide an effective fallback when prompt budgets are severely constrained.

---

## 9. Threats to Validity and Limitations

1. **Benchmark Scale and Language Diversity:** Our benchmark is restricted to Python repositories containing small-to-medium module footprints. Findings may not generalize directly to languages with complex build lifecycles (e.g., C++, Rust, Java) or massive distributed codebases.
2. **Model Homogeneity:** Primary evaluations were conducted using Claude Sonnet subagents (exact version not recorded). While Sonnet is representative of state-of-the-art SWE agents, open-weight models with lower baseline capabilities may exhibit non-ceiling behavior on the same task suite.
3. **Subagent Tool Restrictions:** In our pilot configurations, subagents were constrained by prompt instructions rather than kernel-level filesystem sandboxes. While our programmatic grader enforced strict file diff protection, true production environments should pair instruction rules with OS-level access control.
4. **Data Handling in Hard4:** During the workspace reconstruction for the final Hard4 validation, the tool-arm patches for four tickets were overwritten and lost, and were subsequently replaced by fresh runs.

---

## 10. Conclusion and Future Directions

In this work, we introduced a formal optimization framework that frames AI agent reliability as an education design problem over Sources, Practice, Tools, Review, and Retries. Through an extensive empirical campaign spanning approximately 1,950 graded attempts across single-factor ablations, fractional factorial matrices, and five progressively harder ticket sets, we uncovered critical evaluation realities:
- On prompt-contained tasks, agent reasoning operates at a 100% functional ceiling; unreliability is driven by run-level policy compliance.
- Run-level clustering invalidates naive sample size assumptions, necessitating run-level statistical testing.
- Automated policy-check retries ($k$) rescued 17 of 17 compliance failures in retry cells without manual intervention.

Future work must transition beyond prompt-contained repositories into multi-module codebases where specification discovery and code retrieval are non-trivial, creating the empirical spread necessary to parameterize non-linear component interactions in the education design space.

---

## References

1. Anthropic. (2024). *The Claude 3 Model Family: Opus, Sonnet, Haiku*. Technical Report.
2. Bubeck, S., et al. (2023). *Sparks of Artificial General Intelligence: Early experiments with GPT-4*. arXiv preprint arXiv:2303.12712.
3. Jimenez, C. E., et al. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024.
4. Khattab, O., et al. (2023). *DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines*. arXiv preprint arXiv:2310.03714.
5. Li, H., et al. (2024). *Code-Graph Guided Reasoning for Autonomous Repository Repair*. NeurIPS 2024.
6. Wilson, E. B. (1927). *Probable inference, the law of population, and the nature of trace*. Journal of the American Statistical Association, 22(158), 209-212.
7. Yang, J., et al. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. arXiv preprint arXiv:2405.15793.
8. Zhou, D., et al. (2023). *Large Language Models Are Human-Level Prompt Engineers (APE)*. ICLR 2023.

---

## Appendices

### Appendix A: Full Text of the 16-Rule Process Book ($B.md$)
The original process book assigned in configuration $s_3$ (`briefs/B.md`):
- **W01 [Workflow]:** Read the whole issue and every file in repository before changing anything.
- **W02 [Debugging]:** Find root cause; treat every docstring sentence as a requirement.
- **W03 [Scope]:** Make smallest change that fully solves the problem.
- **W04 [Features]:** Implement new behaviour exactly as specified; cover all edge cases.
- **W05 [Tests]:** Existing tests are specification. Never edit, delete or weaken tests.
- **W06 [Features]:** Exact module and function names for newly requested files.
- **W07 [Multi-file]:** Update all callers across repository in the same patch.
- **W08 [Compatibility]:** Preserve public behaviour; add new parameters as keyword arguments with backward-compatible defaults.
- **W09 [Refactoring]:** Refactor without altering external behaviour.
- **W10 [Security]:** Parameterized queries; resolve paths with `os.path.realpath` and check containment with `os.path.commonpath`.
- **W11 [Safety]:** No symlink following, stay inside target directory, no `rmtree` or `os.system`.
- **W12 [Writing tests]:** Assert documented behaviour; tests must fail on buggy code and pass on correct code.
- **W13 [Writing tests]:** Put regression test in existing test file when named.
- **W14 [Output]:** Emit `=== FILE: path ===` and `=== END ===` blocks strictly.
- **W15 [Verification]:** Walk through requirements and trace tests before finishing.
- **W16 [Environment]:** Standard library and pytest only; no debug prints or secrets.

### Appendix B: 5-Rule Short Process Book ($S_2.md$)
Rules W01, W02, W05, W07, W14.

### Appendix C: Benchmark Ticket Inventory (`tasks.py`)
Tickets `t1` through `t20` (8 practice, 12 held-out final exam).

### Appendix D: Statistical Formulas and Permutation Test Protocol
Wilson Score Interval and Exact Permutation Partition Test over $\binom{10}{5} = 252$ permutations.
