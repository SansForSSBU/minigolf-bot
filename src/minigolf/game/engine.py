"""
Game engine: orchestrates the high-level loop of play.

Responsibilities:
- Manage world + physics + turn system integration.
- Attach controllers to player balls.
- Step simulation forward each frame (input → physics → rules → win).
- Stop game once win condition is reached.
"""

from dataclasses import dataclass, field

import pygame
from loguru import logger

from minigolf.components import Mode, Phase, Player, TurnState
from minigolf.controllers import Controller
from minigolf.entity import Entity
from minigolf.game.state import GameState
from minigolf.observation import observe
from minigolf.systems.physics import PhysicsSpace
from minigolf.systems.turn import ensure_turn_manager, get_player_ball, turn_system
from minigolf.systems.win import win_condition_system
from minigolf.world import World


@dataclass
class Game:
    """
    Central game engine object.

    Fields:
    - world: ECS world holding entities/components
    - mode: gameplay mode (turn or realtime)
    - screen: optional pygame surface for rendering
    - controllers: mapping of player_id -> Controller
    """

    world: World
    mode: Mode
    screen: pygame.Surface | None = None
    controllers: dict[int, Controller] = field(default_factory=dict)

    def __post_init__(self):
        # Initialise physics and turn manager
        self.physics = PhysicsSpace(self.world)
        self.physics.populate()
        ensure_turn_manager(self.world, mode=self.mode)

    # Player & controller management

    def add_player(self, controller: Controller) -> int:
        """
        Assign a new player_id to a controller.
        - Reuse the first unclaimed ball (i.e. missing Player component).
        - Attach Player(id) to the ball.
        """
        player_id = len(self.controllers)

        for ball in self.world.get_balls():
            if not ball.get(Player):
                ball.add(Player(id=player_id))
                self.controllers[player_id] = controller
                logger.info(f"[Game] Assigned Player {player_id} to Ball {ball.id}")
                return player_id

        raise RuntimeError("No free ball to assign!")

    def request_action(self, player_id: int) -> None:
        """
        Poll a player’s controller for an Action and attach it to their ball.
        (Low-level helper; step() uses _maybe_request_action.)
        """
        ctrl: Controller | None = self.controllers.get(player_id)
        if ctrl is None:
            return

        ball = get_player_ball(world=self.world, player_id=player_id)
        if ball.id is None:
            e: str = f"{player_id=} ball has no id"
            logger.exception(e)
            return

        obs = observe(self.world, ball.id)
        act = ctrl.act(obs, player_id)
        if act:
            ball.add(act)

    # Frame loop

    def step(self, dt: float):
        """
        Advance one tick of the game loop:
        1. Poll controller if waiting for input
        2. Advance physics
        3. Apply turn logic
        4. Check win condition
        """
        # Freeze if game is already won
        if self.world.game_state is GameState.WON:
            return

        # 1. Poll controllers only if TurnManager wants input
        tm = self._get_turn_manager()
        if tm and tm.get(TurnState).phase is Phase.AWAIT_INPUT:
            pid = tm.get(TurnState).current_player
            self.request_action(pid)

        # 2. Physics integration
        self.physics.step(dt)

        # 3. Gameplay rules (turn system)
        turn_system(self.world, self.physics)

        # 4. Win condition check
        evt = win_condition_system(self.world)
        if evt:
            self.world.game_state = GameState.WON
            logger.debug("[Game] Win detected, halting loop")
            return evt

    def _get_turn_manager(self) -> Entity | None:
        """Return the TurnManager entity, if any."""
        matches = self.world.all_with(TurnState)
        if len(matches) > 1:
            raise RuntimeError("Multiple TurnManager entities found!")
        return matches[0] if matches else None
