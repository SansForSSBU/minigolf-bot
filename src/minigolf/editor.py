import sys
from enum import Enum, auto
from pathlib import Path
from typing import Optional
import copy

import click
import pygame
import pygame_gui
from pygame import Surface
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextEntryLine
from pygame_gui.windows import UIConfirmationDialog, UIFileDialog

from loguru import logger

from minigolf import components
from minigolf.entity import Entity
from minigolf.objects import EntityBuilder
from minigolf.systems.physics import PhysicsSpace
from minigolf.systems.rendering import render_system
from minigolf.world import World

# ────────────────────────────────────────────────────────────────────────────────

TILE_SIZE = 50
GRID_WIDTH, GRID_HEIGHT = 16, 16
CANVAS_WIDTH, CANVAS_HEIGHT = TILE_SIZE * GRID_WIDTH, TILE_SIZE * GRID_HEIGHT
UI_WIDTH = 250
SCREEN_WIDTH = CANVAS_WIDTH + UI_WIDTH
SCREEN_HEIGHT = CANVAS_HEIGHT

LEVELS_DIR = Path("levels")
LEVELS_DIR.mkdir(exist_ok=True)


# ────────────────────────────────────────────────────────────────────────────────


class Tool(Enum):
    WALL = auto()
    BALL = auto()
    HOLE = auto()
    ERASER = auto()


TOOL_KEYS = {
    pygame.K_1: Tool.WALL,
    pygame.K_2: Tool.BALL,
    pygame.K_3: Tool.HOLE,
    pygame.K_4: Tool.ERASER,
}
TOOL_NAMES = {
    Tool.WALL: "WALL (1)",
    Tool.BALL: "BALL (2)",
    Tool.HOLE: "HOLE (3)",
    Tool.ERASER: "ERASER (4)",
}


