from __future__ import annotations

import pygame

from minigolf.editor.state import State
from minigolf.systems.rendering import render_system
from minigolf.editor.grid import snap_to_grid
from minigolf.editor.consts import TOOL_PREVIEW_COLOURS


def draw_everything(screen: pygame.Surface, state: State) -> None:
    render_system(state.world, screen)
    draw_grid_overlay(screen, state)
    draw_tool_preview(screen, state)


def draw_grid_overlay(screen: pygame.Surface, state: State) -> None:
    for x in range(0, state.CANVAS_WIDTH, state.TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, state.SCREEN_HEIGHT))
    for y in range(0, state.SCREEN_HEIGHT, state.TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (state.CANVAS_WIDTH, y))


def draw_tool_preview(screen: pygame.Surface, state: State) -> None:
    if state.mouse_over_ui:
        return

    mx, my = pygame.mouse.get_pos()
    gx, gy = snap_to_grid(mx, my)
    colour = TOOL_PREVIEW_COLOURS.get(state.current_tool, (255, 255, 255))
    pygame.draw.rect(screen, colour, (gx, gy, state.TILE_SIZE, state.TILE_SIZE), 2)
