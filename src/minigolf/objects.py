from enum import Enum
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


class EntityRole(str, Enum):
    BALL = "ball"
    WALL = "wall"
    HOLE = "hole"


class EntityBuilder:
    def __init__(self):
        self.components: list[BaseModel] = []
        self._role: EntityRole | None = None

    def _set_role(self, role: EntityRole) -> None:
        """
        Role: a type of entity being built (e.g. "ball", "wall", "hole").
        A builder can only be used for one role at a time.
        This method ensures the builder is locked to a specific role.
        This prevents accidental mixing of components across different entity types.
        """
        if self._role is None:
            self._role = role
        elif self._role != role:
            raise RuntimeError(
                f"EntityBuilder reused for multiple roles: {self._role} -> {role}"
            )

    def ball(self, x: float, y: float) -> "EntityBuilder":
        """
        Create a ball entity with specified position.

        Args:
            x (float): The x-coordinate of the ball's position.
            y (float): The y-coordinate of the ball's position.
        """
        self._set_role(EntityRole.BALL)
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
        self._set_role(EntityRole.WALL)
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
        self._set_role(EntityRole.HOLE)
        shape = Circle(radius=15)
        self.components += [
            Position(x=x, y=y),
            Collider(shape=shape),
            Renderable(colour=(91, 166, 0), shape=shape),
            Hole(),
        ]
        return self

    def velocity(self, dx: float, dy: float) -> "EntityBuilder":
        # Keep this strict: only valid while building a ball
        if self._role not in (None, EntityRole.BALL):
            raise RuntimeError("velocity() can only be used when building a ball")
        self.components.append(Velocity(dx=dx, dy=dy))
        return self

    def colour(self, rgb: tuple[int, int, int]) -> "EntityBuilder":
        for i, comp in enumerate(self.components):
            if isinstance(comp, Renderable):
                self.components[i] = Renderable(colour=rgb, shape=comp.shape)
                break
        else:
            raise RuntimeError(
                "colour() can only be used after adding a Renderable component"
            )
        return self

    def build(self) -> Entity:
        entity = Entity()
        for c in self.components:
            entity.add(c)
        self.components.clear()
        # Safely reset the role for reuse
        self._role = None
        return entity
