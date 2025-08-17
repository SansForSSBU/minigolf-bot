from typing import Protocol

from minigolf.components import Action
from minigolf.world import World


class Controller(Protocol):
    def act(self, world: World, player_id: int) -> Action | None: ...
