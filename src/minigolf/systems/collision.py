from dataclasses import dataclass
from minigolf.world import World
from minigolf.components import Position, Collider, Velocity


@dataclass
class CollisionEvent:
    a: int
    b: int


def detect_collisions(world: World) -> list[CollisionEvent]:
    events: list[CollisionEvent] = []
    entities = world.all_with(Position, Collider)

    for i, eid1 in enumerate(entities):
        pos1 = world.get(Position, eid1)
        col1 = world.get(Collider, eid1).shape
        rect1 = col1.to_pygame_shape(pos1)

        for eid2 in entities[i + 1 :]:
            pos2 = world.get(Position, eid2)
            col2 = world.get(Collider, eid2).shape
            rect2 = col2.to_pygame_shape(pos2)

            if rect1.colliderect(rect2):
                events.append(CollisionEvent(a=eid1, b=eid2))
    return events


def resolve_collisions(world: World, events: list[CollisionEvent]) -> None:
    for event in events:
        vel = world.get(Velocity, event.a)
        if vel:
            vel.dx *= -1
            vel.dy *= -1
