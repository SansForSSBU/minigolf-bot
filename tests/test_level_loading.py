import subprocess
import sys
from pathlib import Path

OK_EXIT = 0
SIGKILL_EXIT = -9


def test_minigolf_loads_level():
    level_path = Path("tests/level1.json")
    proc = subprocess.Popen(
        [sys.executable, "-m", "minigolf.game.main", str(level_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        # Wait up to 1 second for the process to finish
        outs, errs = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    # Fail if the process crashed (nonzero exit code)
    assert proc.returncode in [OK_EXIT, SIGKILL_EXIT], (
        f"minigolf exited with {proc.returncode}: {errs}"
    )
    assert "Loaded world from" in outs or errs
