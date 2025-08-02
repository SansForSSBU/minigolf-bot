from typing import TYPE_CHECKING, TypeVar

import pymunk
from pydantic import BaseModel

from minigolf.components import Collider, PhysicsBody, Position, Velocity

if TYPE_CHECKING:
    from minigolf.world import World

T = TypeVar("T", bound=BaseModel)


class Entity:
    def __init__(self, eid: int, world: "World"):
        self.id = eid
        self._world = world

    def get(self, component_type: type[T]) -> T | None:
        return self._world.get(component_type, self.id)

    def has(self, component_type: type[BaseModel]) -> bool:
        return self.id in self._world.components[component_type]

    def to_pymunk_position(self):
        pos = self.get(Position)
        col = self.get(Collider)
        if not (pos and col):
            return None
        return (pos.x + col.shape.width / 2, pos.y + col.shape.height / 2)

    def to_pymunk(self):
        pos = self.get(Position)
        col = self.get(Collider)
        vel = self.get(Velocity)
        bodydef = self.get(PhysicsBody)

        if not (pos and col):
            return None

        if col.shape.type != "rect":
            raise NotImplementedError

        if vel and bodydef:
            body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
            body.mass = bodydef.mass
            body.moment = float("inf")
            body.velocity = (vel.dx, vel.dy)
        else:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)

        width, height = col.shape.width, col.shape.height
        if width is None or height is None:
            raise ValueError("Collider shape missing width/height")
        body.position = self.to_pymunk_position()
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.elasticity = 1
        shape.friction = 0
        return body, shape

    def from_pymunk_position(self, pos):
        col = self.get(Collider)
        if not col or col.shape.type != "rect":
            raise NotImplementedError
        bx, by = pos
        return Position(
            x=bx - (col.shape.width / 2),
            y=by - (col.shape.height / 2),
        )

    def sync_with_pymunk_body(self, body) -> None:
        pos = self.get(Position)
        if not pos:
            return
        new_pos = self.from_pymunk_position(body.position)
        pos.x = new_pos.x
        pos.y = new_pos.y

    def to_pygame(self):
        raise NotImplementedError
