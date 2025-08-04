from typing import Literal

import pygame
import pymunk
from pydantic import BaseModel


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
    # TODO: Should anchored be an attribute of this?

    def to_pymunk(self, anchored) -> pymunk.Body:
        body_type = pymunk.Body.STATIC if anchored else pymunk.Body.DYNAMIC
        body = pymunk.Body(body_type=body_type)

        if not anchored:
            body.mass = self.mass
            body.moment = float("inf")

        return body


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape
