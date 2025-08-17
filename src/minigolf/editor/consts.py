from enum import Enum, auto

import pygame


class Tool(Enum):
    WALL = auto()
    BALL = auto()
    HOLE = auto()
    ERASER = auto()


TOOL_KEYS: dict[int, Tool] = {
    pygame.K_1: Tool.WALL,
    pygame.K_2: Tool.BALL,
    pygame.K_3: Tool.HOLE,
    pygame.K_4: Tool.ERASER,
}

TOOL_NAMES: dict[Tool, str] = {
    Tool.WALL: "WALL (1)",
    Tool.BALL: "BALL (2)",
    Tool.HOLE: "HOLE (3)",
    Tool.ERASER: "ERASER (4)",
}

TOOL_PREVIEW_COLOURS: dict[Tool, tuple[int, int, int]] = {
    Tool.WALL: (255, 0, 0),
    Tool.BALL: (255, 255, 255),
    Tool.HOLE: (91, 166, 0),
    Tool.ERASER: (255, 100, 100),
}
