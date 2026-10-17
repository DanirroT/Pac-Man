
from src import (CoordinatesFloat, PMArgs, MazeGenerator, Coordinates,
                 Directions)
from typing import NamedTuple
from enum import Enum
import random


class Player():

    pos: CoordinatesFloat
    starting_pos: Coordinates
    dir: Directions
    lives: int

    supergum_power: bool = False
    invincibility: bool = False
    wall_phase: bool = False
    extra_speed: bool = False

    map_dimensions: Coordinates
    dir_queue: Directions | None = None

    def __init__(self, pos: Coordinates, lives: int,
                 map_dimensions: Coordinates,
                 dir: Directions = Directions.RIGHT
                 ) -> None:
        self.pos = CoordinatesFloat(*pos)
        self.starting_pos = pos
        self.dir = dir
        self.lives = lives
        self.map_dimensions = map_dimensions

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
        if self.pos.x < 0:
            self.pos = CoordinatesFloat(0, self.pos.y)
        if self.pos.y < 0:
            self.pos = CoordinatesFloat(self.pos.x, 0)
        if self.pos.x >= self.map_dimensions.x:
            self.pos = CoordinatesFloat(self.map_dimensions.x - 1, self.pos.y)
        if self.pos.y >= self.map_dimensions.y:
            self.pos = CoordinatesFloat(self.pos.x, self.map_dimensions.y - 1)

    def reset(self) -> None:
        self.pos = CoordinatesFloat(*self.starting_pos)
        self.dir = Directions.RIGHT
        self.supergum_power = False
        self.invincibility = False
        self.wall_phase = False
        self.extra_speed = False


class Ghost():

    pos: CoordinatesFloat
    starting_pos: Coordinates
    dir: Directions
    color: tuple[int, int, int]
    # ai: DecisionAlgorithm
    map_dimensions: Coordinates
    target: Coordinates | None = None

    def __init__(self, color: tuple[int, int, int], pos: Coordinates,
                 map_dimensions: Coordinates,
                 dir: Directions = Directions.RIGHT) -> None:
        self.pos = CoordinatesFloat(*pos)
        self.starting_pos = pos
        self.dir = dir
        self.color = color
        self.map_dimensions = map_dimensions

    def change_dir(self, dir: Directions) -> None:
        self.dir = dir

    def move(self, movement: float) -> None:
        self.pos = CoordinatesFloat(
            self.pos.x + (movement if "r" in self.dir.value else 0)
            - (movement if "l" in self.dir.value else 0),
            self.pos.y + (movement if "d" in self.dir.value else 0)
            - (movement if "u" in self.dir.value else 0)
        )
        if self.pos.x < 0:
            self.pos = CoordinatesFloat(0, self.pos.y)
        if self.pos.y < 0:
            self.pos = CoordinatesFloat(self.pos.x, 0)
        if self.pos.x >= self.map_dimensions.x:
            self.pos = CoordinatesFloat(self.map_dimensions.x - 1, self.pos.y)
        if self.pos.y >= self.map_dimensions.y:
            self.pos = CoordinatesFloat(self.pos.x, self.map_dimensions.y - 1)

    def die(self) -> None:
        self.target = self.starting_pos

    # def draw(self) -> None:
    #     pass


# class PacGum(MazeElement):

#     pos: Coordinates
#     color: tuple[int, int, int] = (255, 184, 174)

#     def __init__(self, pos: Coordinates) -> None:
#         self.pos = pos  # pyright: ignore

#     def draw(self, screen: pygame.Surface) -> None:
#         pygame.draw.circle(screen, self.color,
#                             self.get_sq_poi(self.pos), self.s_obj_size)


# class SuperGum(MazeElement):

#     pos: Coordinates
#     color: tuple[int, int, int] = (255, 184, 174)

#     def __init__(self, pos: Coordinates) -> None:
#         self.pos = pos  # pyright: ignore

#     def draw(self, screen: pygame.Surface) -> None:
#         pygame.draw.circle(screen, self.color,
#                            self.get_sq_poi(self.pos), self.l_obj_size)

#         for gum in self.maze_manager.pacgum:
#         for supergum in self.maze_manager.supergum:

