from minigolf.components import (
    Collider,
    Hole,
    PhysicsBody,
    Position,
    Renderable,
    Rect,
    Circle,
    Velocity,
)
from minigolf.entity import Entity
from pydantic import BaseModel
from minigolf.constants import DEFAULT_ELASTICITY, DEFAULT_WALL_FRICTION


class EntityBuilder:
    def __init__(self):
        self.components: list[BaseModel] = []

    def ball(self, x: float, y: float) -> "EntityBuilder":
        """
        Create a ball entity with specified position.

        Args:
            x (float): The x-coordinate of the ball's position.
            y (float): The y-coordinate of the ball's position.
        """
        shape = Circle(radius=5)
        self.components += [
            Position(x=x, y=y),
            Velocity(dx=0, dy=0),
            PhysicsBody(
                mass=1.0,
                bounciness=DEFAULT_ELASTICITY,
                friction=DEFAULT_WALL_FRICTION,
                anchored=False,
            ),
            Collider(shape=shape),
            Renderable(colour=(255, 255, 255), shape=shape),
        ]
        return self

    def wall(self, x: float, y: float, width: int, height: int) -> "EntityBuilder":
        """
        Create a wall entity with specified position and dimensions.

        Args:
            x (float): The x-coordinate of the wall's position.
            y (float): The y-coordinate of the wall's position.
            width (int): The width of the wall.
            height (int): The height of the wall.
        """
        shape = Rect(width=width, height=height)
        self.components += [
            Position(x=x, y=y),
            Collider(shape=shape),
            Renderable(colour=(255, 0, 0), shape=shape),
            PhysicsBody(
                mass=float("inf"),
                bounciness=DEFAULT_ELASTICITY,
                friction=DEFAULT_WALL_FRICTION,
                anchored=True,
            ),
        ]
        return self

    def hole(self, x: float, y: float) -> "EntityBuilder":
        """
        Create a hole entity with specified position.

        Args:
            x (float): The x-coordinate of the hole's position.
            y (float): The y-coordinate of the hole's position.
        Returns:
            int: The entity ID of the created hole.
        """
        shape = Circle(radius=15)
        self.components += [
            Position(x=x, y=y),
            Collider(shape=shape),
            Renderable(colour=(91, 166, 0), shape=shape),
            Hole(),
        ]
        return self

    def velocity(self, dx: float, dy: float) -> "EntityBuilder":
        self.components.append(Velocity(dx=dx, dy=dy))
        return self

    def colour(self, rgb: tuple[int, int, int]) -> "EntityBuilder":
        for i, comp in enumerate(self.components):
            if isinstance(comp, Renderable):
                self.components[i] = Renderable(colour=rgb, shape=comp.shape)
                break
        return self

    def build(self) -> Entity:
        entity = Entity()
        for c in self.components:
            entity.add(c)
        self.components.clear()
        return entity
