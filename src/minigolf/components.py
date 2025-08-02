from pydantic import BaseModel


class Position(BaseModel):
    x: float
    y: float


class Velocity(BaseModel):
    dx: float
    dy: float


class Collider(BaseModel):
    width: int
    height: int


class PhysicsBody(BaseModel):
    mass: float
    bounciness: float  # restitution
    friction: float


class Renderable(BaseModel):
    colour: tuple[int, int, int]
