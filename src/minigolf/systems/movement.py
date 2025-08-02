from minigolf.world import World
from minigolf.components import Position, Velocity


def movement_system(world: World) -> None:
    for eid in world.all_with(Position, Velocity):
        pos = world.get(Position, eid)
        vel = world.get(Velocity, eid)
        pos.x += vel.dx
        pos.y += vel.dy
