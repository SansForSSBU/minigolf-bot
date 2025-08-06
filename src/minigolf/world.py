import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from minigolf import components
from minigolf.entity import Entity

T = TypeVar("T", bound=BaseModel)


class World:
    def __init__(self):
        self._next_id: int = 0
        self.entities: dict[int, Entity] = {}

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

    def get_balls(self):
        # TODO: The ball entity should have some unique tag associated with it but this will work for now
        dynamic_bodies = self.all_with(components.PhysicsBody)
        return dynamic_bodies
        pass

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

        # Map shape type names to concrete classes
        from minigolf.components import Rect, Circle  # Add more shapes as needed

        SHAPE_CLASSES = {
            "Rect": Rect,
            "Circle": Circle,
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
                # Special handling for components with a 'shape' field
                if (
                    "shape" in comp_data
                    and isinstance(comp_data["shape"], dict)
                    and "type" in comp_data["shape"]
                ):
                    shape_info = comp_data["shape"].copy()
                    shape_type = shape_info.pop("type")
                    shape_cls = SHAPE_CLASSES.get(shape_type)
                    if not shape_cls:
                        raise ValueError(f"Unknown shape type: {shape_type}")
                    comp_data["shape"] = shape_cls(**shape_info)
                component = comp_cls(**comp_data)
                world.entities[eid].add(component)

        world._next_id = max(world.entities.keys(), default=-1) + 1

        return world
