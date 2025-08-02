from pydantic import BaseModel
from typing import Literal
import pygame


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
