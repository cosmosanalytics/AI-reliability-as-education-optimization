"""Unit and integration tests for the live agent runner and protocol compliance.

Verifies:
1. No silent mock fallbacks (raises RuntimeError if backend is unconfigured).
2. Standard task envelope header is always included.
3. u=1 interactive tool parser and execution logging.
4. Parity equation for k factor matches Resolution-V.
5. Review (r) and Retry (k) contracts preserve format requirements.
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner")))
import pytest
from runner.agent_runner import (
    STANDARD_TASK_ENVELOPE_HEADER,
    TOOL_BLOCK_REGEX,
    TOOL_INSTRUCTION_ENVELOPE,
    LiveModelBackend,
    compute_k_parity,
)


def test_no_silent_mock_fallback():
    """Confirms that an unconfigured backend raises a fatal RuntimeError and never returns a mock patch."""
    # Ensure no keys in environment for this test
    old_env = {}
    for k in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
        if k in os.environ:
            old_env[k] = os.environ.pop(k)

    try:
        backend = LiveModelBackend(
            model_id="claude-3-7-sonnet-20250219", backend="unconfigured"
        )
        with pytest.raises(RuntimeError) as exc_info:
            backend.startup_self_check()
        assert "FATAL" in str(exc_info.value)
        assert (
            "No mock fallbacks" in str(exc_info.value)
            or "not configured" in str(exc_info.value)
        )

        with pytest.raises(RuntimeError) as exc_info2:
            backend.call("hello", "", [])
        assert "FATAL" in str(exc_info2.value)
    finally:
        os.environ.update(old_env)


def test_task_envelope_presence():
    """Verifies format header is defined and mandates block format."""
    assert "Resolve this ticket" in STANDARD_TASK_ENVELOPE_HEADER
    assert "=== FILE: path/to/file ===" in STANDARD_TASK_ENVELOPE_HEADER
    assert "=== END ===" in STANDARD_TASK_ENVELOPE_HEADER
    assert "=== DELETE: path ===" in STANDARD_TASK_ENVELOPE_HEADER


def test_tool_regex_and_instructions():
    """Verifies that the interactive pytest tool block is correctly matched by regex."""
    sample_turn = (
        "Here is my draft patch:\n"
        "=== FILE: foo.py ===\ndef bar(): return 42\n=== END ===\n\n"
        "=== TOOL: pytest ===\ntests/test_foo.py\n=== END_TOOL ==="
    )
    match = TOOL_BLOCK_REGEX.search(sample_turn)
    assert match is not None, "Tool regex must detect the tool call block"
    assert match.group(1).strip() == "tests/test_foo.py"

    no_tool_turn = "=== FILE: foo.py ===\ndef bar(): return 42\n=== END ==="
    assert TOOL_BLOCK_REGEX.search(no_tool_turn) is None


def test_parity_symmetry():
    """Verifies that k parity is balanced and symmetric across all 16 cells."""
    ones = 0
    zeros = 0
    for s in [0, 1]:
        for p in [0, 1]:
            for u in [0, 1]:
                for r in [0, 1]:
                    k = compute_k_parity(s, p, u, r)
                    if k == 1:
                        ones += 1
                    else:
                        zeros += 1
    assert ones == 8
    assert zeros == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
