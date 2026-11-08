from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING
from .helper import Coordinates, Directions

if TYPE_CHECKING:
    # Imported for type hints only, so there is no circular import at runtime.
    from .map_manager import MazeObj

_STEP_DIRECTIONS: dict[tuple[int, int], Directions] = {
    (0, -1): Directions.UP,
    (1, 0): Directions.RIGHT,
    (0, 1): Directions.DOWN,
    (-1, 0): Directions.LEFT,
}


def neighbors(maze: MazeObj, pos: Coordinates) -> list[Coordinates]:
    walls = maze.maze[pos.y][pos.x].walls
    candidates = (
        (walls.up, Coordinates(pos.x, pos.y - 1)),
        (walls.right, Coordinates(pos.x + 1, pos.y)),
        (walls.down, Coordinates(pos.x, pos.y + 1)),
        (walls.left, Coordinates(pos.x - 1, pos.y)),
    )
    return [cell for wall, cell in candidates if not wall]


def find_path(maze: MazeObj, start: Coordinates,
              goal: Coordinates) -> list[Coordinates]:
    if start == goal:
        return [start]

    came_from: dict[Coordinates, Coordinates | None] = {start: None}
    queue: deque[Coordinates] = deque([start])
    while queue:
        current = queue.popleft()
        for target in neighbors(maze, current):
            if target in came_from:
                continue
            came_from[target] = current
            if target == goal:
                return _rebuild_path(came_from, goal)
            queue.append(target)
    return []


def _rebuild_path(came_from: dict[Coordinates, Coordinates | None],
                  goal: Coordinates) -> list[Coordinates]:
    path: list[Coordinates] = []
    step: Coordinates | None = goal
    while step is not None:
        path.append(step)
        step = came_from[step]
    path.reverse()
    return path


def direction_between(here: Coordinates, there: Coordinates) -> Directions:
    return _STEP_DIRECTIONS.get((there.x - here.x, there.y - here.y),
                                Directions.NA)


def next_direction(maze: MazeObj, start: Coordinates,
                   goal: Coordinates) -> Directions:
    path = find_path(maze, start, goal)
    if len(path) < 2:
        return Directions.NA
    return direction_between(path[0], path[1])
