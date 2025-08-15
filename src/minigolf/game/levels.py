"""
Levels for the minigolf game.

To export a level, use the `World.to_json` method.
This saves the world state to a JSON file.
"""

from pathlib import Path

from loguru import logger

from minigolf.objects import EntityBuilder
from minigolf.world import World


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
    add(EntityBuilder().ball(200, 800).velocity(dx=0, dy=0).build())

    # Hole
    add(EntityBuilder().hole(500, 500).build())


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        logger.debug("Usage: python -m minigolf.levels <output_file.json>")
        sys.exit(1)
    output_path = Path(sys.argv[1])
    world = World()
    create_level1(world)
    world.to_json(output_path)
    logger.debug(f"Level 1 exported to {output_path}")
