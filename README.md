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

We evaluate this formulation across a comprehensive empirical progression exceeding 2,500 graded attempts on tamper-aware software engineering tasks featuring hidden functional tests, mutant test suites, and strict protected-file constraints. Our resolution-V fractional factorial design ($I = s \cdot p \cdot u \cdot r \cdot k$, $N = 320$ attempts across 80 independent runs, $\text{df} = 64$) achieves **full statistical separation of all five variables ($p < 0.0001$)**, establishing an empirical hierarchy of educational leverage:
$$\text{Sources } (\beta_s = +0.197) > \text{Review } (\beta_r = +0.153) > \text{Practice } (\beta_p = +0.072) > \text{Retry } (\beta_k = +0.041) > \text{Tools } (\beta_u = +0.034)$$

---

## Empirical Findings: Resolution-V Factorial Regression ($E3d$)

Evaluated under single-ticket isolation ($N = 320$ attempts across 80 independent runs, degrees of freedom $\text{df} = 64, R^2 = 0.982$):

| Factor / Interaction | Effect ($\beta$) | Std Error | $t$-statistic | $p$-value | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Intercept ($\beta_0$)** | **+0.6469** | **0.0070** | **92.57** | **< 0.0001** | *** |
| **Sources ($s$)** | **+0.1969** | **0.0070** | **28.17** | **< 0.0001** | *** |
| **Practice ($p$)** | **+0.0719** | **0.0070** | **10.29** | **< 0.0001** | *** |
| **Tools ($u$)** | **+0.0344** | **0.0070** | **4.92** | **< 0.0001** | *** |
| **Review ($r$)** | **+0.1531** | **0.0070** | **21.91** | **< 0.0001** | *** |
| **Retry ($k$)** | **+0.0406** | **0.0070** | **5.81** | **< 0.0001** | *** |
| **Sources $\times$ Practice ($sp$)** | **-0.0406** | **0.0070** | **-5.81** | **< 0.0001** | *** |
| **Tools $\times$ Review ($ur$)** | **-0.0219** | **0.0070** | **-3.13** | **0.0026** | ** |
| **Tools $\times$ Retry ($uk$)** | **-0.0344** | **0.0070** | **-4.92** | **< 0.0001** | *** |
| **Review $\times$ Retry ($rk$)** | **-0.0281** | **0.0070** | **-4.03** | **0.0002** | *** |

### Key Takeaways:
1. **Sources & Review Dominate:** The 16-rule engineering process book ($\beta_s = +0.197$) and pre-submission review checklists ($\beta_r = +0.153$) provide the greatest reliability gains.
2. **Sub-Additive Knowledge Returns ($\beta_{sp} = -0.041$):** Once an agent has comprehensive syllabus rules ($s=1$), worked examples ($p=1$) offer reduced marginal utility.
3. **Tools and Retry Act as Substitutes ($\beta_{uk} = -0.034$):** Runtime test runners and automated retry loops both provide test error tracebacks, acting as functional substitutes rather than additive complements.

---

## Repository Structure

```
├── designing_ai_reliability_as_an_education_optimization_problem.pdf  # Publication PDF of the paper
├── designing_ai_reliability_as_an_education_optimization_problem.md   # Full markdown manuscript
├── designing_ai_reliability_as_an_education_optimization_problem.html # Formatted HTML presentation
├── harness/
│   ├── core.py               # Evaluation harness (patch parser, pytest runner, tamper checker)
│   ├── tasks.py              # 20 original benchmark tasks (12 held-out, 8 practice)
│   └── validate.py           # Pre-flight validator for reference patches
├── benchmarks/
│   ├── sep_tasks.py          # Calibrated diagnostic benchmark tasks (Tasks 801-804)
│   ├── run_factorial_sep.py  # 16-cell Resolution-V factorial experiment execution script
│   ├── validate_sep.py       # Validation script for diagnostic tasks
│   ├── hard_tasks.py         # Hard suite (Tasks 101-112)
│   ├── hard2_tasks.py        # Hard2 multi-file suite (Tasks 201-206)
│   ├── hard3_tasks.py        # Hard3 dense bug suite (Task 301)
│   └── hard4_tasks.py        # Hard4 suite with partial visible tests (Tasks 601-701)
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
    ├── rows_sep_factorial.json # Full row-level output from E3d (320 attempts)
    ├── rows_fact.json        # 16-cell factorial output from original suite (960 attempts)
    ├── rows_abl.json         # OATA ablation results (480 attempts)
    ├── rows_hard.json        # Hard suite results (120 attempts)
    ├── rows_hard2.json       # Hard2 suite results (60 attempts)
    └── patches_hard4/        # Raw patch outputs from Hard4 evaluations
```

---

## Quickstart

### 1. Requirements
- Python 3.10+
- `pytest`
- `numpy`, `scipy` (for ANOVA and regression analysis)

```bash
pip install pytest numpy scipy
```

### 2. Validate Benchmark Reference Solutions
Confirm that all gold reference patches pass hidden tests and unpatched code fails:
```bash
python benchmarks/validate_sep.py
```

### 3. Re-run Factorial Regression Analysis
Execute the 16-cell resolution-V factorial model:
```bash
python benchmarks/run_factorial_sep.py
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
