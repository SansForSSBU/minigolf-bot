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
    s = spawn(world)

    # Outer borders
    s.wall(100, 900, 800, 2).build()
    s.wall(900, 100, 2, 800).build()
    s.wall(100, 100, 800, 2).build()
    s.wall(100, 100, 2, 800).build()

    # Obstacle walls
    s.wall(100, 700, 600, 2).build()
    s.wall(700, 300, 2, 400).build()
    s.wall(300, 300, 400, 2).build()
    s.wall(300, 300, 2, 300).build()

    # Inner blockades
    s.wall(400, 600, 200, 2).build()
    s.wall(600, 400, 2, 200).build()
    s.wall(400, 400, 200, 2).build()

    # Ball
    s.ball(200, 800).velocity(dx=-1000, dy=-1000).build()

    # Hole
    s.hole(500, 500).build()
