# Brief Combinatorial Design and Incremental Differences (`briefs/DIFF.md`)

This document records the exact structure, factor decomposition, and token measurements for all 16 cell briefs in the $2^{5-1}$ Resolution-V fractional factorial design.

---

## 1. Factor Grid and Defining Relation

The design uses five binary factors:
- **$s$ (Sources):** $0 \implies$ No Book (bare prompt); $1 \implies$ Full 16-rule Process Book (`B.md`).
- **$p$ (Practice):** $0 \implies$ Zero-shot; $1 \implies$ Two worked examples with bug-fix patches (`P3.md`).
- **$u$ (Tools):** $0 \implies$ Static diff generation; $1 \implies$ Interactive test runner instructions (`U2.md`).
- **$r$ (Review):** $0 \implies$ Single-turn submission; $1 \implies$ Pre-submission self-review checklist (`R2.md`).
- **$k$ (Retry):** Parity defined by $I = s \cdot p \cdot u \cdot r \cdot k \implies k = s \cdot p \cdot u \cdot r$ (implemented in the runner as policy retry logic).

---

## 2. All 16 Cell Briefs & Measured Token Footprints

Tokens measured using `tiktoken` (`cl100k_base` / `o200k_base`):

| Cell Code | $s$ | $p$ | $u$ | $r$ | Chars | Words | Tokens (`cl100k`) | Tokens (`o200k`) | Active Prompt Components |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **C0000** | 0 | 0 | 0 | 0 | 136 | 20 | 26 | 26 | Bare prompt ($S_1$) |
| **C0001** | 0 | 0 | 0 | 1 | 582 | 74 | 118 | 119 | Bare + Review ($R$) |
| **C0010** | 0 | 0 | 1 | 0 | 558 | 84 | 132 | 133 | Bare + Tools ($U$) |
| **C0011** | 0 | 0 | 1 | 1 | 1,004 | 138 | 224 | 226 | Bare + Tools + Review |
| **C0100** | 0 | 1 | 0 | 0 | 4,059 | 544 | 1,098 | 1,108 | Bare + Practice ($P$) |
| **C0101** | 0 | 1 | 0 | 1 | 4,505 | 598 | 1,190 | 1,201 | Bare + Practice + Review |
| **C0110** | 0 | 1 | 1 | 0 | 4,481 | 608 | 1,204 | 1,215 | Bare + Practice + Tools |
| **C0111** | 0 | 1 | 1 | 1 | 4,927 | 662 | 1,296 | 1,308 | Bare + Practice + Tools + Review |
| **C1000** | 1 | 0 | 0 | 0 | 4,238 | 696 | 871 | 873 | Baseline Full Book ($B$) |
| **C1001** | 1 | 0 | 0 | 1 | 4,684 | 770 | 966 | 968 | Book + Review ($R_2$) |
| **C1010** | 1 | 0 | 1 | 0 | 4,657 | 760 | 980 | 982 | Book + Tools ($U_2$) |
| **C1011** | 1 | 0 | 1 | 1 | 5,106 | 814 | 1,072 | 1,075 | Book + Tools + Review |
| **C1100** | 1 | 1 | 0 | 0 | 8,162 | 1,220 | 1,943 | 1,955 | Book + Practice ($P_3$) |
| **C1101** | 1 | 1 | 0 | 1 | 8,607 | 1,294 | 2,035 | 2,048 | Book + Practice + Review |
| **C1110** | 1 | 1 | 1 | 0 | 8,583 | 1,304 | 2,049 | 2,062 | Book + Practice + Tools |
| **C1111** | 1 | 1 | 1 | 1 | 9,029 | 1,378 | 2,141 | 2,155 | Full Scaffold ($s+p+u+r$) |

---

## 3. Incremental Component Deltas (`cl100k_base`)

- **Full Process Book ($s=1$ vs $s=0$):** $+845$ tokens ($871 - 26$).
- **Worked Examples ($p=1$ vs $p=0$):** $+1{,}072$ tokens ($1{,}943 - 871$).
- **Interactive Test Runner ($u=1$ vs $u=0$):** $+109$ tokens ($980 - 871$).
- **Self-Review Checklist ($r=1$ vs $r=0$):** $+95$ tokens ($966 - 871$).
- **Short Book ($S_2$):** $323$ tokens ($+297$ tokens over bare prompt $S_1$).
- **Student Notes ($S_4$):** $623$ tokens ($+597$ tokens over bare prompt $S_1$).
- **Practice Notes ($P_2$):** $943$ tokens ($+72$ tokens over full book $B$).
