import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from minigolf import components
from minigolf.entity import Entity, PhysicsBody
from minigolf.game.state import GameState

T = TypeVar("T", bound=BaseModel)


class World:
    def __init__(self):
        self._next_id: int = 0
        self.entities: dict[int, Entity] = {}
        self.game_state: GameState = GameState.PLAYING

    def add_entity(self, entity: Entity) -> int:
        """
        Add an entity to the world and return its ID.
        """
        eid = self._next_id
        self._next_id += 1
        entity.id = eid
        self.entities[eid] = entity
        return eid

    def create_entity(self) -> Entity:
        eid: int = self._next_id
        self._next_id += 1
        entity = Entity()
        self.entities[eid] = entity
        return entity

    def remove_entity(self, eid: int) -> None:
        """
        Remove an entity by its ID.
        """
        if eid in self.entities:
            del self.entities[eid]
        else:
            raise KeyError(f"Entity with ID {eid} does not exist.")

    def get_balls(self):
        # TODO: The ball entity should have some unique tag associated with it
        # TODO: this will work for now
        physics_bodies = self.all_with(components.PhysicsBody)
        return [
            entity for entity in physics_bodies if not entity.get(PhysicsBody).anchored
        ]

    def get_holes(self):
        hole_entities = [
            e
            for e in self.entities.values()
            if e.get(components.Name) and e.get(components.Name).name == "hole"
        ]
        return hole_entities

    def get_entity(self, eid: int) -> Entity:
        return self.entities[eid]

    def all_with(self, *types: type[BaseModel]) -> list[Entity]:
        return [
            e for e in self.entities.values() if all(t in e.components for t in types)
        ]

    def to_json_dict(self) -> dict[str, Any]:
        out: dict[str, dict[str, Any]] = {}

        # Collect all components by type
        for entity in self.entities.values():
            for comp_type, comp in entity.components.items():
                if comp_type.__name__ not in out:
                    out[comp_type.__name__] = {}
                out[comp_type.__name__][str(entity.id)] = comp.model_dump()

        return {
            "entities": list(self.entities.keys()),
            "components": out,
        }

    def to_json(self, path: Path) -> None:
        """
        Save the world to a JSON file.
        """
        data = self.to_json_dict()
        path.write_text(json.dumps(data, indent=4))

    @classmethod
    def from_json(cls, path: Path) -> "World":
        data = json.loads(path.read_text())
        return cls.from_json_dict(data)

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> "World":
        world = cls()

        component_classes: dict[str, type[BaseModel]] = {
            name: obj
            for name, obj in vars(components).items()
            if isinstance(obj, type) and issubclass(obj, BaseModel)
        }

        for eid_str in data["entities"]:
            eid = int(eid_str)
            entity = Entity()
            entity.id = eid
            world.entities[eid] = entity

        for comp_name, eid_map in data["components"].items():
            comp_cls = component_classes.get(comp_name)
            if not comp_cls:
                raise ValueError(f"Unknown component type: {comp_name}")
            for eid_str, comp_data in eid_map.items():
                eid = int(eid_str)
                component = comp_cls(**comp_data)
                world.entities[eid].add(component)

        world._next_id = max(world.entities.keys(), default=-1) + 1

        return world
