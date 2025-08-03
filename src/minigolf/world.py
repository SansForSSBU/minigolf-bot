import json
from typing import Any, TypeVar

from pydantic import BaseModel

from minigolf import components
from minigolf.entity import Entity

T = TypeVar("T", bound=BaseModel)


class World:
    def __init__(self):
        self._next_id: int = 0
        self.entities: dict[int, Entity] = {}

    def create_entity(self) -> Entity:
        eid: int = self._next_id
        self._next_id += 1
        entity = Entity(eid, self)
        self.entities[eid] = entity
        return entity

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

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_json_dict(), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "World":
        with open(path) as f:
            data = json.load(f)
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
            entity = Entity(eid, world)
            world.entities[eid] = entity

        for comp_name, eid_map in data["components"].items():
            comp_cls = component_classes.get(comp_name)
            if not comp_cls:
                raise ValueError(f"Unknown component type: {comp_name}")
            for eid_str, comp_data in eid_map.items():
                eid = int(eid_str)
                component = comp_cls(**comp_data)
                world.entities[eid].add(component)

        return world
