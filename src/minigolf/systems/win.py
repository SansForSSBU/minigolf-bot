from dataclasses import dataclass
from math import hypot

from loguru import logger

from minigolf.components import Circle, Collider, Hole, Position, Velocity
from minigolf.consts import (
    FUNNEL_DAMPING,
    FUNNEL_EXTRA,
    FUNNEL_RADIUS,
    FUNNEL_STRENGTH,
    VELOCITY_THRESHOLD,
)
from minigolf.entity import Entity
from minigolf.world import World

# Numerical guard for zero-length vectors
EPS = 1e-6


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

    # Offset vector
    ox = hole_pos.x - ball_pos.x
    oy = hole_pos.y - ball_pos.y
    sep_sq = ox * ox + oy * oy
    if sep_sq > radius * radius:
        # Outside funnel zone
        return

    sep = hypot(ox, oy)

    # Already at centre; avoid divide-by-zero
    if sep < EPS:
        return

    # Unit direction * scaled pull
    pull_mag = strength * sep
    inv_sep = 1.0 / sep
    nx, ny = ox * inv_sep, oy * inv_sep

    # Damped current velocity + pull
    ball_vel.dx = ball_vel.dx * damping + nx * pull_mag
    ball_vel.dy = ball_vel.dy * damping + ny * pull_mag


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

        ball_radius = ball_col.shape.radius

        # Geometry
        # Offset vectors
        ox = ball_pos.x - hole_pos.x
        oy = ball_pos.y - hole_pos.y
        sep_sq = ox * ox + oy * oy
        r_contact = hole_radius + ball_radius
        r_funnel = r_contact + FUNNEL_EXTRA

        # Kinematics
        vx, vy = ball_vel.dx, ball_vel.dy
        speed_sq = vx * vx + vy * vy

        # Funnel zone
        if sep_sq <= r_funnel * r_funnel:
            apply_funnel(ball, hole)

        # Win condition check
        in_hole = sep_sq <= r_contact * r_contact
        slow_enough = speed_sq <= VELOCITY_THRESHOLD * VELOCITY_THRESHOLD

        if in_hole:
            sep = hypot(ox, oy)
            speed = hypot(vx, vy)
            logger.debug(
                f"[HoleEntry] Ball {ball.id} -> Hole {hole.id}"
                f" dist={sep:.2f}, speed={speed:.2f}"
            )
            if slow_enough:
                logger.info(
                    f"[Win] Ball {ball.id} captured in Hole {hole.id} "
                    f" dist={sep:.2f}, speed={speed:.2f}"
                )
                # Snap + freeze
                ball_pos.x, ball_pos.y = hole_pos.x, hole_pos.y
                ball_vel.dx = ball_vel.dy = 0.0
                events.append(WinEvent(ball.id, hole.id, sep, speed))

    return events
