from pymunk import Vec2d

moves = list(
    reversed(
        [
            Vec2d(300.0, 0.0),
            Vec2d(0.0, -300.0),
            Vec2d(-300.0, 0.0),
            Vec2d(0.0, 300.0),
            Vec2d(120.0, 480.0),
        ]
    )
)

STOPPING_VELOCITY = 10.0


def control_system(world, physics_system):
    balls = world.get_balls()
    assert len(balls) == 1
    ball = balls[0]
    pymunk_ball = physics_system.eid_to_body[ball.id]
    if pymunk_ball.velocity.length < STOPPING_VELOCITY:
        stop_ball(pymunk_ball)
        try:
            next_move = moves.pop()
            pymunk_ball.velocity = next_move
        except IndexError:
            print("No moves left")


def stop_ball(pymunk_ball):
    pymunk_ball.velocity = Vec2d(0.0, 0.0)
