from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING
from .helper import Coordinates

if TYPE_CHECKING:
    from .map_manager import MazeObj


def _in_bounds(maze: MazeObj, pos: Coordinates) -> bool:
    return 0 <= pos.x < maze.size.x and 0 <= pos.y < maze.size.y


def _is_blocked(maze: MazeObj, pos: Coordinates) -> bool:
    return all(maze.maze[pos.y][pos.x].walls)


def neighbors(maze: MazeObj, pos: Coordinates) -> list[Coordinates]:
    if not _in_bounds(maze, pos):
        raise ValueError(f"position {pos} is outside the maze")

    walls = maze.maze[pos.y][pos.x].walls
    candidates = (
        (walls.up, Coordinates(pos.x, pos.y - 1)),
        (walls.right, Coordinates(pos.x + 1, pos.y)),
        (walls.down, Coordinates(pos.x, pos.y + 1)),
        (walls.left, Coordinates(pos.x - 1, pos.y)),
    )
    result: list[Coordinates] = []
    for has_wall, target in candidates:
        if has_wall:
            continue
        if not _in_bounds(maze, target) or _is_blocked(maze, target):
            continue
        result.append(target)
    return result


def bfs_distances(maze: MazeObj, start: Coordinates) -> dict[Coordinates, int]:
    if not _in_bounds(maze, start):
        raise ValueError(f"position {start} is outside the maze")
    if _is_blocked(maze, start):
        return {}

    distances: dict[Coordinates, int] = {start: 0}
    queue: deque[Coordinates] = deque([start])
    while queue:
        current = queue.popleft()
        for target in neighbors(maze, current):
            if target not in distances:
                distances[target] = distances[current] + 1
                queue.append(target)
    return distances


def nearest_open_cell(maze: MazeObj, start: Coordinates) -> Coordinates:
    if not _in_bounds(maze, start):
        raise ValueError(f"position {start} is outside the maze")

    seen: set[Coordinates] = {start}
    queue: deque[Coordinates] = deque([start])
    while queue:
        current = queue.popleft()
        if not _is_blocked(maze, current):
            return current
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            target = Coordinates(current.x + dx, current.y + dy)
            if _in_bounds(maze, target) and target not in seen:
                seen.add(target)
                queue.append(target)
    raise ValueError("the maze has no open cell")


def unreachable_cells(maze: MazeObj, start: Coordinates) -> list[Coordinates]:
    reachable = bfs_distances(maze, start)
    missing: list[Coordinates] = []
    for row in maze.maze:
        for cell in row:
            if cell.loc in reachable or all(cell.walls):
                continue
            missing.append(cell.loc)
    return missing
