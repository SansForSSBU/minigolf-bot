import sys
import click
import pygame
from pygame import Surface
from loguru import logger

from minigolf.editor.state import State, init_state
from minigolf.editor.ui import setup_ui
from minigolf.editor.actions import handle_event, handle_drag
from minigolf.editor.draw import draw_everything


def main_loop() -> None:
    pygame.init()
    screen: Surface = pygame.display.set_mode(
        (State.SCREEN_WIDTH, State.SCREEN_HEIGHT), vsync=1
    )
    pygame.display.set_caption("Minigolf Level Editor")
    clock = pygame.time.Clock()

    state = init_state(screen)
    setup_ui(state)
    logger.info("Editor initialised.")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        state.update_mouse()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Exiting editor.")
                running = False
            else:
                handle_event(event, state)

        handle_drag(state)
        draw_everything(screen, state)
        state.manager.update(dt)
        state.manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


@click.command()
@click.option("--debug", is_flag=True, help="Run in debug mode.")
def cli(debug: bool) -> None:
    if debug:
        logger.info("Debug mode enabled.")
    main_loop()


if __name__ == "__main__":
    cli()
