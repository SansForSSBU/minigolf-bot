from minigolf import components
from minigolf.entity import Entity
from minigolf.objects import EntityBuilder
from minigolf.world import World
from minigolf.editor.consts import Tool

TILE_SIZE = 50


def snap_to_grid(x: int, y: int) -> tuple[int, int]:
    return (x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE


def get_entity_at(world: World, x: int, y: int) -> Entity | None:
    gx, gy = snap_to_grid(x, y)

    for entity in world.entities.values():
        pos = entity.get(components.Position)
        if not pos:
            continue
        ex, ey = snap_to_grid(pos.x, pos.y)
        if (gx, gy) == (ex, ey):
            return entity
    return None


def build_entity(tool: Tool, x: int, y: int) -> Entity | None:
    builder = EntityBuilder()
    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2

    if tool == Tool.WALL:
        return builder.wall(x, y, TILE_SIZE, TILE_SIZE).build()
    elif tool == Tool.BALL:
        # subtract radius (assuming 20x20)
        return builder.ball(cx - 10, cy - 10).build()
    elif tool == Tool.HOLE:
        return builder.hole(cx - 10, cy - 10).build()
    return None
