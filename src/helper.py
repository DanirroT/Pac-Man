from enum import Enum
from typing import NamedTuple
# from abc import ABC, abstractmethod


class CloseProgram(Exception):
    pass


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


class Overlays(Enum):
    PAUSE = "p"
    WIN = "w"
    LOSE = "l"
    STARTING = "s"


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
    SCORING = 5


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


# class MazeElement(ABC):
#     """
#     Abstract class for all objects that can be drawn on the maze.
#     """

#     pos: Coordinates | CoordinatesFloat

#     def __init__(self, pos: CoordinatesFloat) -> None:
#         self.pos = pos

#     @abstractmethod
#     def draw(self) -> None:
#         pass
