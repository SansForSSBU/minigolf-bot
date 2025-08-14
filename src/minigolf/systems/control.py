from pymunk import Vec2d
from minigolf.systems.agents.DefaultMovesAgent import DefaultMovesAgent

STOPPING_VELOCITY = 10.0
AGENT = DefaultMovesAgent()


class ControlSystem:
    def __init__(self, ball, agent=None):
        self.agent = AGENT
        self.ball = ball

    def step(self):
        if self.ball.body.velocity.length < STOPPING_VELOCITY:
            self.stop_ball()
            next_move = AGENT.make_move()
            if next_move is not None:
                self.ball.body.velocity = next_move[0]
                self.ball.body.angular_velocity = next_move[1]

    def stop_ball(self):
        self.ball.body.velocity = Vec2d(0.0, 0.0)
