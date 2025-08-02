from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    dx: float
    dy: float


@dataclass
class Collider:
    width: int
    height: int


@dataclass
class PhysicsBody:
    mass: float
    bounciness: float  # restitution
    friction: float


@dataclass
class Renderable:
    colour: tuple[int, int, int]