#         for ghost in self.maze_manager.ghosts:
#             pygame.draw.circle(self.screen, ghost.color,
#                                self.get_sq_poi(ghost.pos), self.l_obj_size)
#         pygame.draw.circle(self.screen, (255, 255, 0), self.get_sq_poi(
#             self.maze_manager.player.pos), self.l_obj_size)

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
    score: int

    ghosts: list[Ghost]

    supergum: list[Coordinates]
    pacgum: list[Coordinates]

    maze: MazeObj
    current_map: int

    def __init__(self, args: PMArgs) -> None:

        self.args = args
        self.current_map = -1
        self.score = 0

    def load_pre_set(self) -> None:

        map_generator = MazeGenerator(Coordinates(1, 1))
        map_int = map_generator.use_preset_maze()
        self.maze = MazeObj(map_int)
        self.setup_map()

    def load_next_map(self) -> None:

        if (not len(self.args.levels)):
            if self.current_map:
                self.load_pre_set()
                self.current_map += 1
                return
            else:
                raise IndexError("No more maps available.")

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

        for cell in self.maze.maze[0][1:-1]:
            cell.walls = Walls(True, False, False, False)
            cell.state = CellState.CORRIDOR

        for cell in self.maze.maze[-1][1:-1]:
            cell.walls = Walls(False, False, True, False)
            cell.state = CellState.CORRIDOR

        for line in self.maze.maze[1:-1]:
            line[0].walls = Walls(False, False, False, True)
            line[0].state = CellState.CORRIDOR

            line[-1].walls = Walls(False, True, False, False)
            line[-1].state = CellState.CORRIDOR

        self.maze.maze[0][0].walls = Walls(True, False, False, True)
        self.maze.maze[0][0].state = CellState.CORNER
        self.maze.maze[0][-1].walls = Walls(True, True, False, False)
        self.maze.maze[0][-1].state = CellState.CORNER
        self.maze.maze[-1][0].walls = Walls(False, False, True, True)
        self.maze.maze[-1][0].state = CellState.CORNER
        self.maze.maze[-1][-1].walls = Walls(False, True, True, False)
        self.maze.maze[-1][-1].state = CellState.CORNER

    def setup_map(self) -> None:
        map_dimensions = self.maze.size

        self.ghosts = [
            Ghost((255, 0, 0), Coordinates(0, 0),
                  map_dimensions, Directions.RIGHT),
            Ghost((255, 184, 255), Coordinates(0, map_dimensions.y-1),
                  map_dimensions, Directions.DOWN),
            Ghost((0, 255, 255), Coordinates(map_dimensions.x-1, 0),
                  map_dimensions, Directions.LEFT),
            Ghost((255, 184, 81), Coordinates(
                map_dimensions.x-1, map_dimensions.y-1),
                map_dimensions, Directions.UP)
        ]

        self.supergum = [
            Coordinates(0, 0), Coordinates(map_dimensions.x-1, 0),
            Coordinates(0, map_dimensions.y-1),
            Coordinates(map_dimensions.x-1, map_dimensions.y-1)
        ]

        player_original = (map_dimensions.x // 2, map_dimensions.y // 2)
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
                    self.args.lives, map_dimensions)
                break

        n_pacgums: int = self.args.pacgum
        self.pacgum = []
        random.seed(self.args.seed)
        n_pacgums = max(2, min(
            n_pacgums, (map_dimensions.x * map_dimensions.y) - 25))

        while n_pacgums:
            attempt = Coordinates(random.randint(0, map_dimensions[0] - 1),
                                  random.randint(0, map_dimensions[1] - 1))
            # print(attempt)
            if ((attempt.x == 0 or attempt.x == map_dimensions[0] - 1) and
                    (attempt.y == 0 or attempt.y == map_dimensions[1] - 1)):
                continue
            if self.maze.maze[attempt.y][attempt.x].state == CellState.BLOCKED:
                continue
            if (attempt in self.pacgum or
                Coordinates(int(self.player.pos.x),
                            int(self.player.pos.y)) == attempt):
                continue
            self.pacgum.append(attempt)
            n_pacgums -= 1
