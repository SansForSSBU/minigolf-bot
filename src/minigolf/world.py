import json
from collections import defaultdict
from typing import Any, TypeVar, cast

from pydantic import BaseModel

from minigolf import components

T = TypeVar("T", bound=BaseModel)


class World:
    def __init__(self):
        self._next_id: int = 0
        self.entities: set[int] = set()
        self.components: defaultdict[type[BaseModel], dict[int, BaseModel]] = (
            defaultdict(dict)
        )

    def create_entity(self) -> int:
        eid: int = self._next_id
        self._next_id += 1
        self.entities.add(eid)
        return eid

    def get(self, component_type: type[T], eid: int) -> T | None:
        return cast(T | None, self.components[component_type].get(eid))

    def all_with(self, *types: type[BaseModel]) -> list[int]:
        return [
            eid
            for eid in self.entities
            if all(eid in self.components[t] for t in types)
        ]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "entities": list(self.entities),
            "components": {
                comp_type.__name__: {
                    str(eid): comp.model_dump() for eid, comp in comps.items()
                }
                for comp_type, comps in self.components.items()
            },
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
        world.entities = set(map(int, data["entities"]))

        # Build a component registry dynamically
        component_classes: dict[str, type[BaseModel]] = {
            name: obj
            for name, obj in vars(components).items()
            if isinstance(obj, type) and issubclass(obj, BaseModel)
        }

        for comp_name, eid_map in data["components"].items():
            comp_cls = component_classes.get(comp_name)
            if not comp_cls:
                raise ValueError(f"Unknown component type: {comp_name}")
            for eid_str, comp_data in eid_map.items():
                eid = int(eid_str)
                world.components[comp_cls][eid] = comp_cls(**comp_data)

        return world
