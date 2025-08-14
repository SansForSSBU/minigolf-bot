class BruteForceAgent:
    def __init__(self, world, ball):
        self.world = world
        self.ball = ball

    def pathfind(self):
        # Generate a reward grid, where positions are judged based on how close they are to the hole.
        # Cache the result and return it whenever recalled.
        pass

    def make_move(self):
        # reward = self.pathfind()
        pass
