import numpy as np
from pymunk import ShapeFilter
from minigolf.components import Name, Position

NO_FILTER = ShapeFilter()
WALL = 1
GRID_SIZE = 1000

class BruteForceAgent:
    def __init__(self, world, ball, physics_system):
        self.world = world
        self.ball = ball
        self.physics_system = physics_system

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
        wall_pixels = self.get_wall_pixels()
        holes = self.world.get_holes()
        # Assume only 1 hole
        hole = holes[0]
        hole_pos = hole.get(Position)
        hole_x, hole_y = int(hole_pos.x), int(hole_pos.y)
        costs = np.full((GRID_SIZE, GRID_SIZE), np.inf)
        # Now Dijkstra
        
        pass

    def make_move(self):
        reward = self.pathfind()
        pass
