"""
Turn system: manages game flow in either 'turn' or 'realtime' modes.

Core responsibilities:
- Maintain a TurnManager entity holding the current phase and active player.
- Apply or consume Action components according to the phase.
- Switch phases as balls are struck, in motion, or stopped.
- Support strict turn-taking or freeform realtime action.

Contracts:
- Every turn-managed world has exactly one TurnManager (TurnState).
- Each player is tied to a ball entity (via Player(id)).
- Controllers add Action components to their player’s ball.
"""

from loguru import logger
from pymunk import Vec2d

from minigolf.components import Action, Phase, Player, TurnState, Velocity
from minigolf.constants import STOPPING_VELOCITY
from minigolf.entity import Entity
from minigolf.world import World

# Helpers for TurnManager lifecycle


def _get_turn_state_entity(world: World) -> Entity | None:
    """Return the single TurnManager entity, or None if missing."""
    matches = world.all_with(TurnState)
    return matches[0] if matches else None


def ensure_turn_manager(world: World, *, mode: str = "turn") -> Entity:
    """
    Ensure a TurnManager exists.
    - If one exists but in the wrong mode: replace with same progress, new mode.
    - If none exists: create with default state (phase=AWAIT_INPUT, player=0).
    """
    tm_e = _get_turn_state_entity(world)
    if tm_e:
        turn = tm_e.get(TurnState)
        if turn.mode != mode:
            tm_e.add(
                TurnState(
                    phase=turn.phase,
                    current_player=turn.current_player,
                    mode=mode,
                )
            )
            logger.debug(f"[Turn] Switched TurnManager mode → {mode}")
        return tm_e

    tm_e = world.create_entity()
    tm_e.add(TurnState(phase=Phase.AWAIT_INPUT, current_player=0, mode=mode))
    logger.debug(f"[Turn] Created TurnManager with mode={mode}")
    return tm_e


# Player / Ball lookup


def get_player_ball(world: World, player_id: int) -> Entity:
    """
    Return the ball entity for a player.
    Convention:
      - Ball entity carries Player(id=...).
      - Fallback: single-ball worlds without Player component.
    """
    candidates = [e for e in world.all_with(Player) if e.get(Player).id == player_id]
    if candidates:
        return candidates[0]
    return world.get_balls()[0]


# Action consumption / application


def consume_action(entity: Entity) -> Action | None:
    """
    Pop an Action component off the given entity (if present).
    Side effect: removes Action from entity once consumed.
    """
    act = entity.get(Action)
    if act:
        logger.debug(f"[Turn] Consuming {act.type} from Ball {entity.id}")
        entity.remove(Action)
        return act


def apply_action_to_body(action: Action, body) -> None:
    """
    Apply an Action directly to a pymunk body:
    - strike: set linear and angular velocity
    - reset: stop movement entirely
    - other: ignored
    """
    logger.debug(f"[Turn] Applying {action.type} with vel={action.velocity}")
    if action.type == "strike":
        body.velocity = Vec2d(*action.velocity)
        body.angular_velocity = action.angular_velocity
    elif action.type == "reset":
        body.velocity = Vec2d(0.0, 0.0)
        body.angular_velocity = 0.0


# Turn system entry point


def turn_system(world: World, physics) -> None:
    """
    Main gameplay loop logic for turn progression.

    Modes:
      - 'turn': strict turn-taking with phases.
      - 'realtime': apply actions every frame immediately.
    """
    turn_manager: Entity = ensure_turn_manager(world)
    turn: TurnState | None = turn_manager.get(TurnState)
    players = list(world.all_with(Player)) or [None]

    player_id: int = turn.current_player
    ball = get_player_ball(world=world, player_id=player_id)
    body = physics.eid_to_body[ball.id].body

    if turn.mode == "realtime":
        _realtime_tick(world, physics)
        return

    match turn.phase:
        case Phase.AWAIT_INPUT:
            if ball.get(Action):
                logger.debug(f"[Turn] Player {player_id} provided an action")
                turn.phase = Phase.APPLY_ACTION

        case Phase.APPLY_ACTION:
            logger.debug(f"[Turn] Phase=APPLY_ACTION for player {player_id}")
            action = consume_action(ball)
            if action:
                apply_action_to_body(action=action, body=body)
                logger.debug("[Turn] Transition: APPLY_ACTION → BALL_IN_MOTION")
                turn.phase = Phase.BALL_IN_MOTION
            else:
                logger.debug("[Turn] No action found, reverting to AWAIT_INPUT")
                turn.phase = Phase.AWAIT_INPUT

        case Phase.BALL_IN_MOTION:
            if body.velocity.length < STOPPING_VELOCITY:
                if vel := ball.get(Velocity):
                    vel.dx, vel.dy = body.velocity
                logger.debug("[Turn] Ball stopped, transitioning to RESOLVE")
                turn.phase = Phase.RESOLVE

        case Phase.RESOLVE:
            logger.debug(f"[Turn] Phase=RESOLVE, switching from player {player_id}")
            turn.current_player = (turn.current_player + 1) % len(players)
            logger.debug(f"[Turn] Next player → {turn.current_player}")
            turn.phase = Phase.AWAIT_INPUT


# Realtime mode


def _realtime_tick(world: World, physics) -> None:
    """
    In realtime mode:
    - Any entity with an Action gets it applied immediately.
    - No phases or strict sequencing.
    """
    for e in world.entities.values():
        act = consume_action(e)
        if not act:
            continue
        if e.id not in physics.eid_to_body:
            continue
        body = physics.eid_to_body[e.id].body
        logger.debug(f"[Realtime] Applying action {act.type} to entity {e.id}")
        apply_action_to_body(act, body)
