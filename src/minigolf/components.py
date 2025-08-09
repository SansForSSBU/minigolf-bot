from typing import Annotated, Literal

import pygame
import pymunk
from pydantic import BaseModel, Field

from minigolf.utils import add_tuples


class Position(BaseModel):
    x: float
    y: float

    def __str__(self) -> str:
        return f"<Position x={round(self.x, 2)}, y={round(self.y, 2)}>"


class Velocity(BaseModel):
    dx: float
    dy: float

    def __str__(self) -> str:
        return f"<Velocity(dx={round(self.dx, 2)}, dy={round(self.dy, 2)})>"


class Rect(BaseModel):
    type: Literal["Rect", "rect"] = "rect"
    width: float
    height: float

    def __str__(self) -> str:
        return f"<Rect width={self.width}, height={self.height}>"

    def pymunk_offset(self) -> tuple[float, float]:
        return (self.width / 2, self.height / 2)

    def pygame_offset(self) -> tuple[float, float]:
        return (0, 0)

    def draw_at(self, screen, pos, colour) -> None:
        draw_pos = add_tuples((pos.x, pos.y), self.pygame_offset())
        rect = pygame.Rect(draw_pos[0], draw_pos[1], self.width, self.height)
        pygame.draw.rect(surface=screen, color=colour, rect=rect)

    def to_pymunk(self, body: pymunk.Body) -> pymunk.Poly:
        return pymunk.Poly.create_box(body, (self.width, self.height))


class Circle(BaseModel):
    type: Literal["Circle", "circle"] = "circle"
    radius: float

    def __str__(self) -> str:
        return f"<Circle radius={self.radius}>"

    def pymunk_offset(self) -> tuple[float, float]:
        return (0, 0)

    def pygame_offset(self) -> tuple[float, float]:
        return (0, 0)

    def draw_at(self, screen, pos, colour) -> None:
        draw_pos = add_tuples((pos.x, pos.y), self.pygame_offset())
        pygame.draw.circle(screen, colour, draw_pos, self.radius)

    def to_pymunk(self, body: pymunk.Body) -> pymunk.Circle:
        return pymunk.Circle(body, self.radius)


Shape = Annotated[Rect | Circle, Field(discriminator="type")]


class Collider(BaseModel):
    shape: Shape

    def __str__(self) -> str:
        return f"<Collider shape={self.shape}>"


class PhysicsBody(BaseModel):
    mass: float
    bounciness: float  # restitution
    friction: float
    anchored: bool

    def __str__(self) -> str:
        return (
            f"<PhysicsBody mass={self.mass}, bounciness={self.bounciness}, "
            f"friction={self.friction}, anchored={self.anchored}>"
        )


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape

    def __str__(self) -> str:
        return f"<Renderable colour={self.colour}, shape={self.shape}>"


class Hole(BaseModel):
    pass
