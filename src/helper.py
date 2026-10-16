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
