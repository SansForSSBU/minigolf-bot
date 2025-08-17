from functools import cache

import networkx as nx
import numpy as np
from pymunk import ShapeFilter, Vec2d

from minigolf.components import Name, Position

NO_FILTER = ShapeFilter()
WALL = 1
GRID_SIZE = 1000
# Generate a set of sensible shots:
# directions every 15 degrees
# speeds from 100 to 600 in steps of 100
# spin 0 only
POSSIBLE_SHOTS = [
    [Vec2d(speed * np.cos(theta), speed * np.sin(theta)), 0.0]
    for speed in [20, 30] + list(range(100, 700, 100))
    for theta in np.linspace(0, 2 * np.pi, 24, endpoint=False)
]


class BruteForceAgent:
    def __init__(self, world, ball, physics_system):
        self.world = world
        self.ball = ball
        self.physics_system = physics_system
        self._costs = None

    def get_map_grid(self):
        # TODO: Speed up by assuming empty and iterating over collider boxes to fill in
        def is_wall(point):
            results = self.physics_system.space.point_query(point, 1, NO_FILTER)
            for res in results:
                if res and res.shape:
                    entity = res.shape.entity
                    if entity.get(Name).name == "wall":
                        return WALL
            return 0

        points = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        occupancy_flat = list(map(is_wall, points))
        return np.array(occupancy_flat, dtype=np.uint8).reshape((GRID_SIZE, GRID_SIZE))

    @cache
    def pathfind(self):
        wall_pixels = self.get_map_grid()
        holes = self.world.get_holes()
        if len(holes) != 1:
            raise ValueError("World should have exactly one hole")
        hole = holes[0]
        hole_pos = (int(hole.get(Position).x), int(hole.get(Position).y))
        G = nx.grid_2d_graph(*wall_pixels.shape)
        for r, c in np.argwhere(wall_pixels == 1):
            G.remove_node((r, c))
        dict_costs = nx.single_source_shortest_path_length(G, hole_pos)
        # TODO: Make nx return it as np array to avoid this annoying conversion
        costs = np.full(wall_pixels.shape, np.inf)
        for (x, y), cost in dict_costs.items():
            costs[x, y] = cost
        return costs

    def cost_fn(self, pos):
        costs = self.pathfind()
        x, y = int(pos[0]), int(pos[1])
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return costs[x, y]
        else:
            return np.inf

    def get_end_pos(self, shot):
        import copy

        # Deep copy the world and physics system to avoid affecting the real game
        world_copy = copy.deepcopy(self.world)
        physics_copy = copy.deepcopy(self.physics_system)
        # Find the ball in the copied world/physics
        balls = world_copy.get_balls()
        if not balls:
            return np.inf  # No ball found
        ball_entity = balls[0]
        pymunk_ball = physics_copy.eid_to_body[ball_entity.id]
        # Set ball velocity for this shot
        pymunk_ball.body.velocity = shot[0]
        pymunk_ball.body.angular_velocity = shot[1]
        # Simulate until stop or max steps
        MAX_STEPS = 1000000
        STOPPING_VELOCITY = 10.0
        for _ in range(MAX_STEPS):
            physics_copy.step()
            if pymunk_ball.body.velocity.length < STOPPING_VELOCITY:
                break
        pos = pymunk_ball.body.position
        end_pos = (pos.x, pos.y)
        return end_pos

    def print_calc_progress(self, idx, length):
        print(f"Calculating... {100 * (idx / length)}%")

    def make_move(self):
        best_shot = None
        best_cost = np.inf
        for idx, shot in enumerate(POSSIBLE_SHOTS):
            self.print_calc_progress(idx, len(POSSIBLE_SHOTS))
            end_pos = self.get_end_pos(shot)
            print(end_pos)
            cost = self.cost_fn(end_pos)
            if cost < best_cost:
                best_cost = cost
                best_shot = shot
        return best_shot
