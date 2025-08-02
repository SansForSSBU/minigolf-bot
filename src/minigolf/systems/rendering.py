import pygame
from minigolf.world import World
from minigolf.components import Position, Collider, Renderable


def render_system(world: World, screen: pygame.Surface) -> None:
    screen.fill((30, 30, 30))
    for eid in world.all_with(Position, Collider, Renderable):
        pos = world.get(Position, eid)
        col = world.get(Collider, eid)
        rend = world.get(Renderable, eid)
        rect = pygame.Rect(pos.x, pos.y, col.width, col.height)
        pygame.draw.rect(screen, rend.colour, rect)
    pygame.display.flip()
