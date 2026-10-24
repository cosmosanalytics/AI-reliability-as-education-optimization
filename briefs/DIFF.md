# Brief Combinatorial Design and Incremental Differences (`briefs/DIFF.md`)

This document records the exact structure, factor decomposition, prompt envelopes, and token measurements for all 16 cell briefs in the $2^{5-1}$ Resolution-V fractional factorial design.

---

## 1. Resolution-V Factorial Matrix ($I = s \cdot p \cdot u \cdot r \cdot k$)

The design evaluates five binary educational scaffolding factors:
- **$s$ (Sources):** $0 \implies$ Bare instruction ($S_1$); $1 \implies$ Full 16-rule Process Book ($B$).
- **$p$ (Practice):** $0 \implies$ Zero-shot; $1 \implies$ Two worked examples with patches ($P_3$).
- **$u$ (Tools):** $0 \implies$ Static diff synthesis; $1 \implies$ Interactive test execution tool (`pytest`).
- **$r$ (Review):** $0 \implies$ Immediate submission; $1 \implies$ Pre-submission self-review checklist ($R_2$).
- **$k$ (Retry):** Sign parity $k = s \cdot p \cdot u \cdot r$ in $\pm 1$ coding ($k=1$ if $(s+p+u+r)$ is even; $k=0$ if odd).

### Complete 16-Cell Orthogonal Table

| Cell Code | $s$ | $p$ | $u$ | $r$ | $k$ | Chars | Words | Tokens (`cl100k`) | Description / Active Prompt Components |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **C0000** | 0 | 0 | 0 | 0 | **1** | 136 | 20 | 26 | Bare prompt ($S_1$) + automated retry policy ($k^+$) |
| **C0001** | 0 | 0 | 0 | 1 | **0** | 582 | 94 | 121 | Bare + Review Checklist ($R$) |
| **C0010** | 0 | 0 | 1 | 0 | **0** | 638 | 107 | 129 | Bare + Interactive Test Runner ($U$) |
| **C0011** | 0 | 0 | 1 | 1 | **1** | 1,084 | 181 | 224 | Bare + Tools + Review + Retry ($k^+$) |
| **C0100** | 0 | 1 | 0 | 0 | **0** | 4,059 | 544 | 1,098 | Bare + Practice Worked Examples ($P$) |
| **C0101** | 0 | 1 | 0 | 1 | **1** | 4,505 | 618 | 1,193 | Bare + Practice + Review + Retry ($k^+$) |
| **C0110** | 0 | 1 | 1 | 0 | **1** | 4,561 | 631 | 1,201 | Bare + Practice + Tools + Retry ($k^+$) |
| **C0111** | 0 | 1 | 1 | 1 | **0** | 5,007 | 705 | 1,296 | Bare + Practice + Tools + Review |
| **C1000** | 1 | 0 | 0 | 0 | **0** | 4,238 | 696 | 871 | Baseline Full Book ($B$) |
| **C1001** | 1 | 0 | 0 | 1 | **1** | 4,684 | 770 | 966 | Book + Review + Retry ($k^+$) |
| **C1010** | 1 | 0 | 1 | 0 | **1** | 4,740 | 783 | 974 | Book + Interactive Test Runner + Retry ($k^+$) |
| **C1011** | 1 | 0 | 1 | 1 | **0** | 5,186 | 857 | 1,069 | Book + Tools + Review |
| **C1100** | 1 | 1 | 0 | 0 | **1** | 8,162 | 1,220 | 1,943 | Book + Practice Worked Examples + Retry ($k^+$) |
| **C1101** | 1 | 1 | 0 | 1 | **0** | 8,607 | 1,294 | 2,038 | Book + Practice + Review |
| **C1110** | 1 | 1 | 1 | 0 | **0** | 8,663 | 1,307 | 2,046 | Book + Practice + Tools |
| **C1111** | 1 | 1 | 1 | 1 | **1** | 9,109 | 1,381 | 2,141 | Full Scaffolding ($s+p+u+r$) + Retry ($k^+$) |

*Orthogonality property:* Exactly 8 cells have $k=1$ and 8 cells have $k=0$. All pairs of factors satisfy $\sum_{i=1}^{16} x_i x_j = 0$, guaranteeing Resolution V. Verified in `tests/test_factorial_design.py`.

---

## 2. Standardized Task Envelope (Across ALL Cells)

To prevent confounding format knowledge with factor scaffolding, every ticket prompt across all 16 cells is wrapped with this standardized format header outside the factor brief:

```text
Resolve this ticket. First read the whole ticket and every repository file below. Output ONLY the patch in exactly this format: for every file you create or change write a line === FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. Paths are relative to the repository root. To delete a file write === DELETE: path ===. Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks.
```

---

## 3. Interactive Tool Calling Envelope ($u=1$ Arms)

For all arms where $u=1$, the prompt is appended with the interactive test runner specification:

```text
INTERACTIVE TEST RUNNER TOOL:
You have access to an interactive test execution tool to run visible unit tests in your workspace.
To run tests before final submission, output a tool block:
=== TOOL: pytest ===
tests/
=== END_TOOL ===
You may include draft === FILE === blocks in the same turn so tests run against your updated code.
You will receive the test exit code and traceback. You may run tests multiple times across turns.
When you are finished, output your complete final patch in the standard === FILE === block format without any tool blocks.
```

---

## 4. Incremental Component Deltas (`cl100k_base`)

- **Full Process Book ($s=1$ vs $s=0$):** $+845$ tokens ($871 - 26$).
- **Worked Examples ($p=1$ vs $p=0$):** $+1{,}072$ tokens ($1{,}943 - 871$).
- **Interactive Test Runner ($u=1$ vs $u=0$):** $+103$ tokens ($974 - 871$).
- **Self-Review Checklist ($r=1$ vs $r=0$):** $+95$ tokens ($966 - 871$).
- **Short Book ($S_2$):** $323$ tokens ($+297$ tokens over bare prompt $S_1$).
- **Student Notes ($S_4$):** $623$ tokens ($+597$ tokens over bare prompt $S_1$).
- **Practice Notes ($P_2$):** $943$ tokens ($+72$ tokens over full book $B$).

Verification script: `harness/token_accounting.py`.
