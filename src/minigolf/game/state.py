from enum import Enum, auto


class GameState(Enum):
    """Represents the current state of the game."""

    PLAYING = auto()
    WON = auto()
    LOST = auto()
    PAUSED = auto()
