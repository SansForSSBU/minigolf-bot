from minigolf.components import (
    Collider,
    PhysicsBody,
    Position,
    Renderable,
    Shape,
    Velocity,
)
from minigolf.entity import Entity
from minigolf.world import World


def create_ball(world: World, x: float, y: float, dx: float, dy: float) -> Entity:
    shape = Shape(type="rect", width=10, height=10)
    entity = world.create_entity()

    entity.add(Position(x=x, y=y))
    entity.add(Velocity(dx=dx, dy=dy))
    entity.add(PhysicsBody(mass=1.0, bounciness=0.9, friction=0.01))
    entity.add(Collider(shape=shape))
    entity.add(Renderable(colour=(255, 255, 255), shape=shape))

    return entity


def create_wall(world: World, x: float, y: float, width: int, height: int) -> Entity:
    shape = Shape(type="rect", width=width, height=height)
    entity = world.create_entity()

    entity.add(Position(x=x, y=y))
    entity.add(Collider(shape=shape))
    entity.add(Renderable(colour=(255, 0, 0), shape=shape))

    return entity


def create_hole(world: World, x: float, y: float) -> Entity:
    shape = Shape(type="rect", width=20, height=20)
    entity = world.create_entity()

    entity.add(Position(x=x, y=y))
    entity.add(Collider(shape=shape))
    entity.add(Renderable(colour=(91, 166, 0), shape=shape))

    return entity
