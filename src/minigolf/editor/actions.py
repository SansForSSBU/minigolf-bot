from __future__ import annotations

import copy
from pathlib import Path
import pygame
import pygame_gui

from loguru import logger

from minigolf.editor.consts import TOOL_KEYS, Tool
from minigolf.editor.files import get_filename
from minigolf.editor.grid import build_entity, get_entity_at, snap_to_grid
from minigolf.editor.state import State
from minigolf.systems.physics import PhysicsSpace
from minigolf.world import World


def handle_event(event: pygame.event.Event, state: State) -> None:
    """
    Central dispatcher for all editor events. Handles:
    - Mouse clicks and drags
    - UI interactions
    - Keyboard shortcuts
    """
    event_handlers = {
        pygame.KEYDOWN: _handle_keydown,
        pygame.MOUSEBUTTONDOWN: _start_paint,
        pygame.MOUSEBUTTONUP: _stop_paint,
        pygame_gui.UI_BUTTON_PRESSED: _handle_button,
        pygame_gui.UI_FILE_DIALOG_PATH_PICKED: _handle_file_dialog,
        pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED: _handle_confirm_dialog,
    }

    handler = event_handlers.get(event.type)
    if handler:
        handler(event, state)

    state.manager.process_events(event)


def _start_paint(event, state):
    if not state.mouse_over_ui:
        state.drag_painting = True


def _stop_paint(event, state):
    state.drag_painting = False


def _handle_keydown(event: pygame.event.Event, state: State) -> None:
    """
    Handle keybindings for shortcuts and tool selection.
    """

    def is_down(mod: int) -> bool:
        """Check if a modifier key is pressed."""
        return bool(pygame.key.get_mods() & mod)

    key_combo = (event.key, is_down(pygame.KMOD_CTRL), is_down(pygame.KMOD_SHIFT))
    key_actions = {
        (pygame.K_s, True, False): lambda: _button_save(state),
        (pygame.K_o, True, False): lambda: _button_load(state),
        (pygame.K_z, True, False): lambda: _undo(state),
        (pygame.K_z, True, True): lambda: _redo(state),
        (pygame.K_y, True, False): lambda: _redo(state),
    }

    if event.key in TOOL_KEYS:
        state.current_tool = TOOL_KEYS[event.key]
        logger.debug(f"Tool changed to {state.current_tool.name}")
    elif key_combo in key_actions:
        key_actions[key_combo]()


def _undo(state: State) -> None:
    if state.undo_stack:
        logger.debug("Undo triggered")
        state.redo_stack.append(copy.deepcopy(state.world.entities))
        state.world.entities = state.undo_stack.pop()
        _rebuild_physics(state)
    else:
        logger.debug("Undo triggered but stack is empty")


def _redo(state: State) -> None:
    if state.redo_stack:
        logger.debug("Redo triggered")
        state.undo_stack.append(copy.deepcopy(state.world.entities))
        state.world.entities = state.redo_stack.pop()
        _rebuild_physics(state)
    else:
        logger.debug("Redo triggered but stack is empty")


def _rebuild_physics(state: State) -> None:
    state.physics = PhysicsSpace(state.world)
    state.physics.populate()


def _handle_button(event: pygame.event.Event, state: State) -> None:
    """
    Dispatch UI button actions based on label keyword.
    """
    label = getattr(event.ui_element, "text", "").lower()
    match label:
        case l if "save" in l:
            _button_save(state)
        case l if "load" in l:
            _button_load(state)
        case l if "clear" in l:
            _button_clear(state)


def _button_save(state: State) -> None:
    filename = get_filename(state.filename_entry)
    if filename.exists():
        _show_save_confirmation_dialog(state, filename)
    else:
        state.save_world(filename)


def _button_load(state: State) -> None:
    _open_file_dialog(state)


def _button_clear(state: State) -> None:
    state.clear_world()


def _handle_file_dialog(event: pygame.event.Event, state: State) -> None:
    if state.file_dialog and event.ui_element == state.file_dialog:
        path = Path(event.text)
        if path.exists() and path.suffix == ".json":
            _load_world_from_file(state, path)
        state.file_dialog.kill()
        state.file_dialog = None


def _handle_confirm_dialog(event: pygame.event.Event, state: State) -> None:
    if state.confirm_dialog and event.ui_element == state.confirm_dialog:
        filename = get_filename(state.filename_entry)
        state.world.to_json(filename)
        logger.info(f"Overwrote existing level: {filename}")
        state.confirm_dialog.kill()
        state.confirm_dialog = None


def _load_world_from_file(state: State, path: Path) -> None:
    state.world = World.from_json(path)
    _rebuild_physics(state)
    state.undo_stack.clear()
    if state.filename_entry:
        state.filename_entry.set_text(path.name)
    logger.info(f"Loaded level from {path}")


def _show_save_confirmation_dialog(state: State, filename: Path) -> None:
    from pygame_gui.windows import UIConfirmationDialog

    state.confirm_dialog = UIConfirmationDialog(
        rect=pygame.Rect(
            (state.SCREEN_WIDTH // 2 - 150, state.SCREEN_HEIGHT // 2 - 75),
            (300, 150),
        ),
        manager=state.manager,
        window_title="Confirm Save",
        action_long_desc=f"Overwrite {filename.name}?",
        action_short_name="Overwrite",
        blocking=True,
    )


def _open_file_dialog(state: State) -> None:
    from pygame_gui.windows import UIFileDialog

    state.file_dialog = UIFileDialog(
        rect=pygame.Rect(
            (state.SCREEN_WIDTH // 2 - 200, state.SCREEN_HEIGHT // 2 - 200),
            (400, 400),
        ),
        manager=state.manager,
        window_title="Load Level",
        initial_file_path=str(Path("levels").resolve()),
    )
    logger.debug("Opened file dialog")


def handle_drag(state: State) -> None:
    """
    Handles painting and erasing entities on drag events.
    """
    if not state.drag_painting or state.mouse_over_ui:
        return

    mx, my = pygame.mouse.get_pos()
    gx, gy = snap_to_grid(mx, my)
    existing = get_entity_at(state.world, gx, gy)

    if state.current_tool == Tool.ERASER:
        if existing:
            _snapshot_undo(state)
            del state.world.entities[existing.id]
            state.physics.remove_entity(existing)
    else:
        if not existing:
            entity = build_entity(state.current_tool, gx, gy)
            if entity:
                _snapshot_undo(state)
                state.world.add_entity(entity)
                state.physics.add_entity(entity)


def _snapshot_undo(state: State) -> None:
    state.undo_stack.append(copy.deepcopy(state.world.entities))
    state.redo_stack.clear()
