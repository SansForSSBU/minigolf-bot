from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
import pygame
import pygame_gui

from minigolf.entity import Entity
from minigolf.systems.physics import PhysicsSpace
from minigolf.editor.consts import Tool
from minigolf.world import World


@dataclass
class State:
    TILE_SIZE: int = 50
    GRID_WIDTH: int = 16
    GRID_HEIGHT: int = 16
    CANVAS_WIDTH: int = GRID_WIDTH * TILE_SIZE
    UI_WIDTH: int = 250
    SCREEN_WIDTH: int = CANVAS_WIDTH + UI_WIDTH
    SCREEN_HEIGHT: int = GRID_HEIGHT * TILE_SIZE

    world: World = field(default_factory=World)
    physics: PhysicsSpace = field(init=False)

    manager: pygame_gui.UIManager = field(init=False)
    screen: pygame.Surface = field(init=False)

    current_tool: Tool = Tool.WALL
    undo_stack: list[dict[int, Entity]] = field(default_factory=list)
    redo_stack: list[dict[int, Entity]] = field(default_factory=list)
    drag_painting: bool = False
    mouse_over_ui: bool = False

    file_dialog: pygame_gui.windows.UIFileDialog | None = None
    confirm_dialog: pygame_gui.windows.UIConfirmationDialog | None = None
    filename_entry: pygame_gui.elements.UITextEntryLine | None = None

    def update_mouse(self) -> None:
        self.mouse_over_ui = self.manager.get_hovering_any_element()


def init_state(screen: pygame.Surface) -> State:
    state = State()
    state.screen = screen
    state.manager = pygame_gui.UIManager((state.SCREEN_WIDTH, state.SCREEN_HEIGHT))
    state.manager.set_window_resolution((state.SCREEN_WIDTH, state.SCREEN_HEIGHT))
    state.physics = PhysicsSpace(state.world)
    state.physics.populate()
    return state


def save_world(state: State, filename: Path) -> None:
    state.world.to_json(filename)
    logger.info(f"Saved level to {filename}")


def load_world(state: State, filename: Path) -> None:
    state.world = World.from_json(filename)
    state.physics = PhysicsSpace(state.world)
    state.physics.populate()
    state.undo_stack.clear()
    logger.info(f"Loaded level from {filename}")
    if state.filename_entry:
        state.filename_entry.set_text(filename.name)


def clear_world(state: State) -> None:
    if state.world.entities:
        logger.info("Clearing all entities in the world")
        state.undo_stack.append(copy.deepcopy(state.world.entities))
        state.redo_stack.clear()
        state.world.entities.clear()
        state.physics.eid_to_body.clear()
        state.physics.space.remove(
            *state.physics.space.bodies, *state.physics.space.shapes
        )
        logger.info("World cleared and physics reset")
