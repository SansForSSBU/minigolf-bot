from minigolf.world import World
from minigolf.components import Velocity, PhysicsBody


def physics_system(world: World) -> None:
    for _ in world.all_with(Velocity, PhysicsBody):
        # TODO: Implement actual physics logic
        # vel = world.get(Velocity, eid)
        # body = world.get(PhysicsBody, eid)
        return
