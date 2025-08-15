import pymunk

from minigolf.components import Collider
from minigolf.constants import DEFAULT_FLOOR_FRICTION
from minigolf.entity import Entity, PhysicsObject
from minigolf.world import World


class PhysicsSpace:
    def __init__(self, world: World):
        self.world = world
        self.space = pymunk.Space()
        self.space.damping = DEFAULT_FLOOR_FRICTION
        self.eid_to_body = {}

    def populate(self):
        for entity in self.world.entities.values():
            self.add_entity(entity)

    def step(self, timestep=1 / 60, substeps=50):
        for _ in range(substeps):
            self.space.step(timestep / substeps)

        for eid, phys_obj in self.eid_to_body.items():
            entity = self.world.get_entity(eid)
            entity.sync_with_pymunk_body(phys_obj.body)  # access inner pymunk.Body here

    def add_entity(self, entity: Entity) -> None:
        phys_obj = PhysicsObject.from_entity(entity)
        if phys_obj:
            phys_obj.add_to_space(self.space)
            self.eid_to_body[entity.id] = phys_obj

    def remove_entity(self, entity: Entity) -> None:
        phys_obj = self.eid_to_body.pop(entity.id, None)
        if phys_obj:
            self.space.remove(phys_obj.body, phys_obj.shape)
            entity.remove(Collider)
