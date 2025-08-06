from pymunk import Vec2d
from minigolf.constants import DEFAULT_MOVES

STOPPING_VELOCITY = 10.0


class ControlSystem:
    def __init__(self, ball, moves=None):
        self.moves = moves if moves is not None else DEFAULT_MOVES
        self.ball = ball

    def step(self):
        if self.ball.body.velocity.length < STOPPING_VELOCITY:
            self.stop_ball()
            try:
                next_move = self.moves.pop()
                self.ball.body.velocity = next_move[0]
                self.ball.body.angular_velocity = next_move[1]
            except IndexError:
                return

    def stop_ball(self):
        self.ball.body.velocity = Vec2d(0.0, 0.0)
