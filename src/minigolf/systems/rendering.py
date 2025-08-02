import pygame

from minigolf.components import Position, Renderable
from minigolf.world import World


def render_object(screen, pos, rend):
    if rend.shape.type == "rect":
        rect = rend.shape.to_pygame_shape(
            Position(x=pos.x, y=pos.y)
        )  # pygame.Rect(x, y, width, height)
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
