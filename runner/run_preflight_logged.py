"""runner/run_preflight_logged.py: Runs full preflight test suite and saves UTF-8 log.
"""

import subprocess
import sys
import os
import pathlib

repo_root = pathlib.Path(__file__).resolve().parents[1]
log_file = repo_root / "tests" / "preflight_suite_e5_543.log"

cmd = [sys.executable, "-m", "pytest", "tests/test_suite_e5_preflight.py", "-n", "8", "-v", "--tb=short"]

print(f"Executing: {' '.join(cmd)}")
print(f"Logging to: {log_file}")

with open(log_file, "w", encoding="utf-8", newline="\n") as f:
    proc = subprocess.Popen(
        cmd,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    for line in proc.stdout:
        f.write(line)
        f.flush()
        # Print progress every 20 tests
        if "PASSED" in line or "FAILED" in line or "ERROR" in line:
            if line.strip().endswith("]"):
                pct = line.strip().split("[")[-1].rstrip("]")
                if any(x in pct for x in ("10%", "25%", "50%", "75%", "90%", "100%")):
                    print(f"Progress: {pct.strip()} -> {line.strip()[:75]}")

    proc.wait()
    print(f"Completed with exit code: {proc.returncode}")
    sys.exit(proc.returncode)
