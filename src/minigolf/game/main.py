import sys
from pathlib import Path

import click
import pygame
from loguru import logger

from minigolf.constants import SIMULATION_SPEED
from minigolf.game.levels import create_level1
from minigolf.game.state import GameState
from minigolf.systems.control import ControlSystem
from minigolf.systems.physics import PhysicsSpace
from minigolf.systems.rendering import render_system
from minigolf.systems.win import win_condition_system
from minigolf.world import World

ARM_DELAY_S = 0.5
WIN_EXIT_DELAY_MS = 2000  # set to None to disable auto-exit


def build_win_banner(screen: pygame.Surface) -> pygame.Surface:
    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 150))
    font = pygame.font.SysFont(None, 72)
    text = font.render("WINNER!", True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    surf.blit(text, rect)
    return surf


# Game loop runner
def main_loop(world: World) -> None:
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    physics_system = PhysicsSpace(world)
    physics_system.populate()

    balls = world.get_balls()
    if len(balls) != 1:
        raise ValueError("World should only have 1 ball")

    ball_body = physics_system.eid_to_body[balls[0].id]
    control_system = ControlSystem(ball_body, world, physics_system)
    clock = pygame.time.Clock()

    start_ticks = pygame.time.get_ticks()
    win_at_ms: int | None = None
    win_banner: pygame.Surface | None = None
    win_snapshot: pygame.Surface | None = None  # <- snapshot of scene at win time

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if world.game_state is GameState.PLAYING:
            physics_system.step()
            control_system.step()

            armed = (pygame.time.get_ticks() - start_ticks) / 1000.0 >= ARM_DELAY_S
            if armed and win_condition_system(world):
                world.game_state = GameState.WON
                win_at_ms = pygame.time.get_ticks()

                # Render once to capture the scene, then snapshot it
                # No need to render the game anymore. Fixes flashing
                render_system(world, screen)
                win_snapshot = screen.copy()
                win_banner = build_win_banner(screen)
                logger.success("🏁 Win condition met!")

        if world.game_state is GameState.PLAYING:
            # Normal render path
            render_system(world, screen)
        else:
            # WON: show the frozen scene + overlay (no flicker, no re-render)
            if win_snapshot is not None:
                screen.blit(win_snapshot, (0, 0))
            if win_banner is not None:
                screen.blit(win_banner, (0, 0))
            if WIN_EXIT_DELAY_MS is not None and win_at_ms is not None:
                if pygame.time.get_ticks() - win_at_ms >= WIN_EXIT_DELAY_MS:
                    pygame.quit()
                    sys.exit()

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
