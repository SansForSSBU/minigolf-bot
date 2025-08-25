from collections.abc import Iterator
from dataclasses import dataclass

from minigolf.components import Circle, Collider, Hole, Position, Velocity
from minigolf.entity import Entity
from minigolf.world import World


class ObservationError(RuntimeError):
    """World is malformed for observation (missing components, no holes, etc.)."""


@dataclass(frozen=True, slots=True)
class Observation:
    ball_pos: tuple[float, float]
    ball_vel: tuple[float, float]
    hole_vec: tuple[float, float]
    r_ball: float
    r_hole: float


def observe(world: World, ball_id: int) -> Observation:
    """
    Build a single-ball, ego-centric observation.

    Contract:
    - Ball must have Position, Velocity, and a Circle Collider.
    - World must contain at least one Hole (Circle Collider).
        If multiple holes exist, the nearest hole to the ball is used.

    Raises:
        ObservationError: if required components/entities are missing.
    """
    ball = world.get_entity(ball_id)
    bpos, bvel, bcol = _require_ball_components(ball)

    hole = _nearest_hole(world, bpos)
    if hole is None:
        raise ObservationError("No hole entities found")

    hpos, hcol = hole.get(Position), hole.get(Collider)
    if not (hpos and hcol and isinstance(hcol.shape, Circle)):
        raise ObservationError("Hole needs Position and Circle Collider")

    hx, hy = hpos.x - bpos.x, hpos.y - bpos.y

    return Observation(
        ball_pos=(bpos.x, bpos.y),
        ball_vel=(bvel.dx, bvel.dy),
        hole_vec=(hx, hy),
        r_ball=bcol.shape.radius,
        r_hole=hcol.shape.radius,
    )


def _require_ball_components(ball: Entity) -> tuple[Position, Velocity, Collider]:
    bpos = ball.get(Position)
    bvel = ball.get(Velocity)
    bcol = ball.get(Collider)
    if not (bpos and bvel and bcol and isinstance(bcol.shape, Circle)):
        raise ObservationError("Ball needs Position, Velocity, and Circle Collider")
    return bpos, bvel, bcol


def _iter_holes(world: World) -> Iterator[Entity]:
    yield from world.all_with(Hole, Position, Collider)


def _nearest_hole(world: World, bpos: Position) -> Entity | None:
    holes = list(_iter_holes(world))
    if not holes:
        return None
    return min(holes, key=lambda h: _sqdist(h.get(Position), bpos))


def _sqdist(p1: Position | None, p2: Position) -> float:
    if p1 is None:
        return float("inf")
    dx, dy = p1.x - p2.x, p1.y - p2.y
    return dx * dx + dy * dy
