import random

from minigolf.components import Action
from minigolf.controllers import Controller
from minigolf.world import World


class RandomController(Controller):
    """Chooses a random strike each time it's called."""

    def __init__(self, max_force: float = 400.0):
        self.max_force = max_force

    def act(self, world: World, player_id: int) -> Action | None:
        vx = random.uniform(-self.max_force, self.max_force)
        vy = random.uniform(-self.max_force, self.max_force)
        av = random.uniform(-5000.0, 5000.0)
        return Action(type="strike", velocity=(vx, vy), angular_velocity=av)
