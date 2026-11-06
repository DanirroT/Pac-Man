from enum import Enum
from typing import NamedTuple
# from abc import ABC, abstractmethod


class CloseProgram(Exception):
    pass


class Coordinates(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f"x: {self.x:02d}, y: {self.y:02d}"


class CoordinatesFloat(NamedTuple):
    x: float
    y: float

    def __str__(self) -> str:
        return f"x: {self.x:02.2f}, y: {self.y:02.2f}"


class Overlays(Enum):
    PAUSE = "p"
    # WIN = "w"
    # LOSE = "l"
    STARTING = "s"

    def __str__(self) -> str:
        return self.value


class Directions(Enum):
    UP = "u"
    RIGHT = "r"
    DOWN = "d"
    LEFT = "l"

    STARTING = "sr"
    NA = "na"

    def __str__(self) -> str:
        return self.value


class Screens(Enum):
    START = "st"
    GAME = "gm"
    WIN = "wn"
    LOSE = "ls"
    SCORING = "sc"

    def __str__(self) -> str:
        return self.value


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

    def __str__(self) -> str:
        return self.value


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

def s_round(n: float) -> int:
    """
    Rounds a float to the nearest integer, with ties rounding away from zero.
    """
    if int(n) - n <= -0.5:
        return int(n) + 1
    elif int(n) - n >= 0.5:
        return int(n) - 1
    else:
        return int(n)
