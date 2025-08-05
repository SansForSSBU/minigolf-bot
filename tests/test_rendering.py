import pygame
from unittest.mock import patch, MagicMock
from minigolf.systems.rendering import render_system
from minigolf.components import Position, Renderable, Rect, Circle
from minigolf.entity import Entity
from minigolf.world import World


class DummyWorld(World):
    def all_with(self, *types):
        # Return two entities: one with Rect, one with Circle
        entity_rect = Entity()
        entity_rect.add(Position(x=10, y=20))
        shape_rect = Rect(width=30, height=40)
        entity_rect.add(Renderable(colour=(255, 0, 0), shape=shape_rect))

        entity_circle = Entity()
        entity_circle.add(Position(x=50, y=60))
        shape_circle = Circle(radius=15)
        entity_circle.add(Renderable(colour=(0, 255, 0), shape=shape_circle))

        return [entity_rect, entity_circle]


def test_render_system_mocks_draw_at():
    pygame.init()
    pygame.display.set_mode((100, 100))  # Dummy display for Pygame, now 100x100
    screen = MagicMock(spec=pygame.Surface)
    world = DummyWorld()
    with (
        patch.object(Rect, "draw_at", autospec=True) as mock_rect_draw_at,
        patch.object(Circle, "draw_at", autospec=True) as mock_circle_draw_at,
    ):
        render_system(world, screen)
        # Assert draw_at was called for both shapes
        assert mock_rect_draw_at.called
        assert mock_circle_draw_at.called
        # Check call args for Rect
        rect_args, rect_kwargs = mock_rect_draw_at.call_args
        assert rect_args[1] is screen  # self, screen, pos, colour
        assert isinstance(rect_args[2], Position)
        assert rect_args[3] == (255, 0, 0)
        # Check call args for Circle
        circ_args, circ_kwargs = mock_circle_draw_at.call_args
        assert circ_args[1] is screen
        assert isinstance(circ_args[2], Position)
        assert circ_args[3] == (0, 255, 0)
    pygame.quit()
