# Designing AI Reliability as an Education Optimization Problem

[![Paper PDF](https://img.shields.io/badge/Paper-PDF-red.svg)](designing_ai_reliability_as_an_education_optimization_problem.pdf)
[![Status](https://img.shields.io/badge/Status-Research%20Manuscript-blue.svg)](designing_ai_reliability_as_an_education_optimization_problem.md)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Author:** Zhao (October 2026)  
**Full Manuscript:** [designing_ai_reliability_as_an_education_optimization_problem.pdf](designing_ai_reliability_as_an_education_optimization_problem.pdf) | [Markdown Version](designing_ai_reliability_as_an_education_optimization_problem.md)

---

## Abstract

Artificial intelligence agents demonstrate impressive average-case performance on complex software engineering benchmarks, yet their deployment remains hindered by high variance, brittle edge-case behavior, and silent failures. Current approaches to agent reliability rely largely on post-hoc prompt engineering or unstructured multi-agent deliberation, often evaluating systems on single-pass runs where run-level noise obscures true capability differences. 

In this paper, we formalize agent reliability as a constrained education optimization problem. Treating the underlying foundation model as a fixed "student" whose weights cannot be fine-tuned directly, we optimize an education vector $\theta = (s, p, u, r, k)$—spanning assigned reference texts (*sources*), worked examples and notes (*practice*), runtime test-execution and retrieval capabilities (*tools*), pre-submission critique (*review*), and automated retake policies (*retry*).

We evaluate this formulation on a tamper-aware software engineering benchmark of 20 tasks featuring hidden unit test suites and strict protected-file constraints, tracking approximately 1,950 graded attempts across single-factor ablations, a $2^{5-1}$ resolution-V fractional factorial design, and five hardening progressions on Claude Sonnet subagents (exact version not recorded). Our empirical results uncover critical evaluation realities:
1. **Functional Ceiling:** Modern frontier models easily synthesize code for repositories that fit within the prompt, achieving 95–100% functional solve rates and masking educational component differences.
2. **Run-Level Behavioral Clustering:** Failures are dominated by run-wide dispositions (e.g. adding tests to protected files in Run 2); treating tickets as independent inflates sample size ($N_{\text{eff}} = 5$ cohort runs vs. $N = 60$ tickets), rendering single-pass benchmark rankings spurious.
3. **Automated Policy Recovery:** Automated retries conditioned on file-protection checks rescue 100% (17 of 17) of rule compliance failures on the first resubmission.
4. **Specification Ambiguity vs. Capability:** Apparent drops in capability on harder tasks stem from omitted specification conventions rather than algorithmic deficiencies.

---

## Key Empirical Results

### 1. One-at-a-Time Ablation ($E3a$, 480 attempts)
*5 independent runs per design $\times$ 12 held-out tickets. Baseline $B$ = Full 16-rule book.*

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

All failures were protected test modifications, never functional errors.

### 2. Resolution-V Fractional Factorial ($E3b$, 960 attempts)
- **First Attempt:** 936 of 960 attempts passed strictly; all 960 passed functional tests.
- **Policy Retry ($k$):** Rescued **17 of 17 (100%)** first-attempt compliance failures on resubmission.
- **Effect Sizes:** With run-level rates as outcome ($\sigma = 0.065, 64 \text{ df}$), all effects hovered at $\beta = \pm 0.015$ ($p > 0.30$) due to the benchmark ceiling.

### 3. Hardening Progression ($E3c$, 224 attempts)
- Across Hard, Hard2, Hard3, and Hard4, base models consistently solved tickets at 95–100% rates.
- In Hard4 Final, static generation scored **21/21 (100%)** while the test runner arm scored **20/21 (95.2%)**, showing no detectable marginal accuracy gain on this sample when code fits in the prompt.

---

## Repository Structure

```
├── designing_ai_reliability_as_an_education_optimization_problem.pdf  # Publication PDF of the paper
├── designing_ai_reliability_as_an_education_optimization_problem.md   # Full markdown manuscript
├── designing_ai_reliability_as_an_education_optimization_problem.html # Formatted HTML presentation
├── REAL_TEST_REQUIREMENTS.md                                          # Rigorous protocol for live agent runs
├── PAPER_REVIEW_COMMENTS.md                                           # Peer review tracker & resolution notes
├── harness/
│   ├── core.py               # Evaluation harness (patch parser, pytest runner, tamper checker)
│   ├── tasks.py              # 20 original benchmark tasks (12 held-out, 8 practice)
│   └── validate.py           # Pre-flight validator for reference patches
├── benchmarks/
│   ├── hard_tasks.py         # Hard suite (Tasks 101-112)
│   ├── hard2_tasks.py        # Hard2 multi-file suite (Tasks 201-206)
│   ├── hard3_tasks.py        # Hard3 dense bug suite (Task 301)
│   ├── hard4_tasks.py        # Hard4 suite with partial visible tests (Tasks 601-701)
│   ├── gen4.py, harvest4.py  # Workspace generator and test runner scraper for Hard4
│   └── validate*.py          # Validation scripts across benchmark versions
├── briefs/
│   ├── B.md                  # Baseline 16-rule engineering process book
│   ├── S1.md                 # Bare instruction brief (No Book)
│   ├── S2.md                 # 5-rule short process book
│   ├── S4.md                 # Student study notes
│   ├── P2.md, P3.md          # Practice study notes and worked examples
│   ├── U2.md                 # Interactive test runner brief
│   ├── R2.md                 # Self-review checklist brief
│   └── C0001.md - C1111.md   # 16 fractional factorial cell briefs
├── graders/
│   ├── grade_abl.py          # OATA coordinate ablation grading script
│   ├── grade_fact.py         # Initial fractional factorial grading script
│   └── grade_hard4.py        # Hard4 benchmark evaluation script
└── results/
    ├── rows_fact.json        # 16-cell factorial output from original suite (960 attempts)
    ├── rows_abl.json         # OATA ablation results (480 attempts)
    ├── rows_hard.json        # Hard suite results (120 attempts)
    ├── rows_hard2.json       # Hard2 suite results (60 attempts)
    ├── rows_orig.json        # Original pilot results (144 attempts)
    └── patches_hard4/        # Raw patch outputs from Hard4 evaluations (42 attempts)
```

---

## Quickstart

### 1. Requirements
- Python 3.10+
- `pytest`

```bash
pip install pytest
```

### 2. Validate Benchmark Reference Solutions
Confirm that all gold reference patches pass hidden tests and unpatched code fails:
```bash
python harness/validate.py
python benchmarks/validate_hard.py
python benchmarks/validate2.py
python benchmarks/validate3.py
python benchmarks/validate4.py
```

### 3. Grade Existing Factorial and Ablation Runs
```bash
python graders/grade_abl.py
python graders/grade_fact.py
```

---

## Citation

```bibtex
@article{zhao2026designing,
  title={Designing AI Reliability as an Education Optimization Problem},
  author={Zhao},
  journal={Working Manuscript},
  year={2026}
}
```
