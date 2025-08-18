from enum import Enum


class GameState(str, Enum):
    """Represents the current state of the game."""

    PLAYING = "PLAYING"
    WON = "WON"
    LOST = "LOST"
    PAUSED = "PAUSED"
