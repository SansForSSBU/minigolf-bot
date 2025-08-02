from minigolf.components import Velocity, Position, Collider
import pymunk


class PhysicsSpace:
    def __init__(self, world):
        self.world = world
        self.space = pymunk.Space(world)
        self.eid_to_body = {}

    def populate(self):
        for eid in self.world.all_with(Position, Collider):
            col = self.world.get(Collider, eid)
            pos = self.world.get(Position, eid)
            vel = self.world.get(Velocity, eid)
            if vel:
                body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
                body.mass = 10
                body.moment = 1
                body.velocity = (100, -70)
            else:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (pos.x, pos.y)
            width = col.shape.width
            height = col.shape.height
            shape = pymunk.Poly.create_box(body, (width, height))
            self.space.add(body, shape)
            self.eid_to_body[eid] = body  # Store mapping

        pass

    # Steps the simulation. All positions are updated automatically.
    def step(self, timestep=1 / 60):
        self.space.step(timestep)
        # Sync Pymunk body positions back to ECS
        for eid, body in self.eid_to_body.items():
            pos = self.world.get(Position, eid)
            if pos:
                pos.x, pos.y = body.position

    def add_object(self, eid):
        raise NotImplementedError
