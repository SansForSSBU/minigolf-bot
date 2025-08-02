from pydantic import BaseModel
from typing import Literal
import pygame
import pymunk


class Position(BaseModel):
    x: float
    y: float


class Velocity(BaseModel):
    dx: float
    dy: float


class Shape(BaseModel):
    type: Literal["rect", "circle"]
    width: int | None = None
    height: int | None = None
    radius: int | None = None

    def to_pygame_shape(self, pos: Position):
        if self.type == "rect":
            return pygame.Rect(pos.x, pos.y, self.width, self.height)
        elif self.type == "circle":
            raise NotImplementedError


class Collider(BaseModel):
    shape: Shape


class PhysicsBody(BaseModel):
    mass: float
    bounciness: float  # restitution
    friction: float


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape


class Entity:
    def __init__(self):
        pass

    @classmethod
    def from_eid(cls, world, eid) -> "Entity":
        entity = cls()
        for componentCls, v in world.components.items():
            if v.get(eid, None) is not None:
                attrName = componentCls.__name__[0].lower() + componentCls.__name__[1:]
                setattr(entity, attrName, v[eid])
        return entity

    def pymunk_position(self) -> tuple[int, int] | None:
        if not hasattr(self, "position"):
            return None
        if self.collider.shape.type == "rect":
            return (
                self.position.x + self.collider.shape.width / 2,
                self.position.y + self.collider.shape.height / 2,
            )
        else:
            raise NotImplementedError

    def to_pymunk(self) -> tuple[pymunk.Body, pymunk.Poly] | None:
        if not (hasattr(self, "position") and hasattr(self, "collider")):
            return None
        if self.collider.shape.type != "rect":
            raise NotImplementedError
        if hasattr(self, "velocity") and hasattr(self, "physicsBody"):
            body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
            body.mass = self.physicsBody.mass
            body.moment = 1  # TODO: Infer or add moment attribute.
            body.velocity = (self.velocity.dx, self.velocity.dy)
        else:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        width = self.collider.shape.width
        height = self.collider.shape.height
        body.position = self.pymunk_position()
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.elasticity = 1
        shape.friction = 0
        return body, shape

    def from_pymunk_position(self, pos: pymunk.Vec2d) -> Position:
        if self.collider.shape.type == "rect":
            bx, by = pos
            return Position(
                x=bx - (self.collider.shape.width / 2),
                y=by - (self.collider.shape.height / 2),
            )
        else:
            raise NotImplementedError

    def sync_with_pymunk_body(self, body) -> None:
        if hasattr(self, "position"):
            new_pos = self.from_pymunk_position(body.position)
            self.position.x = new_pos.x
            self.position.y = new_pos.y

    def to_pygame(self):
        raise NotImplementedError
