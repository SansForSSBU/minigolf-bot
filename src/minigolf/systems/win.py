from dataclasses import dataclass

from loguru import logger

from minigolf.components import Circle, Collider, Hole, Position, Velocity
from minigolf.entity import Entity
from minigolf.world import World

VELOCITY_THRESHOLD = 2.0


@dataclass(frozen=True)
class WinEvent:
    ball_eid: int
    hole_eid: int
    distance: float
    speed: float


def _first(world: World, *types) -> Entity | None:
    return next((e for e in world.all_with(*types)), None)


def win_condition_system(world: World) -> WinEvent | None:
    """
    Returns a WinEvent if the win condition is met, otherwise None.

    The win condition is met when a ball enters a hole with velocity below a threshold.

    Contract:
        - There must be exactly one ball in the world.
        - There must be exactly one hole in the world.
        - The ball must be moving slowly enough when it enters the hole.
    """
    hole = _first(world, Hole, Position, Collider)
    if not hole or hole.id is None:
        logger.error("No hole found in the world")
        return None

    balls = world.get_balls()

    if len(balls) != 1:
        logger.error("Win condition check failed: no hole or multiple balls")
        return None

    ball = balls[0]

    hp, hc = hole.get(Position), hole.get(Collider)
    bp, bv = ball.get(Position), ball.get(Velocity)

    if not (
        isinstance(hp, Position)
        and isinstance(bp, Position)
        and isinstance(hc, Collider)
        and isinstance(bv, Velocity)
    ):
        logger.error("Invalid components for win condition check")
        return None

    if not isinstance(hc.shape, Circle):
        logger.error("Hole shape is not a Circle")
        return None

    dx, dy = bp.x - hp.x, bp.y - hp.y
    dist2 = dx * dx + dy * dy
    r = hc.shape.radius
    in_hole = dist2 <= r * r

    speed2 = bv.dx * bv.dx + bv.dy * bv.dy
    slow = speed2 <= VELOCITY_THRESHOLD * VELOCITY_THRESHOLD

    if in_hole and slow:
        logger.debug(
            f"Win condition met: Ball {ball.id}"
            f"in Hole {hole.id} with distance {dist2**0.5} and speed {speed2**0.5}"
        )
        return WinEvent(ball.id, hole.id, dist2**0.5, speed2**0.5)
    return None
