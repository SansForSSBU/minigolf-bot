import pygame

from minigolf.components import Position, Renderable
from minigolf.world import World


def render_entity(screen, entity) -> None:
    if entity.renderable.shape.type == "rect":
        rect = entity.renderable.shape.to_pygame_shape(
            Position(x=entity.position.x, y=entity.position.y)
        )
        pygame.draw.rect(surface=screen, color=entity.renderable.colour, rect=rect)
    else:
        raise NotImplementedError


def draw_bg(screen) -> None:
    screen.fill((30, 30, 30))


def render_objects(screen, world) -> None:
    for eid in world.all_with(Position, Renderable):
        entity = world.get_entity(eid)
        render_entity(screen, entity)


def render_system(world: World, screen: pygame.Surface) -> None:
    draw_bg(screen)
    render_objects(screen, world)
    pygame.display.flip()
