from collections import defaultdict
from typing import TypeVar, cast

T = TypeVar("T")


class World:
    def __init__(self):
        self._next_id = 0
        self.entities: set[int] = set()
        self.components: defaultdict[type, dict[int, object]] = defaultdict(dict)

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self.entities.add(eid)
        return eid

    def get(self, component_type: type[T], eid: int) -> T | None:
        return cast(T | None, self.components[component_type].get(eid))

    def all_with(self, *types: type) -> list[int]:
        return [
            eid
            for eid in self.entities
            if all(eid in self.components[t] for t in types)
        ]
