from abc import ABC, abstractmethod
import pygame
import pymunk
from pydantic import BaseModel
from minigolf.utils import add_tuples


class Position(BaseModel):
    x: float
    y: float


class Velocity(BaseModel):
    dx: float
    dy: float


class Shape(BaseModel, ABC):
    @abstractmethod
    def pymunk_offset(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def pygame_offset(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def draw_at(self, screen, pos, colour) -> None:
        pass

    @abstractmethod
    def to_pymunk(self, body: pymunk.Body) -> object:
        pass


class Rect(Shape):
    width: float
    height: float

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


class Circle(Shape):
    radius: float

    def pymunk_offset(self) -> tuple[float, float]:
        return (0, 0)

    def pygame_offset(self) -> tuple[float, float]:
        return (0, 0)

    def draw_at(self, screen, pos, colour) -> None:
        draw_pos = add_tuples((pos.x, pos.y), self.pygame_offset())
        pygame.draw.circle(screen, colour, draw_pos, self.radius)

    def to_pymunk(self, body: pymunk.Body) -> pymunk.Circle:
        return pymunk.Circle(body, self.radius)


class Collider(BaseModel):
    shape: Shape


class PhysicsBody(BaseModel):
    mass: float
    bounciness: float  # restitution
    friction: float
    # TODO: Should anchored be an attribute of this?


class Renderable(BaseModel):
    colour: tuple[int, int, int]
    shape: Shape