def snap_to_grid(x: int, y: int) -> tuple[int, int]:
    """Snap pixel position to nearest tile-aligned grid coords."""
    return (x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE


def get_entity_at(world: World, x: int, y: int) -> Optional[Entity]:
    """Find entity at given coords (x, y)."""
    for entity in world.entities.values():
        pos = entity.get(components.Position)
        shape = entity.get(components.Shape)
        if not pos:
            continue
        w = shape.width if shape else TILE_SIZE
        h = shape.height if shape else TILE_SIZE
        if pos.x <= x < pos.x + w and pos.y <= y < pos.y + h:
            return entity
    return None


def build_entity(tool: Tool, x: int, y: int) -> Optional[Entity]:
    """Construct a new entity based on the selected tool."""
    builder = EntityBuilder()
    if tool == Tool.WALL:
        return builder.wall(x, y, TILE_SIZE, TILE_SIZE).build()
    elif tool == Tool.BALL:
        return builder.ball(x + TILE_SIZE // 2, y + TILE_SIZE // 2).build()
    elif tool == Tool.HOLE:
        return builder.hole(x + TILE_SIZE // 2, y + TILE_SIZE // 2).build()
    return None


def get_filename(entry: UITextEntryLine) -> Path:
    """Get sanitized filename from UI text entry, enforce .json extension."""
    raw = entry.get_text().strip()
    if not raw.endswith(".json"):
        raw += ".json"
    return LEVELS_DIR / raw


def main_loop():
    undo_stack: list[dict[int, Entity]] = []
    redo_stack: list[dict[int, Entity]] = []

    pygame.init()
    screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
    pygame.display.set_caption("Minigolf Level Editor")
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager.set_window_resolution((SCREEN_WIDTH, SCREEN_HEIGHT))

    world = World()
    physics = PhysicsSpace(world)
    physics.populate()

    current_tool: Tool = Tool.WALL
    undo_stack: list[dict[int, Entity]] = []
    drag_painting = False
    confirm_dialog: UIConfirmationDialog | None = None
    file_dialog: "UIFileDialog" | None = None

    # UI Elements
    filename_entry = UITextEntryLine(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 10, 230, 30), manager=manager
    )
    filename_entry.set_text("level.json")

    save_button = UIButton(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 50, 230, 30),
        text="💾 Save",
        manager=manager,
    )
    load_button = UIButton(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 90, 230, 30),
        text="📂 Load",
        manager=manager,
    )
    tool_label = UILabel(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 140, 230, 30),
        text="Tool: WALL (1)",
        manager=manager,
    )
    tool_buttons_panel = UIPanel(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 180, 230, 140),
        manager=manager,
    )

    # Tool selection buttons inside the panel
    tool_buttons = {}
    for i, tool in enumerate(Tool):
        btn = UIButton(
            relative_rect=pygame.Rect(0, i * 35, 230, 30),
            text=TOOL_NAMES[tool],
            manager=manager,
            container=tool_buttons_panel,
        )
        tool_buttons[btn] = tool

    # Clear button below panel
    clear_button = UIButton(
        relative_rect=pygame.Rect(CANVAS_WIDTH + 10, 330, 230, 30),
        text="🧹 Clear",
        manager=manager,
    )

    def set_tool(new_tool: Tool):
        nonlocal current_tool
        current_tool = new_tool
        tool_label.set_text(f"Tool: {TOOL_NAMES[current_tool]}")
        logger.debug(f"Switched tool to: {current_tool}")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mx, my = pygame.mouse.get_pos()
        mouse_over_ui = manager.get_hovering_any_element()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Exiting editor.")
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in TOOL_KEYS:
                    set_tool(TOOL_KEYS[event.key])
                elif (
                    event.key == pygame.K_z
                    and pygame.key.get_mods() & pygame.KMOD_CTRL
                    and not (pygame.key.get_mods() & pygame.KMOD_SHIFT)
                ):
                    if undo_stack:
                        redo_stack.append(copy.deepcopy(world.entities))
                        world.entities = undo_stack.pop()
                        physics = PhysicsSpace(world)
                        physics.populate()
                        logger.debug("Undo performed.")
                elif (
                    event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL
                ):
                    filename = get_filename(filename_entry)
                    if not filename.suffix:
                        filename = filename.with_suffix(".json")
                    world.to_json(filename)
                    logger.info(f"Saved level to {filename}")
                elif (
                    event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL
                ):
                    filename = get_filename(filename_entry)
                    if filename.exists():
                        world = World.from_json(filename)
                        physics = PhysicsSpace(world)
                        physics.populate()
                        undo_stack.clear()
                        logger.info(f"Loaded level from {filename}")
                elif (
                    event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL
                ) or (
                    event.key == pygame.K_z
                    and pygame.key.get_mods() & pygame.KMOD_CTRL
                    and pygame.key.get_mods() & pygame.KMOD_SHIFT
                ):
                    if redo_stack:
                        undo_stack.append(copy.deepcopy(world.entities))
                        world.entities = redo_stack.pop()
                        physics = PhysicsSpace(world)
                        physics.populate()
                        logger.debug("Redo performed.")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not mouse_over_ui:
                    drag_painting = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag_painting = False

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Tool buttons panel
                for btn, tool in tool_buttons.items():
                    if event.ui_element == btn:
                        set_tool(tool)
                # Clear button
                if event.ui_element == clear_button:
                    if world.entities:
                        undo_stack.append(copy.deepcopy(world.entities))
                        redo_stack.clear()
                        world.entities.clear()
                        physics.eid_to_body.clear()
                        physics.space.remove(
                            *physics.space.bodies, *physics.space.shapes
                        )
                        logger.info("Cleared all entities.")

                # Save button
                if event.ui_element == save_button:
                    filename = get_filename(filename_entry)
                    if filename.exists():
                        confirm_dialog = UIConfirmationDialog(
                            rect=pygame.Rect(
                                (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 75),
                                (300, 150),
                            ),
                            manager=manager,
                            window_title="Save Level",
                            action_long_desc=f"Overwrite file '{filename.name}'?",
                            action_short_name="Overwrite",
                            blocking=True,
                        )
                    else:
                        world.to_json(filename)
                        logger.info(f"Saved level to {filename}")
                # Load button
                elif event.ui_element == load_button:
                    from pygame_gui.windows import UIFileDialog

                    file_dialog = UIFileDialog(
                        rect=pygame.Rect(
                            (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200),
                            (400, 400),
                        ),
                        manager=manager,
                        window_title="Load Level",
                        initial_file_path=str(LEVELS_DIR),
                    )
                    logger.debug("Opened load file dialog.")

            elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if file_dialog and event.ui_element == file_dialog:
                    path = Path(event.text)
                    if path.exists() and path.suffix == ".json":
                        world = World.from_json(path)
                        physics = PhysicsSpace(world)
                        physics.populate()
                        undo_stack.clear()
                        filename_entry.set_text(path.name)
                        logger.info(f"Loaded level from {path}")
                    file_dialog.kill()
                    file_dialog = None

            elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                if event.ui_element == confirm_dialog:
                    filename = get_filename(filename_entry)
                    if not filename.suffix:
                        filename = filename.with_suffix(".json")
                    world.to_json(filename)
                    logger.info(f"Saved level to {filename}")
                    confirm_dialog.kill()
                    confirm_dialog = None

            manager.process_events(event)

        # Handle mouse dragging for painting
        if not mouse_over_ui and drag_painting:
            gx, gy = snap_to_grid(mx, my)
            existing = get_entity_at(world, gx, gy)
            if current_tool == Tool.ERASER:
                if existing:
                    undo_stack.append(copy.deepcopy(world.entities))
                    redo_stack.clear()
                    del world.entities[existing.id]
                    physics.remove_entity(existing)
                    logger.debug(f"Erased entity {existing.id} at {gx},{gy}")
            else:
                if not existing:
                    entity = build_entity(current_tool, gx, gy)
                    if entity:
                        undo_stack.append(
                            copy.deepcopy(world.entities)
                        )  # Deep copy undo
                        world.add_entity(entity)
                        physics.add_entity(entity)
                        logger.debug(
                            f"Added entity {entity.id} with tool {current_tool} at {gx},{gy}"
                        )

        physics.step()
        screen.fill((30, 30, 30))
        render_system(world, screen)

        # Draw grid lines
        for x in range(0, CANVAS_WIDTH, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, CANVAS_HEIGHT))
        for y in range(0, CANVAS_HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (0, y), (CANVAS_WIDTH, y))

        # Draw preview square if mouse on canvas (no UI)
        gx, gy = snap_to_grid(mx, my)
        if not mouse_over_ui:
            colour = {
                Tool.WALL: (255, 0, 0),
                Tool.BALL: (255, 255, 255),
                Tool.HOLE: (91, 166, 0),
                Tool.ERASER: (255, 100, 100),
            }[current_tool]
            pygame.draw.rect(screen, colour, (gx, gy, TILE_SIZE, TILE_SIZE), 2)

        manager.update(dt)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option("--debug", is_flag=True, help="Run in debug mode.")
def cli(debug: bool):
    if debug:
        logger.info("Debug mode enabled.")
    main_loop()
