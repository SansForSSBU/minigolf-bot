import pymunk

from minigolf.entity import Entity, PhysicsObject
from minigolf.world import World
from minigolf.constants import DEFAULT_FLOOR_FRICTION


class PhysicsSpace:
    def __init__(self, world: World):
        self.world = world
        self.space = pymunk.Space()
        self.space.damping = DEFAULT_FLOOR_FRICTION
        self.eid_to_body = {}

    def populate(self):
        for entity in self.world.entities.values():
            body: PhysicsObject | None = PhysicsObject.from_entity(entity)
            if body:
                body.add_to_space(self.space)
                self.eid_to_body[entity.id] = body.body

    def step(self, timestep=1 / 60, substeps=50):
        for _ in range(substeps):
            self.space.step(timestep / substeps)

        for eid, body in self.eid_to_body.items():
            entity = self.world.get_entity(eid)
            entity.sync_with_pymunk_body(body)

    def add_entity(self, entity: Entity) -> None:
        raise NotImplementedError

    def rm_entity(self, entity: Entity) -> None:
        raise NotImplementedError
