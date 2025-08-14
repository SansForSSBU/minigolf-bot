from typing import TypeVar, cast

import pymunk
from pydantic import BaseModel

from minigolf.components import Collider, PhysicsBody, Position, Velocity
from minigolf.utils import from_pymunk_position, to_pymunk_position
from minigolf.constants import DEFAULT_ELASTICITY, DEFAULT_WALL_FRICTION, BALL_MOMENT

T = TypeVar("T", bound=BaseModel)


class PhysicsObject:
    def __init__(self, entity: "Entity", body: pymunk.Body, shape: pymunk.Shape):
        self.entity = entity
        self.body = body
        self.shape = shape

    @classmethod
    def from_entity(cls, entity: "Entity") -> "PhysicsObject | None":
        pos = entity.get(Position)
        col = entity.get(Collider)
        bodydef = entity.get(PhysicsBody)
        if pos is None or col is None or bodydef is None:
            return None
        if not bodydef.anchored:
            vel = entity.get(Velocity)
            body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
            body.mass = bodydef.mass
            body.moment = BALL_MOMENT
            body.velocity = vel.dx, vel.dy
        else:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)

        body.position = to_pymunk_position(col.shape, pos)
        shape = col.shape.to_pymunk(body)

        shape.elasticity = DEFAULT_ELASTICITY
        shape.friction = DEFAULT_WALL_FRICTION
        shape.entity = entity

        return cls(entity, body, shape)

    def add_to_space(self, space: pymunk.Space):
        space.add(self.body, self.shape)

    def sync_to_entity(self):
        self.entity.sync_with_pymunk_body(self.body)


class Entity:
    def __init__(self):
        self.id: int | None = None
        self.components: dict[type[BaseModel], BaseModel] = {}

    def add(self, component: BaseModel) -> None:
        self.components[type(component)] = component

    def get(self, cls: type[T]) -> T | None:
        return cast(T | None, self.components.get(cls))

    def has(self, component_type: type[BaseModel]) -> bool:
        return component_type in self.components

    def to_pymunk_position(self):
        pos = self.get(Position)
        col = self.get(Collider)
        if not (pos and col):
            return None
        return (pos.x + col.shape.width / 2, pos.y + col.shape.height / 2)

    def from_pymunk_position(self, pos):
        col = self.get(Collider)
        if not col or col.shape.type != "rect":
            raise NotImplementedError
        bx, by = pos
        return Position(
            x=bx - (col.shape.width / 2),
            y=by - (col.shape.height / 2),
        )

    def remove(self, component_type: type[BaseModel]) -> None:
        if component_type in self.components:
            del self.components[component_type]

    def sync_with_pymunk_body(self, pymunk_body) -> None:
        if (pos := self.get(Position)) is not None and (
            col := self.get(Collider)
        ) is not None:
            pos.x, pos.y = from_pymunk_position(col.shape, pymunk_body.position)

    def to_pygame(self):
        raise NotImplementedError
