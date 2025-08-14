from minigolf.constants import DEFAULT_MOVES


class DefaultMovesAgent:
    def __init__(self, world, ball, physics_system):
        self.world = world
        self.ball = ball
        self.physics_system = physics_system
        self.moves = DEFAULT_MOVES.copy()

    def make_move(self):
        try:
            return self.moves.pop()
        except IndexError:
            return None
