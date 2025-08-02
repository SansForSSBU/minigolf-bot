"""
Levels for the minigolf game.

To export a level, use the `World.to_json` method to save the world state to a JSON file
"""

from minigolf.world import World
from minigolf.objects import create_wall, create_ball, create_hole


def create_level1(world: World) -> None:
    """
    Create the first level of the minigolf game.
    This level includes walls, a ball, and a hole.
    """
    # Clear the world before creating the level
    # Outer borders
    create_wall(world, 100, 900, 800, 0)
    create_wall(world, 900, 900, 0, -800)
    create_wall(world, 900, 100, -800, 0)
    create_wall(world, 100, 100, 0, 800)

    # Obstacle walls
    create_wall(world, 100, 700, 600, 0)
    create_wall(world, 700, 700, 0, -400)
    create_wall(world, 700, 300, -400, 0)
    create_wall(world, 300, 300, 0, 300)

    # Inner blockades
    create_wall(world, 400, 600, 200, 0)
    create_wall(world, 600, 600, 0, -200)
    create_wall(world, 600, 400, -200, 0)

    # Ball
    create_ball(world, 200, 800, dx=0, dy=0)

    # Hole
    create_hole(world, 500, 500)
