from minigolf.components import (
    Collider,
    PhysicsBody,
    Position,
    Renderable,
    Velocity,
    Shape,
)
from minigolf.world import World

# Entity creation


def create_ball(world: World, x: float, y: float, dx: float, dy: float) -> int:
    """
    Create a ball entity with specified position and velocity.

    Args:
        world (World): The game world to add the ball to.
        x (float): The x-coordinate of the ball's position.
        y (float): The y-coordinate of the ball's position.
        dx (float): The x-component of the ball's velocity.
        dy (float): The y-component of the ball's velocity.
    Returns:
        int: The entity ID of the created ball.
    """
    ball = world.create_entity()
    shape = Shape(type="rect", width=10, height=10)
    # Add components to the ball entity
    world.components[Position][ball] = Position(x=x, y=y)
    world.components[Velocity][ball] = Velocity(dx=dx, dy=dy)
    world.components[PhysicsBody][ball] = PhysicsBody(
        mass=1.0, bounciness=0.9, friction=0.01
    )
    world.components[Collider][ball] = Collider(shape=shape)
    world.components[Renderable][ball] = Renderable(colour=(255, 255, 255), shape=shape)

    return ball


def create_wall(world: World, x: float, y: float, width: int, height: int) -> int:
    """
    Create a wall entity with specified position and dimensions.

    Args:
        world (World): The game world to add the wall to.
        x (float): The x-coordinate of the wall's position.
        y (float): The y-coordinate of the wall's position.
        width (float): The width of the wall.
        height (float): The height of the wall.
    Returns:
        int: The entity ID of the created wall.
    """
    wall = world.create_entity()

    # Add components to the wall entity
    shape = Shape(type="rect", width=width, height=height)
    world.components[Position][wall] = Position(x=x, y=y)
    world.components[Collider][wall] = Collider(shape=shape)
    world.components[Renderable][wall] = Renderable(colour=(255, 0, 0), shape=shape)

    return wall


def create_hole(world: World, x: float, y: float) -> int:
    """
    Create a hole entity with specified position.

    Args:
        world (World): The game world to add the hole to.
        x (float): The x-coordinate of the hole's position.
        y (float): The y-coordinate of the hole's position.
    Returns:
        int: The entity ID of the created hole.
    """
    shape = Shape(type="rect", width=20, height=20)
    hole = world.create_entity()

    # Add components to the hole entity
    world.components[Position][hole] = Position(x=x, y=y)
    world.components[Collider][hole] = Collider(shape=shape)
    world.components[Renderable][hole] = Renderable(colour=(91, 166, 0), shape=shape)

    return hole
