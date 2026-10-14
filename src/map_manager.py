from src import MapGenerator
from enum import Enum
from typing import Any
import random


class StartingObjects(Enum):

    PLAYER = 1

    RED_GHOST = 2
    PINK_GHOST = 3
    BLUE_GHOST = 4
    ORANGE_GHOST = 5

    PACGUM = 6
    SUPERGUM = 7


class CellState(Enum):

    FORK = 1
    DEADEND = 3
    BLOCKED = 4

    CORRIDOR = 2
    CORNER = 5


class Cell:
    x: int
    y: int
    walls: tuple[bool, bool, bool, bool]
    starting_objects: list[StartingObjects]
    state: CellState

    def __init__(self, x: int, y: int, value: int):
        self.x = x
        self.y = y
        self.walls = (
            bool(value & 1),  # left wall
            bool(value & 2),  # top wall
            bool(value & 4),  # right wall
            bool(value & 8),  # bottom wall
        )
        wall_count = sum(self.walls)

        if wall_count == 4:
            self.state = CellState.BLOCKED
        elif wall_count == 3:
            self.state = CellState.DEADEND

        elif wall_count == 2:
            if ((self.walls[0] and self.walls[2]) or
                (self.walls[1] and self.walls[3])):
                self.state = CellState.CORRIDOR
            else:
                self.state = CellState.CORNER
        else:
            self.state = CellState.FORK

        self.starting_objects = []


class MazeObj:

    maze_int: list[list[int]]
    size: tuple[int, int]

    maze: list[list[Cell]]

    def __init__(self, maze_int: list[list[int]]):
        self.maze_int = maze_int
        self.size = (len(maze_int[0]), len(maze_int))

        self.maze = []
        for y, row in enumerate(maze_int):
            self.maze.append([])
            for x, value in enumerate(row):
                self.maze[y].append(Cell(x, y, value))


class Maze:

    args: dict[str, Any]

    player: Player

    red_ghost: Ghost
    pink_ghost: Ghost
    blue_ghost: Ghost
    orange_ghost: Ghost

    maze: MazeObj

    def __init__(self, args: dict[str, Any]):

        self.args = args

        map_generator = MapGenerator(args["height"], args["width"], args["seed"])
        map_int = map_generator.get_map()
        self.maze = MazeObj(map_int)

        self.setup_map()

    def setup_map(self):
        self.maze.maze[0][0].starting_objects += [
            StartingObjects.RED_GHOST, StartingObjects.SUPERGUM]
        self.maze.maze[0][self.maze.size[1]-1].starting_objects += [
            StartingObjects.PINK_GHOST, StartingObjects.SUPERGUM]
        self.maze.maze[self.maze.size[0]-1][0].starting_objects += [
            StartingObjects.BLUE_GHOST, StartingObjects.SUPERGUM]
        self.maze.maze[self.maze.size[0]-1][self.maze.size[1]-1].starting_objects += [
            StartingObjects.ORANGE_GHOST, StartingObjects.SUPERGUM]

        player_original = (self.maze.size[0] // 2, self.maze.size[1] // 2)
        player_position = player_original
        change_list = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1)]

        while True:
            if self.maze.maze[player_position[1]][player_position[0]].state == CellState.BLOCKED:
                change = change_list.pop(0)
                player_position = player_original[0] + change[0], player_original[1] + change[1]
                continue
            else:
                self.maze.maze[player_position[1]][player_position[0]].starting_objects.append(StartingObjects.PLAYER)
                break

        n_pacgums: int = self.args["pacgum"]

        while n_pacgums:
            random.seed(self.args["seed"])
            x = random.randint(0, self.maze.size[0] - 1)
            y = random.randint(0, self.maze.size[1] - 1)
            if ((x == 0 or x == self.maze.size[0] - 1) and
                (y == 0 or y == self.maze.size[1] - 1)):
                continue
            if self.maze.maze[y][x].state == CellState.BLOCKED:
                continue
            if (StartingObjects.PACGUM in self.maze.maze[y][x].starting_objects
                or StartingObjects.PLAYER in self.maze.maze[y][x].starting_objects):
                continue
            self.maze.maze[y][x].starting_objects.append(StartingObjects.PACGUM)
            n_pacgums -= 1
