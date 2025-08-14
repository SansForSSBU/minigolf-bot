from minigolf.constants import DEFAULT_MOVES


class DefaultMovesAgent:
    def __init__(self, world, ball):
        self.moves = DEFAULT_MOVES.copy()
        self.world = world
        self.ball = ball

    def make_move(self):
        try:
            return self.moves.pop()
        except IndexError:
            return None
