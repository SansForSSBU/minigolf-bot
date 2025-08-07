from minigolf.components import Collider, PhysicsBody, Position, Renderable, Velocity
from minigolf.objects import EntityBuilder
from minigolf.world import World


def test_ball_components():
    entity = EntityBuilder().ball(x=100, y=200).velocity(dx=50, dy=-10).build()

    assert isinstance(pos := entity.get(Position), Position)
    assert pos.x == 100
    assert pos.y == 200

    assert isinstance(vel := entity.get(Velocity), Velocity)
    assert vel.dx == 50
    assert vel.dy == -10

    assert isinstance(entity.get(PhysicsBody), PhysicsBody)
    assert isinstance(entity.get(Collider), Collider)
    assert isinstance(entity.get(Renderable), Renderable)


def test_bulk_EntityBuilder_isolated():
    world = World()
    for i in range(10):
        e = EntityBuilder().ball(x=i * 10, y=0).build()
        world.add_entity(e)
        assert (pos := e.get(Position)) is not None
        assert pos.x == i * 10
        assert e.get(Velocity) is not None


def test_wall_is_static():
    world = World()
    entity = EntityBuilder().wall(x=0, y=0, width=100, height=10).build()
    world.add_entity(entity)

    assert isinstance(entity.get(Position), Position)
    assert entity.get(Velocity) is None
    assert entity.get(PhysicsBody).anchored is True


def test_hole_is_static_and_separate():
    world = World()
    s = EntityBuilder()

    ball = s.ball(x=50, y=50).velocity(dx=10, dy=0).build()
    hole = s.hole(x=300, y=300).build()

    world.add_entity(ball)
    world.add_entity(hole)

    assert ball.get(Velocity) is not None
    assert hole.get(Velocity) is None
    assert hole.get(PhysicsBody) is None


def test_reuse_safe_after_build():
    world = World()
    s = EntityBuilder()

    world.add_entity(s.ball(x=10, y=10).velocity(dx=1, dy=2).build())
    entity = s.hole(x=500, y=500).build()
    world.add_entity(entity)

    assert entity.get(Velocity) is None
    assert entity.get(PhysicsBody) is None


def test_physics_applies_velocity():
    world = World()
    entity = EntityBuilder().ball(x=0, y=0).velocity(dx=5, dy=0).build()
    world.add_entity(entity)

    from minigolf.systems.physics import PhysicsSpace

    physics_space = PhysicsSpace(world)
    physics_space.populate()
    physics_space.step(1.0)

    assert (pos := entity.get(Position)) is not None
    assert pos.x >= 2


def test_ball_hits_wall_and_stops():
    world = World()
    ball = EntityBuilder().ball(x=100, y=100).velocity(dx=100, dy=0).build()
    wall = EntityBuilder().wall(x=200, y=100, width=20, height=20).build()

    world.add_entity(ball)
    world.add_entity(wall)

    from minigolf.systems.physics import PhysicsSpace

    physics = PhysicsSpace(world)
    physics.populate()
    physics.step(1.0)

    assert (pos := ball.get(Position)) is not None
    assert pos.x < 200


def test_builder_clears_between_builds():
    world = World()
    s = EntityBuilder()

    world.add_entity(s.ball(x=0, y=0).velocity(dx=5, dy=0).build())
    hole_entity = s.hole(x=100, y=100).build()
    world.add_entity(hole_entity)

    assert hole_entity.get(Velocity) is None
    assert hole_entity.get(PhysicsBody) is None
    assert (rend := hole_entity.get(Renderable)) is not None
    assert rend.colour == (91, 166, 0)


def test_shape_matches_between_components():
    e = EntityBuilder().ball(x=0, y=0).build()

    assert (collider := e.get(Collider)) is not None
    assert (renderable := e.get(Renderable)) is not None

    assert collider.shape == renderable.shape


def test_custom_ball_colour():
    e = EntityBuilder().ball(x=0, y=0).colour((123, 45, 67)).build()
    assert (rend := e.get(Renderable)) is not None
    assert rend.colour == (123, 45, 67)
