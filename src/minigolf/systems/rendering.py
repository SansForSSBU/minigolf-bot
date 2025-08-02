import pygame

from minigolf.components import Position, Renderable
from minigolf.entity import Entity
from minigolf.world import World


def render_entity(screen: pygame.Surface, entity: Entity) -> None:
    renderable = entity.get(Renderable)
    if renderable and renderable.shape.type == "rect":
        pos: Position | None = entity.get(Position)
        render = entity.get(Renderable)
        if not (pos and render):
            return
        rect = render.shape.to_pygame_shape(pos)
        if rect is None:
            return
        pygame.draw.rect(surface=screen, color=render.colour, rect=rect)
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
