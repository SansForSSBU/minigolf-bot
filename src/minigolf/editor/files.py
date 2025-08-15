from pathlib import Path

from loguru import logger
from pygame_gui.elements import UITextEntryLine

# Assuming minigolf.editor.files
PROJ_DIR = Path(__file__).resolve().parents[3]
LEVELS_DIR = PROJ_DIR / "levels"
LEVELS_DIR.mkdir(exist_ok=True)

logger.info(f"Levels directory: {LEVELS_DIR}")


def get_filename(entry: UITextEntryLine) -> Path:
    raw = entry.get_text().strip()
    if not raw.endswith(".json"):
        raw += ".json"
    return LEVELS_DIR / raw
