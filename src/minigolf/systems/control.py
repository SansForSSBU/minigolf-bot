from pymunk import Vec2d

moves = list(
    reversed(
        [
            [Vec2d(300.0, 0.0), 10000.0],
            [Vec2d(0.0, -300.0), 10000.0],
            [Vec2d(-300.0, 0.0), 10000.0],
            [Vec2d(-15.0, 500.0), 10000.0],
        ]
    )
)

STOPPING_VELOCITY = 10.0


def control_system(world, physics_system):
    balls = world.get_balls()
    if len(balls) != 1:
        raise ValueError("Level has too many balls")
    ball = balls[0]
    pymunk_ball = physics_system.eid_to_body[ball.id]
    if pymunk_ball.body.velocity.length < STOPPING_VELOCITY:
        stop_ball(pymunk_ball)
        try:
            next_move = moves.pop()
            pymunk_ball.body.velocity = next_move[0]
            pymunk_ball.body.angular_velocity = next_move[1]
        except IndexError:
            print("No moves left")


def stop_ball(pymunk_ball):
    pymunk_ball.body.velocity = Vec2d(0.0, 0.0)
