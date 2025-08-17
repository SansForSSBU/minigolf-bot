from dataclasses import dataclass

from loguru import logger

from minigolf.components import Circle, Collider, Hole, Position, Velocity
from minigolf.consts import (
    FUNNEL_DAMPING,
    FUNNEL_RADIUS,
    FUNNEL_STRENGTH,
    VELOCITY_THRESHOLD,
)
from minigolf.entity import Entity
from minigolf.world import World


@dataclass(frozen=True)
class WinEvent:
    """Represents a single ball sinking into the hole."""

    ball_eid: int
    hole_eid: int
    distance: float
    speed: float


def _first(world: World, *types) -> Entity | None:
    """Return the first entity matching all given component types, or None."""
    return next((e for e in world.all_with(*types)), None)


def apply_funnel(
    ball: Entity,
    hole: Entity,
    radius: float = FUNNEL_RADIUS,
    strength: float = FUNNEL_STRENGTH,
    damping: float = FUNNEL_DAMPING,
) -> None:
    """
    Funnel mechanic:
    - If a ball is within `radius` of the hole centre, apply a gentle force
      nudging it toward the hole.
    - Force is proportional to distance, direction is normalised toward hole.
    - Damping reduces velocity each step so it doesn’t spiral endlessly.
    """
    ball_pos, ball_vel = ball.get(Position), ball.get(Velocity)
    hole_pos = hole.get(Position)

    dx, dy = hole_pos.x - ball_pos.x, hole_pos.y - ball_pos.y
    dist2 = dx * dx + dy * dy
    if dist2 > radius * radius:
        return  # outside funnel zone, do nothing

    dist = dist2**0.5
    if dist < 1e-6:
        return  # already at hole centre (avoid divide by zero)

    # Normalised direction vector pointing ball → hole
    nx, ny = dx / dist, dy / dist

    # Update velocity with funnel pull + damping
    ball_vel.dx = ball_vel.dx * damping + nx * strength * dist
    ball_vel.dy = ball_vel.dy * damping + ny * strength * dist


def win_condition_system(world: World) -> list[WinEvent]:
    """
    Check if balls have been sunk into the hole.

    Behaviour:
    - Funnel: any ball within a funnel radius is gently pulled toward hole centre.
    - Win: a ball counts as sunk when:
        1. Ball + hole colliders overlap (distance ≤ combined radii).
        2. Ball is moving slower than VELOCITY_THRESHOLD.
    - On win: ball is snapped to hole centre and frozen.
    - Multiple balls are supported: return a list of WinEvent, possibly empty.

    Contracts:
    - Exactly one hole must exist.
    - Hole collider must be a Circle.
    """
    hole = _first(world, Hole, Position, Collider)
    if not hole or hole.id is None:
        logger.error("No hole found in the world")
        return []

    hole_pos = hole.get(Position)
    hole_col = hole.get(Collider)

    if hole_col is None or not isinstance(hole_col.shape, Circle):
        logger.error("Hole collider missing or not a Circle")
        return []

    hole_radius = hole_col.shape.radius
    funnel_extra = 40.0  # extra reach beyond hole radius for funnel effect

    events: list[WinEvent] = []
    for ball in world.get_balls():
        ball_pos = ball.get(Position)
        ball_vel = ball.get(Velocity)
        ball_col = ball.get(Collider)

        if not (
            isinstance(ball_pos, Position)
            and isinstance(ball_vel, Velocity)
            and isinstance(ball_col, Collider)
        ):
            continue
        if ball_col.shape is None or not isinstance(ball_col.shape, Circle):
            continue
        if ball.id is None or hole.id is None:
            continue

        dx, dy = ball_pos.x - hole_pos.x, ball_pos.y - hole_pos.y
        dist2 = dx * dx + dy * dy
        dist = dist2**0.5

        ball_radius = ball_col.shape.radius
        speed = (ball_vel.dx * ball_vel.dx + ball_vel.dy * ball_vel.dy) ** 0.5

        # Funnel zone check
        if dist2 <= (hole_radius + ball_radius + funnel_extra) ** 2:
            apply_funnel(ball, hole)

        # Win condition check
        in_hole = dist2 <= (hole_radius + ball_radius) ** 2
        slow_enough = (
            ball_vel.dx * ball_vel.dx + ball_vel.dy * ball_vel.dy
        ) <= VELOCITY_THRESHOLD**2

        if in_hole:
            logger.debug(
                f"[HoleEntry] Ball {ball.id} entered Hole {hole.id} "
                f"dist={dist:.2f}, speed={speed:.2f}"
            )
            if slow_enough:
                logger.info(
                    f"[Win] Ball {ball.id} captured in Hole {hole.id} "
                    f"dist={dist:.2f}, speed={speed:.2f}"
                )
                # Snap ball to hole centre and freeze
                ball_pos.x, ball_pos.y = hole_pos.x, hole_pos.y
                ball_vel.dx, ball_vel.dy = 0.0, 0.0
                events.append(WinEvent(ball.id, hole.id, dist, speed))

    return events
