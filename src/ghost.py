from __future__ import annotations
import random
from enum import Enum
from typing import TYPE_CHECKING
from .helper import Coordinates, CoordinatesFloat, Directions, s_round
from .maze_graph import direction_between, find_path

if TYPE_CHECKING:
    from .map_manager import MazeObj, Player

Color = tuple[int, int, int]

FRIGHTENED_TIME = 8.0    
BLINK_TIME = 2.0         
RESPAWN_TIME = 5.0       
AMBUSH_DISTANCE = 4      
SHY_DISTANCE = 8         
WANDER_DISTANCE = 5      
EPSILON = 1e-9

FRIGHTENED_COLOR: Color = (33, 33, 255)
BLINK_COLOR: Color = (255, 255, 255)
EATEN_COLOR: Color = (90, 90, 90)


class GhostState(Enum):


    CHASE = "ch"
    FRIGHTENED = "fr"
    EATEN = "ea"

    def __str__(self) -> str:
        return self.value


class GhostStyle(Enum):


    DIRECT = "direct"
    AMBUSH = "ambush"    
    WANDER = "wander"    
    SHY = "shy"          

    def __str__(self) -> str:
        return self.value


SPEED: dict[GhostState, float] = {
    GhostState.CHASE: 0.85,
    GhostState.FRIGHTENED: 0.5,
    GhostState.EATEN: 2.0,
}

_AHEAD: dict[Directions, tuple[int, int]] = {
    Directions.UP: (0, -1),
    Directions.RIGHT: (1, 0),
    Directions.DOWN: (0, 1),
    Directions.LEFT: (-1, 0),
}


def _distance(a: Coordinates, b: Coordinates) -> int:

    return abs(a.x - b.x) + abs(a.y - b.y)


class Ghost:
    pos: CoordinatesFloat
    cell: Coordinates
    heading_to: Coordinates | None
    starting_pos: Coordinates
    dir: Directions
    map_dimensions: Coordinates
    target: Coordinates | None
    state: GhostState
    style: GhostStyle
    timer: float
    frozen: bool
    base_color: Color

    def __init__(self, color: Color, pos: Coordinates,
                 map_dimensions: Coordinates,
                 dir: Directions = Directions.RIGHT,
                 style: GhostStyle = GhostStyle.DIRECT) -> None:

        self.base_color = color
        self.starting_pos = pos
        self.map_dimensions = map_dimensions
        self.start_dir = dir
        self.style = style
        self.frozen = False
        self._wander: Coordinates | None = None
        self.reset()

    @property
    def color(self) -> Color:

        if self.state == GhostState.EATEN:
            return EATEN_COLOR
        if self.state == GhostState.FRIGHTENED:
            if self.timer < BLINK_TIME and int(self.timer * 4) % 2 == 0:
                return BLINK_COLOR
            return FRIGHTENED_COLOR
        return self.base_color

    def reset(self) -> None:

        self.pos = CoordinatesFloat(*self.starting_pos)
        self.cell = self.starting_pos
        self.heading_to = None
        self.dir = self.start_dir
        self.target = None
        self.state = GhostState.CHASE
        self.timer = 0.0
        self._wander = None

    def change_dir(self, dir: Directions) -> None:

        self.dir = dir

    def frighten(self, duration: float = FRIGHTENED_TIME) -> None:

        if self.state == GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.timer = duration

    def die(self, respawn_time: float = RESPAWN_TIME) -> None:

        self.state = GhostState.EATEN
        self.timer = respawn_time
        self.target = self.starting_pos

    def update(self, maze: MazeObj, player: Player,
               movement: float, dt: float) -> None:
        if self.frozen:
            return
        self._update_timers(dt)
        budget = movement * SPEED[self.state]
        while budget > EPSILON:
            heading = self.heading_to
            if heading is None:
                heading = self._pick_next_cell(maze, player)
            if heading is None:
                break
            budget = self._advance(heading, budget)

    def _update_timers(self, dt: float) -> None:
  
        if self.state == GhostState.CHASE:
            return
        self.timer -= dt
        if self.timer > 0:
            return
        if self.state == GhostState.FRIGHTENED:
            self.state = GhostState.CHASE
        elif (self.heading_to is None and self.cell == self.starting_pos):
            self.state = GhostState.CHASE

    def _advance(self, heading: Coordinates, budget: float) -> float:

        dx = heading.x - self.pos.x
        dy = heading.y - self.pos.y
        remaining = abs(dx) + abs(dy)
        if budget >= remaining:
            self.pos = CoordinatesFloat(*heading)
            self.cell = heading
            self.heading_to = None
            return budget - remaining
        fraction = budget / remaining
        self.pos = CoordinatesFloat(self.pos.x + dx * fraction,
                                    self.pos.y + dy * fraction)
        return 0.0

    def _pick_next_cell(self, maze: MazeObj,
                        player: Player) -> Coordinates | None:

        player_cell = Coordinates(s_round(player.pos.x),
                                  s_round(player.pos.y))
        goals = self._goals(maze, player_cell, player.dir)
        self.target = goals[0]
        for goal in goals:
            path = find_path(maze, self.cell, goal)
            if len(path) >= 2:
                self.target = goal
                self.dir = direction_between(path[0], path[1])
                self.heading_to = path[1]
                return path[1]
        return None

    def _goals(self, maze: MazeObj, player_cell: Coordinates,
               player_dir: Directions) -> list[Coordinates]:

        if self.state == GhostState.EATEN:
            return [self.starting_pos]
        if self.state == GhostState.FRIGHTENED:
            return self._corners_far_from(maze, player_cell)
        gap = _distance(self.cell, player_cell)
        if self.style == GhostStyle.AMBUSH:
            return [self._ahead_of(maze, player_cell, player_dir),
                    player_cell]
        if self.style == GhostStyle.SHY and gap < SHY_DISTANCE:
            return [self.starting_pos, player_cell]
        if self.style == GhostStyle.WANDER and gap > WANDER_DISTANCE:
            return [self._wander_goal(maze), player_cell]
        return [player_cell]

    def _corners_far_from(self, maze: MazeObj,
                          player_cell: Coordinates) -> list[Coordinates]:

        last_x = maze.size.x - 1
        last_y = maze.size.y - 1
        corners = [Coordinates(0, 0), Coordinates(last_x, 0),
                   Coordinates(0, last_y), Coordinates(last_x, last_y)]
        far_first = sorted(corners, reverse=True,
                           key=lambda c: _distance(c, player_cell))
        return [c for c in far_first if c != self.cell]

    @staticmethod
    def _ahead_of(maze: MazeObj, player_cell: Coordinates,
                  player_dir: Directions) -> Coordinates:

        dx, dy = _AHEAD.get(player_dir, (0, 0))
        x = player_cell.x + dx * AMBUSH_DISTANCE
        y = player_cell.y + dy * AMBUSH_DISTANCE
        return Coordinates(min(max(x, 0), maze.size.x - 1),
                           min(max(y, 0), maze.size.y - 1))

    def _wander_goal(self, maze: MazeObj) -> Coordinates:

        if self._wander is None or self._wander == self.cell:
            open_cells = [cell.loc for row in maze.maze for cell in row
                          if not all(cell.walls)]
            self._wander = random.choice(open_cells)
        return self._wander
