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

    # Snap click to grid cell, then use the cell centre
    gx, gy = snap_to_grid(x, y)
    cx, cy = gx + TILE_SIZE // 2, gy + TILE_SIZE // 2

    match tool:
        case Tool.WALL:
            # Walls align with grid cells (top-left origin)
            return builder.wall(gx, gy, TILE_SIZE, TILE_SIZE).build()
        case Tool.BALL:
            e = builder.ball(0, 0).build()
        case Tool.HOLE:
            e = builder.hole(0, 0).build()
        case _:
            return None

    pos = e.get(components.Position)
    if pos is None:
        raise RuntimeError("Entity has no Position component")

    pos.x, pos.y = cx, cy
    return e
