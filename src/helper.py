from enum import Enum
from typing import NamedTuple


class Coordinates(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"


class CoordinatesFloat(NamedTuple):
    x: float
    y: float

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"


class Directions(Enum):
    UP = "u"
    RIGHT = "r"
    DOWN = "d"
    LEFT = "l"


class Screens(Enum):
    START = 1
    GAME = 2
    WIN = 3
    LOSE = 4


class CloseProgram(Exception):
    pass


# class MapColors(Enum):
#     WALL = (0, 0, 0)


class SqPOI(Enum):
    T = "t"
    R = "r"
    B = "b"
    L = "l"

    TR = "tr"
    BR = "br"
    BL = "bl"
    TL = "tl"

    C = "c"
