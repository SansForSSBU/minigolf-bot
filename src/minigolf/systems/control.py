from pymunk import Vec2d

from minigolf.systems.agents.DefaultMovesAgent import DefaultMovesAgent
from minigolf.systems.agents.BruteForceAgent import BruteForceAgent

agents = {"default": DefaultMovesAgent, "brute_force": BruteForceAgent}

STOPPING_VELOCITY = 10.0
AGENT = agents["brute_force"]


class ControlSystem:
    def __init__(self, ball, world, physics_system):
        self.agent = AGENT(world, ball, physics_system)
        self.physics_system = physics_system
        self.world = world
        self.ball = ball

    def step(self):
        if self.ball.body.velocity.length < STOPPING_VELOCITY:
            self.stop_ball()
            next_move = self.agent.make_move()
            if next_move is not None:
                self.ball.body.velocity = next_move[0]
                self.ball.body.angular_velocity = next_move[1]

    def stop_ball(self):
        self.ball.body.velocity = Vec2d(0.0, 0.0)
