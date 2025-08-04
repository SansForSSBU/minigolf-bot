from typing import TypeVar, cast

import pymunk
from pydantic import BaseModel

from minigolf.components import Collider, PhysicsBody, Position, Velocity
from minigolf.utils import from_pymunk_position, to_pymunk_position
from minigolf.constants import DEFAULT_ELASTICITY, DEFAULT_WALL_FRICTION

T = TypeVar("T", bound=BaseModel)


class PhysicsObject:
    def __init__(self, entity: "Entity", body: pymunk.Body, shape: pymunk.Shape):
        self.entity = entity
        self.body = body
        self.shape = shape

    @classmethod
    def from_entity(cls, entity: "Entity") -> "PhysicsObject | None":
        assert (pos := entity.get(Position)) is not None
        assert (col := entity.get(Collider)) is not None
        vel = entity.get(Velocity)
        bodydef = entity.get(PhysicsBody)
        is_dynamic = isinstance(vel, Velocity) and bodydef is not None
        body_type = pymunk.Body.DYNAMIC if is_dynamic else pymunk.Body.STATIC
        body = pymunk.Body(body_type=body_type)
        if bodydef is not None:
            assert vel is not None
            body.mass = bodydef.mass
            body.moment = float("inf")
            body.velocity = vel.dx, vel.dy

        body.position = to_pymunk_position(col.shape, pos)
        shape = col.shape.to_pymunk(body)

        shape.elasticity = DEFAULT_ELASTICITY
        shape.friction = DEFAULT_WALL_FRICTION
        shape.mass = body.mass

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

    def sync_with_pymunk_body(self, pymunk_body) -> None:
        assert (pos := self.get(Position)) is not None
        assert (col := self.get(Collider)) is not None
        pos.x, pos.y = from_pymunk_position(col.shape, pymunk_body.position)

    def to_pygame(self):
        raise NotImplementedError
