from typing import TYPE_CHECKING

from loguru import logger

from minigolf.components import Action
from minigolf.consts import DEFAULT_MOVES
from minigolf.controllers import Controller
from minigolf.world import World

if TYPE_CHECKING:
    from pymunk import Vec2d


class SequenceController(Controller):
    """Plays from a fixed sequence of moves one by one."""

    def __init__(self, moves=DEFAULT_MOVES):
        self._moves: list[list[Vec2d | float]] = list(moves)
        self._i = 0

    def act(self, world: World, player_id: int) -> Action | None:
        if self._i >= len(self._moves):
            return None
        v, av = self._moves[self._i]
        self._i += 1
        logger.debug(f"[SeqCtrl] Player {player_id} move {self._i}")
        return Action(
            type="strike",
            velocity=(float(v.x), float(v.y)),
            angular_velocity=float(av),
        )
