from typing import Any


class Maze:

    player: Player

    red_ghost: Ghost
    pink_ghost: Ghost
    blue_ghost: Ghost
    orange_ghost: Ghost

    maze_int: list[list[int]]
    maze_int: list[list[int]]

    def __init__(self, args: dict[str, Any]):
        self.width = args["width"]
        self.height = args["height"]
