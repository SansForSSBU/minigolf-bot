from minigolf.constants import DEFAULT_MOVES


class DefaultMovesAgent:
    def __init__(self):
        self.moves = DEFAULT_MOVES.copy()

    def make_move(self):
        try:
            return self.moves.pop()
        except IndexError:
            return None
