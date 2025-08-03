from pytest import approx

from minigolf.components import Collider, PhysicsBody, Position, Renderable, Velocity
from minigolf.objects import spawn
from minigolf.world import World


def test_ball_components():
    world = World()
    entity = spawn(world).ball(100, 200).velocity(dx=50, dy=-10).build()

    assert isinstance(entity.get(Position), Position)
    assert entity.get(Position).x == 100
    assert entity.get(Position).y == 200

    assert isinstance(entity.get(Velocity), Velocity)
    assert entity.get(Velocity).dx == 50
    assert entity.get(Velocity).dy == -10

    assert isinstance(entity.get(PhysicsBody), PhysicsBody)
    assert isinstance(entity.get(Collider), Collider)
    assert isinstance(entity.get(Renderable), Renderable)


def test_bulk_spawn_isolated():
    world = World()
    for i in range(10):
        e = spawn(world).ball(x=i * 10, y=0).build()
        assert e.get(Position).x == i * 10
        assert e.get(Velocity) is not None


def test_wall_is_static():
    world = World()
    entity = spawn(world).wall(0, 0, 100, 10).build()

    assert isinstance(entity.get(Position), Position)
    assert entity.get(Velocity) is None
    assert entity.get(PhysicsBody) is None


def test_hole_is_static_and_separate():
    world = World()
    s = spawn(world)

    ball = s.ball(50, 50).velocity(dx=10, dy=0).build()
    hole = s.hole(300, 300).build()

    assert ball.get(Velocity) is not None
    assert hole.get(Velocity) is None
    assert hole.get(PhysicsBody) is None


def test_reuse_safe_after_build():
    world = World()
    s = spawn(world)

    s.ball(10, 10).velocity(1, 2).build()
    entity = s.hole(500, 500).build()

    # Should not inherit Velocity or PhysicsBody
    assert entity.get(Velocity) is None
    assert entity.get(PhysicsBody) is None


def test_physics_applies_velocity():
    world = World()
    entity = spawn(world).ball(0, 0).velocity(5, 0).build()

    from minigolf.systems.physics import PhysicsSpace

    physics_space = PhysicsSpace(world)

    physics_space.populate()
    physics_space.step(1.0)

    pos = entity.get(Position)

    assert pos.x == approx(5.0)


def test_ball_hits_wall_and_stops():
    world = World()
    ball = spawn(world).ball(100, 100).velocity(100, 0).build()
    _ = spawn(world).wall(200, 100, width=20, height=20).build()

    from minigolf.systems.physics import PhysicsSpace

    physics = PhysicsSpace(world)
    physics.populate()

    # Step enough for ball to hit wall
    physics.step(1.0)

    pos = ball.get(Position)
    # Should not have passed through the wall
    assert pos.x < 200


def test_builder_clears_between_builds():
    world = World()
    s = spawn(world)

    s.ball(0, 0).velocity(5, 0).build()
    hole_entity = s.hole(100, 100).build()

    assert hole_entity.get(Velocity) is None
    assert hole_entity.get(PhysicsBody) is None
    assert hole_entity.get(Renderable).colour == (91, 166, 0)  # hole colour


def test_shape_matches_between_components():
    e = spawn(World()).ball(0, 0).build()

    collider = e.get(Collider)
    renderable = e.get(Renderable)

    assert collider.shape == renderable.shape


def test_custom_ball_colour():
    e = spawn(World()).ball(0, 0).colour((123, 45, 67)).build()
    assert e.get(Renderable).colour == (123, 45, 67)
