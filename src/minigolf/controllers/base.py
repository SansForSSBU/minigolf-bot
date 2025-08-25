from typing import Protocol

from minigolf.components import Action
from minigolf.observation import Observation


class Controller(Protocol):
    def act(self, obs: Observation, player_id: int) -> Action | None: ...
