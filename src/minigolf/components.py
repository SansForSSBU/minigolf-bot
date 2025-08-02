from pydantic import BaseModel
from typing import Literal


class Shape(BaseModel):
    type: Literal["rect", "circle"]
    width: int | None = None
    height: int | None = None
    radius: int | None = None


class Position(BaseModel):
    x: float
    y: float


class Velocity(BaseModel):
    dx: float
    dy: float


class Collider(BaseModel):
    shape: Shape


class PhysicsBody(BaseModel):
    mass: float
    bounciness: float  # restitution
    friction: float


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape
