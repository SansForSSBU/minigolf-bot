import pygame

from minigolf.components import Collider, Position, Renderable
from minigolf.world import World


def render_system(world: World, screen: pygame.Surface) -> None:
    screen.fill((30, 30, 30))
    for eid in world.all_with(Position, Collider, Renderable):
        pos = world.get(Position, eid)
        col = world.get(Collider, eid)
        rend = world.get(Renderable, eid)
        width = abs(col.width) if col.width != 0 else 2
        height = abs(col.height) if col.height != 0 else 2

        # Handle negative widths/heights
        x = pos.x + min(0, col.width)
        y = pos.y + min(0, col.height)

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface=screen, color=rend.colour, rect=rect)
    pygame.display.flip()
