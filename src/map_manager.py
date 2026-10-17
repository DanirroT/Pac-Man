
from src import (CoordinatesFloat, PMArgs, MazeGenerator, Coordinates,
                 Directions)
from typing import NamedTuple
from enum import Enum
import random


class Player():

    pos: CoordinatesFloat
    dir: Directions
    lives: int

    invincibility: bool = False
    wall_phase: bool = False
    extra_speed: bool = False

    dir_queue: Directions | None = None

    def __init__(self, pos: Coordinates, lives: int,
                 dir: Directions = Directions.RIGHT
                 ) -> None:
        self.pos = CoordinatesFloat(*pos)
        self.dir = dir
        self.lives = lives

    def handle_input(self, input_dir: Directions) -> None:
        if (self.dir == Directions.UP and input_dir == Directions.DOWN or
            self.dir == Directions.DOWN and input_dir == Directions.UP or
            self.dir == Directions.LEFT and input_dir == Directions.RIGHT or
                self.dir == Directions.RIGHT and input_dir == Directions.LEFT):
            self.dir = input_dir
            return

        if self.dir == input_dir:
            self.dir = input_dir
            return
        if self.dir_queue == input_dir:
            return
        self.dir_queue = input_dir

    def change_dir(self, possible: list[Directions]) -> bool:
        if self.dir_queue in possible:
            self.dir = self.dir_queue
            self.dir_queue = None
            return True
        elif self.dir in possible:
            return True
        else:
            self.dir_queue = None
            return False

    def move(self, movement: float) -> None:
        self.pos = CoordinatesFloat(
            self.pos.x + (movement if "r" in self.dir.value else 0)
            - (movement if "l" in self.dir.value else 0),
            self.pos.y + (movement if "d" in self.dir.value else 0)
            - (movement if "u" in self.dir.value else 0)
        )


class Ghost():

    pos: CoordinatesFloat
    dir: Directions
    color: tuple[int, int, int]
    # ai: DecisionAlgorithm

    def __init__(self, color: tuple[int, int, int], pos: Coordinates,
                 dir: Directions = Directions.RIGHT) -> None:
        self.pos = CoordinatesFloat(*pos)
        self.dir = dir
        self.color = color

    def change_dir(self, dir: Directions) -> None:
        self.dir = dir

    def move(self, movement: float) -> None:
        self.pos = CoordinatesFloat(
            self.pos.x + (movement if "r" in self.dir.value else 0)
            - (movement if "l" in self.dir.value else 0),
            self.pos.y + (movement if "d" in self.dir.value else 0)
            - (movement if "u" in self.dir.value else 0)
        )


class CellState(Enum):

    FORK = 1
    DEADEND = 3
    BLOCKED = 4

    CORRIDOR = 2
    CORNER = 5


class Walls(NamedTuple):
    up: bool
    right: bool
    down: bool
    left: bool


class Cell:
    loc: Coordinates
    y: int
    walls: Walls
    # starting_objects: list[StartingObjects]
    state: CellState

    def __init__(self, loc: Coordinates, value: int):
        self.loc = loc
        self.walls = Walls(
            bool(value & 1),  # left wall
            bool(value & 2),  # bottom wall
            bool(value & 4),  # right wall
            bool(value & 8),  # top wall
        )
        wall_count = sum(self.walls)

        if wall_count == 4:
            self.state = CellState.BLOCKED
        elif wall_count == 3:
            self.state = CellState.DEADEND

        elif wall_count == 2:
            if ((self.walls.up and self.walls.down) or
                    (self.walls.left and self.walls.right)):
                self.state = CellState.CORRIDOR
            else:
                self.state = CellState.CORNER
        else:
            self.state = CellState.FORK

        # self.starting_objects = []


class MazeObj:

    maze_int: list[list[int]]
    size: Coordinates

    maze: list[list[Cell]]

    def __init__(self, maze_int: list[list[int]]) -> None:
        self.maze_int = maze_int
        self.size = Coordinates(len(maze_int[0]), len(maze_int))

        self.maze = []
        for y, row in enumerate(maze_int):
            self.maze.append([])
            for x, value in enumerate(row):
                self.maze[y].append(Cell(Coordinates(x, y), value))

    def __str__(self) -> str:
        return "\n".join("".join(str(cell.state.value) for cell in row)
                         for row in self.maze)


