from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from minigolf.components import Shape, Position


def add_tuples(a, b) -> tuple:
    return tuple(x + y for x, y in zip(a, b))


def sub_tuples(a, b) -> tuple:
    return tuple(x - y for x, y in zip(a, b))


def from_pymunk_position(shape: "Shape", pos: tuple[int, int]) -> tuple[int, int]:
    offset = shape.pymunk_offset()
    return sub_tuples(pos, offset)


def to_pymunk_position(shape: "Shape", pos: "Position") -> tuple[int, int]:
    offset = shape.pymunk_offset()
    return add_tuples((pos.x, pos.y), offset)
