"""Unit test verifying the 2^(5-1) Resolution-V fractional factorial design.

Defining relation: I = s * p * u * r * k => k = s * p * u * r in +/-1 coding.
"""

import itertools
import pytest


def compute_k(s, p, u, r):
    """Computes k factor level using +/-1 sign parity.

    For binary indicators in {0, 1} where 0 => -1 and 1 => +1:
    The product of four +/-1 factors is +1 iff the number of -1s is even,
    which is equivalent to: (s + p + u + r) % 2 == 0.
    """
    # Convert {0, 1} to {-1, +1}
    s_sign = 1 if s == 1 else -1
    p_sign = 1 if p == 1 else -1
    u_sign = 1 if u == 1 else -1
    r_sign = 1 if r == 1 else -1

    k_sign = s_sign * p_sign * u_sign * r_sign
    return 1 if k_sign == 1 else 0


def get_factorial_cells():
    cells = []
    for s in [0, 1]:
        for p in [0, 1]:
            for u in [0, 1]:
                for r in [0, 1]:
                    k = compute_k(s, p, u, r)
                    cells.append((f"C{s}{p}{u}{r}", s, p, u, r, k))
    return cells


def test_16_cells_balance():
    cells = get_factorial_cells()
    assert len(cells) == 16, "Must contain exactly 16 cells"

    # Count of k=1 and k=0 must be exactly 8 each
    k_ones = [c for c in cells if c[5] == 1]
    k_zeros = [c for c in cells if c[5] == 0]
    assert len(k_ones) == 8, f"Expected 8 cells with k=1, got {len(k_ones)}"
    assert len(k_zeros) == 8, f"Expected 8 cells with k=0, got {len(k_zeros)}"


def test_resolution_v_orthogonality():
    cells = get_factorial_cells()
    # Map to +/-1 matrix
    matrix = []
    for _, s, p, u, r, k in cells:
        row = [
            1 if s == 1 else -1,
            1 if p == 1 else -1,
            1 if u == 1 else -1,
            1 if r == 1 else -1,
            1 if k == 1 else -1,
        ]
        matrix.append(row)

    # 1. Main effects sum to zero
    for col_idx, factor_name in enumerate(["s", "p", "u", "r", "k"]):
        col_sum = sum(matrix[r][col_idx] for r in range(16))
        assert col_sum == 0, f"Factor {factor_name} sum must be 0, got {col_sum}"

    # 2. All pairs of factors are orthogonal: sum(x_i * x_j) == 0
    for i in range(5):
        for j in range(i + 1, 5):
            inner_prod = sum(matrix[r][i] * matrix[r][j] for r in range(16))
            assert (
                inner_prod == 0
            ), f"Factors {i} and {j} must be orthogonal, got inner product {inner_prod}"

    # 3. All two-factor interactions are orthogonal to main effects (Resolution V)
    # 2FI columns: x_i * x_j
    two_fis = []
    for i in range(5):
        for j in range(i + 1, 5):
            col = [matrix[r][i] * matrix[r][j] for r in range(16)]
            two_fis.append(col)

    # Each 2FI is orthogonal to each main effect
    for fi_idx, fi_col in enumerate(two_fis):
        for main_idx in range(5):
            prod = sum(fi_col[r] * matrix[r][main_idx] for r in range(16))
            assert (
                prod == 0
            ), f"2FI {fi_idx} must be orthogonal to main effect {main_idx}, got {prod}"


def test_table_matches_spec():
    cells = get_factorial_cells()
    expected = [
        ("C0000", 0, 0, 0, 0, 1),
        ("C0001", 0, 0, 0, 1, 0),
        ("C0010", 0, 0, 1, 0, 0),
        ("C0011", 0, 0, 1, 1, 1),
        ("C0100", 0, 1, 0, 0, 0),
        ("C0101", 0, 1, 0, 1, 1),
        ("C0110", 0, 1, 1, 0, 1),
        ("C0111", 0, 1, 1, 1, 0),
        ("C1000", 1, 0, 0, 0, 0),
        ("C1001", 1, 0, 0, 1, 1),
        ("C1010", 1, 0, 1, 0, 1),
        ("C1011", 1, 0, 1, 1, 0),
        ("C1100", 1, 1, 0, 0, 1),
        ("C1101", 1, 1, 0, 1, 0),
        ("C1110", 1, 1, 1, 0, 0),
        ("C1111", 1, 1, 1, 1, 1),
    ]
    for cell, exp in zip(cells, expected):
        assert cell == exp, f"Mismatch: computed {cell} vs expected {exp}"


if __name__ == "__main__":
    test_16_cells_balance()
    test_resolution_v_orthogonality()
    test_table_matches_spec()
    print("All factorial design unit tests passed successfully!")
    cells = get_factorial_cells()
    print("\n16 Factorial Cells (s, p, u, r -> k):")
    for c, s, p, u, r, k in cells:
        print(f"  {c}: s={s} p={p} u={u} r={r} => k={k}")