class Maze:

    args: PMArgs

    player: Player

    ghosts: list[Ghost]

    supergum: list[Coordinates]
    pacgum: list[Coordinates]

    maze: MazeObj
    current_map: int

    def __init__(self, args: PMArgs) -> None:

        self.args = args
        self.current_map = -1

    def load_pre_set(self) -> None:

        map_generator = MazeGenerator(Coordinates(1, 1))
        map_int = map_generator.use_preset_maze()
        self.maze = MazeObj(map_int)
        self.setup_map()

    def load_next_map(self) -> None:

        self.current_map += 1

        map_generator = MazeGenerator(self.args.levels[self.current_map],
                                      self.args.seed)
        map_int = map_generator.generate_maze()
        self.maze = MazeObj(map_int)

        self.setup_map()

    def get_wall_less(self) -> None:
        for row in self.maze.maze:
            for cell in row:
                cell.walls = Walls(False, False, False, False)
                cell.state = CellState.FORK

        for cell in self.maze.maze[0]:
            cell.walls = Walls(True, False, False, False)
            cell.state = CellState.CORRIDOR

        for cell in self.maze.maze[-1]:
            cell.walls = Walls(True, False, False, False)
            cell.state = CellState.CORRIDOR

        for line in self.maze.maze:
            for cell in line:
                cell.walls = Walls(True, False, False, False)
                cell.state = CellState.CORRIDOR

        self.maze.maze[0][0].walls = Walls(True, False, False, True)
        self.maze.maze[0][-1].walls = Walls(True, True, False, False)
        self.maze.maze[-1][0].walls = Walls(False, False, True, True)
        self.maze.maze[-1][-1].walls = Walls(False, True, True, False)

    def setup_map(self) -> None:

        self.ghosts = [
            Ghost((255, 0, 0), Coordinates(0, 0), Directions.RIGHT),
            Ghost((255, 184, 255), Coordinates(0, self.maze.size.y-1),
                  Directions.DOWN),
            Ghost((0, 255, 255), Coordinates(self.maze.size.x-1, 0),
                  Directions.LEFT),
            Ghost((255, 184, 81), Coordinates(
                self.maze.size.x-1, self.maze.size.y-1), Directions.UP)
        ]

        self.supergum = [
            Coordinates(0, 0), Coordinates(self.maze.size.x-1, 0),
            Coordinates(0, self.maze.size.y-1),
            Coordinates(self.maze.size.x-1, self.maze.size.y-1)
        ]

        player_original = (self.maze.size.x // 2, self.maze.size.y // 2)
        player_position = player_original
        change_list = [(1, 0), (0, 1), (-1, 0), (0, -1),
                       (1, 1), (-1, 1), (-1, -1), (1, -1)]

        while True:
            if (self.maze.maze[player_position[1]][player_position[0]].state
                    == CellState.BLOCKED):
                change = change_list.pop(0)
                player_position = (player_original[0] + change[0],
                                   player_original[1] + change[1])
                continue
            else:
                self.player = Player(
                    Coordinates(player_position[0], player_position[1]),
                    self.args.lives)
                break

        n_pacgums: int = self.args.pacgum
        self.pacgum = []
        random.seed(self.args.seed)

        while n_pacgums:
            attempt = Coordinates(random.randint(0, self.maze.size[0] - 1),
                                  random.randint(0, self.maze.size[1] - 1))
            # print(attempt)
            if ((attempt.x == 0 or attempt.x == self.maze.size[0] - 1) and
                    (attempt.y == 0 or attempt.y == self.maze.size[1] - 1)):
                continue
            if self.maze.maze[attempt.y][attempt.x].state == CellState.BLOCKED:
                continue
            if (attempt in self.pacgum or
                Coordinates(int(self.player.pos.x),
                            int(self.player.pos.y)) == attempt):
                continue
            self.pacgum.append(attempt)
            n_pacgums -= 1
