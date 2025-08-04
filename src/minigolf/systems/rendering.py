import pygame

from minigolf.components import Position, Renderable
from minigolf.entity import Entity
from minigolf.world import World


def render_entity(screen: pygame.Surface, entity: Entity) -> None:
    renderable = entity.get(Renderable)
    pos: Position | None = entity.get(Position)
    if not (pos and renderable):
        return

    renderable.shape.draw_at(screen, pos, renderable.colour)


def draw_bg(screen) -> None:
    screen.fill((30, 30, 30))


def render_objects(screen, world: World) -> None:
    for entity in world.all_with(Position, Renderable):
        render_entity(screen, entity)


def render_system(world: World, screen: pygame.Surface) -> None:
    draw_bg(screen)
    render_objects(screen, world)
    pygame.display.flip()
