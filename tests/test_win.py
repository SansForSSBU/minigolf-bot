# TODO: Explore multiple controllers at once
import math

from minigolf.components import Circle, Collider
from minigolf.constants import STOPPING_VELOCITY, VELOCITY_THRESHOLD
from minigolf.objects import EntityBuilder
from minigolf.systems.win import win_condition_system
from minigolf.world import World


def test_stop_vs_win_threshold_consistency():
    assert STOPPING_VELOCITY <= VELOCITY_THRESHOLD, (
        "Game may resolve turns while the ball is still too fast for win condition"
    )


def _add_ball(world: World, x: float, y: float, dx: float = 0, dy: float = 0):
    e = EntityBuilder().ball(x, y).velocity(dx, dy).build()
    world.add_entity(e)
    return e


def _add_hole(world: World, x: float, y: float, r: float = 15):
    e = EntityBuilder().hole(x, y, radius=r).build()
    col = e.get(Collider)
    assert isinstance(col.shape, Circle)
    assert col.shape.radius == r
    world.add_entity(e)
    return e


def test_ball_rolls_into_hole_triggers_win():
    world = World()
    _ = _add_hole(world, 100, 100, r=15)
    _ = _add_ball(world, 100 + 20, 100, dx=-1, dy=0)

    # fake a few physics steps
    from minigolf.systems.physics import PhysicsSpace

    physics = PhysicsSpace(world)
    physics.populate()
    for _ in range(60):  # simulate ~1 second
        physics.step()

    evt = win_condition_system(world)
    assert evt is not None, "Ball should eventually be counted as in hole"


def test_win_true_when_inside_and_slow():
    world = World()
    hole = _add_hole(world, 100, 100, r=15)
    ball = _add_ball(world, 100, 100, dx=0, dy=0)  # centre on centre, speed 0
    evt = win_condition_system(world)[0]
    assert evt is not None
    assert evt.ball_eid == ball.id
    assert evt.hole_eid == hole.id
    assert evt.distance == 0
    assert evt.speed == 0


def test_win_false_when_outside_radius():
    world = World()
    _add_hole(world, 100, 100, r=15)
    _add_ball(world, 200, 200, dx=0, dy=0)  # far away
    assert len(win_condition_system(world)) == 0


def test_win_false_when_fast_inside():
    world = World()
    _add_hole(world, 100, 100, r=15)
    # place ball centre exactly at hole centre but too fast
    # slightly above threshold to avoid float-equality issues
    speed = VELOCITY_THRESHOLD + 0.1
    _add_ball(world, 100, 100, dx=speed, dy=0)
    assert len(win_condition_system(world)) == 0


def test_win_true_on_edge_of_radius_and_slow():
    world = World()
    _add_hole(world, 100, 100, r=15)
    # place ball exactly on the edge of the radius (distance == r), zero speed
    _add_ball(world, 115, 100, dx=0, dy=0)
    evt = win_condition_system(world)[0]
    assert evt is not None
    assert math.isclose(evt.distance, 15, rel_tol=1e-6, abs_tol=1e-6)


def test_requires_hole_present():
    world = World()
    _add_ball(world, 100, 100, dx=0, dy=0)
    assert len(win_condition_system(world)) == 0
