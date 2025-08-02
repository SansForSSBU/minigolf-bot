import pygame

from minigolf.components import Position, Renderable
from minigolf.world import World


def render_object(screen, pos, rend):
    if rend.shape.type == "rect":
        width = max(abs(rend.shape.width), 2)
        height = max(abs(rend.shape.height), 2)

        # TODO: Prevent negative widths/heights
        # Handle negative widths/heights
        x = pos.x + min(0, rend.shape.width)
        y = pos.y + min(0, rend.shape.height)

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface=screen, color=rend.colour, rect=rect)


def draw_bg(screen):
    screen.fill((30, 30, 30))


def render_objects(screen, world):
    for eid in world.all_with(Position, Renderable):
        pos = world.get(Position, eid)
        rend = world.get(Renderable, eid)
        render_object(screen, pos, rend)


def render_system(world: World, screen: pygame.Surface) -> None:
    draw_bg(screen)
    render_objects(screen, world)
    pygame.display.flip()
