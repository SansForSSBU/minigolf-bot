import sys
from pathlib import Path

import click
import pygame
from loguru import logger

from minigolf.components import Mode
from minigolf.constants import SIMULATION_SPEED
from minigolf.controllers import SequenceController
from minigolf.game.engine import Game
from minigolf.game.levels import create_level1
from minigolf.game.state import GameState
from minigolf.systems.rendering import render_system
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
def main_loop(world: World, *, mode: Mode = Mode.TURN) -> None:
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    game = Game(world=world, mode=mode, screen=screen)
    clock = pygame.time.Clock()

    win_at_ms: int | None = None
    win_banner: pygame.Surface | None = None
    win_snapshot: pygame.Surface | None = None

    # Add player
    game.add_player(SequenceController())

    running = True
    while running:
        # Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.step(1.0 / 60.0)

        # --- RENDER ---``
        if world.game_state is GameState.PLAYING:
            render_system(world, screen)
        else:
            if win_snapshot is None:
                win_snapshot = screen.copy()
                win_banner = build_win_banner(screen)
                logger.success("🏁 Win condition met!")

            if win_snapshot is not None:
                screen.blit(win_snapshot, (0, 0))
            if win_banner is not None:
                screen.blit(win_banner, (0, 0))

            if WIN_EXIT_DELAY_MS is not None and win_at_ms is None:
                win_at_ms = pygame.time.get_ticks()
            if WIN_EXIT_DELAY_MS is not None and win_at_ms is not None:
                if pygame.time.get_ticks() - win_at_ms >= WIN_EXIT_DELAY_MS:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60 * SIMULATION_SPEED)


@click.command()
@click.argument("path", type=click.Path(path_type=Path), required=False)
@click.option("--mode", type=click.Choice(["turn", "realtime"]), default="turn")
def cli(path: Path | None, mode: str) -> None:
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

    main_loop(world, mode=Mode(mode))


if __name__ == "__main__":
    cli()
