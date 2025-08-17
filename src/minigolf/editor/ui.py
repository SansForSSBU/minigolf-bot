import pygame
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextEntryLine

from minigolf.editor.consts import TOOL_NAMES, Tool
from minigolf.editor.state import State


def setup_ui(state: State) -> None:
    entry = UITextEntryLine(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 10, 230, 30),
        manager=state.manager,
    )
    entry.set_text("level.json")
    state.filename_entry = entry

    UIButton(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 50, 230, 30),
        text="💾 Save",
        manager=state.manager,
    )

    UIButton(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 90, 230, 30),
        text="📂 Load",
        manager=state.manager,
    )

    UILabel(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 140, 230, 30),
        text=f"Tool: {TOOL_NAMES[state.current_tool]}",
        manager=state.manager,
    )

    panel = UIPanel(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 180, 230, 140),
        manager=state.manager,
    )

    for i, tool in enumerate(Tool):
        UIButton(
            relative_rect=pygame.Rect(0, i * 35, 230, 30),
            text=TOOL_NAMES[tool],
            manager=state.manager,
            container=panel,
        )

    UIButton(
        relative_rect=pygame.Rect(state.CANVAS_WIDTH + 10, 330, 230, 30),
        text="🧹 Clear",
        manager=state.manager,
    )
