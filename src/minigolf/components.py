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

    def to_pymunk(self):
        body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        body.mass = self.mass
        body.moment = 1  # TODO: Infer or add moment attribute.
        return body


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape


class Entity:
    def __init__(self):
        pass

    @classmethod
    def from_eid(cls, world, eid):
        entity = cls()
        for componentCls, v in world.components.items():
            if v.get(eid, None) is not None:
                attrName = componentCls.__name__[0].lower() + componentCls.__name__[1:]
                setattr(entity, attrName, v[eid])
        return entity

    def pymunk_position(self):
        if self.collider.shape.type == "rect":
            return (
                self.position.x + self.collider.shape.width / 2,
                self.position.y + self.collider.shape.height / 2,
            )
        else:
            raise NotImplementedError

    def to_pymunk(self):
        if not (hasattr(self, "position") and hasattr(self, "collider")):
            return None
        if self.collider.shape.type != "rect":
            raise NotImplementedError
        if hasattr(self, "velocity") and hasattr(self, "physicsBody"):
            body = self.physicsBody.to_pymunk()
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

    def to_pygame(self):
        raise NotImplementedError
