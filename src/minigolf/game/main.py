import sys
from pathlib import Path

import click
import pygame
from loguru import logger

from minigolf.game.levels import create_level1
from minigolf.systems.physics import PhysicsSpace
from minigolf.systems.rendering import render_system
from minigolf.systems.control import control_system
from minigolf.world import World
from minigolf.constants import SIMULATION_SPEED


# Game loop runner
def main_loop(world: World) -> None:
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    physics_system = PhysicsSpace(world)
    physics_system.populate()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        physics_system.step()
        control_system(world, physics_system)
        render_system(world, screen)
        pygame.display.flip()
        clock.tick(60 * SIMULATION_SPEED)


@click.command()
@click.argument("path", type=click.Path(path_type=Path), required=False)
def cli(path: Path | None) -> None:
    """
    Run the game.

    - If PATH is provided, load the world from a JSON file.
    - Otherwise, build and run the default 'level1' from code.
    """

    if path:
        if not path.exists():
            logger.error(f"File not found: {path}")
            sys.exit(1)
        logger.info(f"📂 Loading world from {path}")
        world = World.from_json(path)
    else:
        logger.info("🧱 Creating default level1 from code")
        world = World()
        create_level1(world)

    main_loop(world)


if __name__ == "__main__":
    cli()
