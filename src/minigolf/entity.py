from typing import TypeVar, cast

import pymunk
from pydantic import BaseModel

from minigolf.components import Collider, PhysicsBody, Position, Velocity


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
        vel = entity.get(Velocity)
        bodydef = entity.get(PhysicsBody)
        if not (pos and col):
            return None
        is_dynamic = vel is not None and bodydef is not None
        body_type = pymunk.Body.DYNAMIC if is_dynamic else pymunk.Body.STATIC
        body = pymunk.Body(body_type=body_type)
        if bodydef is not None:
            body.mass = bodydef.mass
            body.moment = float("inf")
            body.velocity = vel.dx, vel.dy

        body.position = entity.to_pymunk_position()
        shape = col.shape.to_pymunk(body)

        shape.elasticity = 1
        shape.friction = 0

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
        offset = col.shape.pymunk_offset()
        return (pos.x + offset[0], pos.y + offset[1])

    def from_pymunk_position(self, pos: tuple[int, int]) -> Position:
        # TODO: This should operate on Shape and be a utility method.
        col = self.get(Collider)
        bx, by = pos
        if not col:
            return None
        offset = col.shape.pymunk_offset()
        return Position(
            x=bx - offset[0],
            y=by - offset[1],
        )

    def sync_with_pymunk_body(self, body) -> None:
        pos = self.get(Position)
        if not pos:
            return
        new_pos: Position = self.from_pymunk_position(body.position)
        pos.x = new_pos.x
        pos.y = new_pos.y

    def to_pygame(self):
        raise NotImplementedError
