from minigolf.components import Position, Collider, Entity
import pymunk


class PhysicsSpace:
    def __init__(self, world):
        self.world = world
        self.space = pymunk.Space(world)
        self.eid_to_body = {}

    def populate(self):
        for eid in self.world.all_with(Position, Collider):
            entity = self.world.get_entity(eid)
            body, shape = entity.to_pymunk()
            self.space.add(body, shape)
            self.eid_to_body[eid] = body  # Store mapping

    def step(self, timestep=1 / 60, substeps=50):
        for _ in range(substeps):
            self.space.step(timestep / substeps)
        # Sync Pymunk body positions back to ECS
        for eid, body in self.eid_to_body.items():
            pos = self.world.get(Position, eid)
            col = self.world.get(Collider, eid)
            width = col.shape.width
            height = col.shape.height
            if pos:
                bx, by = body.position
                pos.x, pos.y = bx - (width / 2), by - (height / 2)

    def add_object(self, entity: Entity):
        raise NotImplementedError
