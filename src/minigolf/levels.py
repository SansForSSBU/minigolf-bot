"""
Levels for the minigolf game.

To export a level, use the `World.to_json` method to save the world state to a JSON file.
"""

from minigolf.world import World
from minigolf.objects import EntityBuilder


def create_level1(world: World) -> None:
    """
    Create the first level of the minigolf game.
    This level includes walls, a ball, and a hole.
    """
    # Ergonomic alias
    add = world.add_entity

    # Outer borders
    add(EntityBuilder().wall(100, 900, 800, 2).build())
    add(EntityBuilder().wall(900, 100, 2, 800).build())
    add(EntityBuilder().wall(100, 100, 800, 2).build())
    add(EntityBuilder().wall(100, 100, 2, 800).build())

    # Obstacle walls
    add(EntityBuilder().wall(100, 700, 600, 2).build())
    add(EntityBuilder().wall(700, 300, 2, 400).build())
    add(EntityBuilder().wall(300, 300, 400, 2).build())
    add(EntityBuilder().wall(300, 300, 2, 300).build())

    # Inner blockades
    add(EntityBuilder().wall(400, 600, 200, 2).build())
    add(EntityBuilder().wall(600, 400, 2, 200).build())
    add(EntityBuilder().wall(400, 400, 200, 2).build())

    # Ball
    add(EntityBuilder().ball(200, 800).velocity(dx=-1000, dy=-1000).build())

    # Hole
    add(EntityBuilder().hole(500, 500).build())
