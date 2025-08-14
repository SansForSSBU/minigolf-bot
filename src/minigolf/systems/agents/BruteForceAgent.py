import numpy as np
from pymunk import ShapeFilter, Vec2d
from minigolf.components import Name, Position

NO_FILTER = ShapeFilter()
WALL = 1
GRID_SIZE = 1000
# Generate a set of sensible shots: directions every 15 degrees, speeds from 100 to 600 in steps of 100, spin 0 only
POSSIBLE_SHOTS = [
    [Vec2d(speed * np.cos(theta), speed * np.sin(theta)), 0.0]
    for speed in range(100, 700, 100)
    for theta in np.linspace(0, 2 * np.pi, 24, endpoint=False)
]


class BruteForceAgent:
    def __init__(self, world, ball, physics_system):
        self.world = world
        self.ball = ball
        self.physics_system = physics_system
        self._costs = None

    def get_wall_pixels(self):
        # Create a 1000x1000 grid to store occupancy (1 if occupied, 0 if free)
        occupancy = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                point = (x, y)
                results = self.physics_system.space.point_query(point, 0, NO_FILTER)
                for res in results:
                    if res and res.shape:
                        entity = res.shape.entity
                        if entity.get(Name).name == "wall":
                            occupancy[x, y] = WALL
        return occupancy

    def pathfind(self):
        if self._costs is not None:
            return self._costs
        wall_pixels = self.get_wall_pixels()
        holes = self.world.get_holes()
        # Assume only 1 hole
        hole = holes[0]
        hole_pos = hole.get(Position)
        hole_x, hole_y = int(hole_pos.x), int(hole_pos.y)
        costs = np.full((GRID_SIZE, GRID_SIZE), np.inf)
        visited = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
        from heapq import heappush, heappop

        heap = []
        # Dijkstra: start from hole, cost 0
        costs[hole_x, hole_y] = 0
        heappush(heap, (0, hole_x, hole_y))
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while heap:
            cost, x, y = heappop(heap)
            if visited[x, y]:
                continue
            visited[x, y] = True
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if wall_pixels[nx, ny] == WALL:
                        continue  # impassible
                    new_cost = cost + 1
                    if new_cost < costs[nx, ny]:
                        costs[nx, ny] = new_cost
                        heappush(heap, (new_cost, nx, ny))
        self._costs = costs
        return costs

    def get_cost(self, shot):
        cost = self.pathfind()
        # Simulate the shot and get the cost.
        return 1

    def make_move(self):
        best_shot = None
        best_cost = np.inf
        for shot in POSSIBLE_SHOTS:
            cost = self.get_cost(shot)
            if cost < best_cost:
                best_cost = cost
                best_shot = shot
        return best_shot
