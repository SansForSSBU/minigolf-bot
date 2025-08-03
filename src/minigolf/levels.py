"""
Levels for the minigolf game.

To export a level, use the `World.to_json` method to save the world state to a JSON file.
"""

from minigolf.world import World
from minigolf.objects import spawn


def create_level1(world: World) -> None:
    """
    Create the first level of the minigolf game.
    This level includes walls, a ball, and a hole.
    """
    # Ergonomic alias
    add = world.add_entity

    # Outer borders
    add(spawn().wall(100, 900, 800, 2).build())
    add(spawn().wall(900, 100, 2, 800).build())
    add(spawn().wall(100, 100, 800, 2).build())
    add(spawn().wall(100, 100, 2, 800).build())

    # Obstacle walls
    add(spawn().wall(100, 700, 600, 2).build())
    add(spawn().wall(700, 300, 2, 400).build())
    add(spawn().wall(300, 300, 400, 2).build())
    add(spawn().wall(300, 300, 2, 300).build())

    # Inner blockades
    add(spawn().wall(400, 600, 200, 2).build())
    add(spawn().wall(600, 400, 2, 200).build())
    add(spawn().wall(400, 400, 200, 2).build())

    # Ball
    add(spawn().ball(200, 800).velocity(dx=-1000, dy=-1000).build())

    # Hole
    add(spawn().hole(500, 500).build())
