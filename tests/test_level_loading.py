import subprocess
import sys
from pathlib import Path


def test_minigolf_loads_level():
    # Use the provided test level file directly
    level_path = Path("tests/level1.json")
    result = subprocess.run(
        [sys.executable, "-m", "minigolf.game.main", str(level_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"minigolf exited with {result.returncode}: {result.stderr}"
    )
    assert "Loaded world from" in result.stdout or result.stderr
