"""
Ghosts: states, targets and cell-to-cell movement.
States:
    CHASE       walks towards target that depends on ghost type
    FRIGHTENED  edible, runs to corner farthest from pacman
    EATEN       walks back to starting corner then waits to respawn
"""

from __future__ import annotations
import random
from enum import Enum
from typing import TYPE_CHECKING
import pygame
import time

from .helper import Coordinates, CoordinatesFloat, Directions, s_round
from .maze_graph import direction_between, find_path

if TYPE_CHECKING:
    from .map_manager import MazeObj, Player
    from pygame import Surface

Color = tuple[int, int, int]

FRIGHTENED_TIME = 8.0       # seconds ghost stays edible
BLINK_TIME = 2.0            # ghosts blink during final seconds of edible
RESPAWN_TIME = 5.0          # seconds before eaten ghost chases again
AMBUSH_DISTANCE = 4         # cells ahead of pacman that PINK aims
SHY_DISTANCE = 8            # ORANGE backs off when close to distance
WANDER_DISTANCE = 5         # CYAN ghosts chase when pacman is close
EPSILON = 1e-9

FRIGHTENED_COLOR: Color = (33, 33, 255)
BLINK_COLOR: Color = (255, 255, 255)
EATEN_COLOR: Color = (90, 90, 90)


class GhostState(Enum):
    """
    State of ghost:
    - chase mode
    - frightened
    - eaten
    """
    CHASE = "ch"
    FRIGHTENED = "fr"
    EATEN = "ea"

    def __str__(self) -> str:
        return self.value


class GhostStyle(Enum):
    """
    How ghost picks target while chasing:
    - Goes straight for pacman (direct)
    - Aims X cells ahead of pacman (ambush)
    - Roams randomly until pacman close (wander)
    - Chases from far, backs off when close (shy)
    """
    DIRECT = "direct"
    AMBUSH = "ambush"
    WANDER = "wander"
    SHY = "shy"

    def __str__(self) -> str:
        return self.value


# Ghost speed compared to what pacman gets each frame
SPEED: dict[GhostState, float] = {
    GhostState.CHASE: 0.65,
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
    """
    Return manhattan distance between two cells (ignore wall)
    """
    return abs(a.x - b.x) + abs(a.y - b.y)


class Ghost:
    """
    Ghost:
    - where located
    - what doing
    - where heading

    pos: what gets drawn and used for collisions
    cell: last cell centre ghost reached
    heading_to: next cell centre ghost goes

    Ghost is only ever on straight line between two cells
    """

    class GhostSprites():

        alive: dict[Directions, tuple[Surface, Surface]]
        frightened: tuple[tuple[Surface, Surface], tuple[Surface, Surface]]
        eyes: dict[Directions, Surface]

        def __init__(self) -> None:

            self.alive = {}
            self.eyes = {}

            self.alive[Directions.UP] = (
                pygame.image.load("images/Ghosts/GhostU1.png").convert_alpha(),
                pygame.image.load("images/Ghosts/GhostU2.png").convert_alpha())

            self.alive[Directions.RIGHT] = (
                pygame.image.load("images/Ghosts/GhostR1.png").convert_alpha(),
                pygame.image.load("images/Ghosts/GhostR2.png").convert_alpha())

            self.alive[Directions.DOWN] = (
                pygame.image.load("images/Ghosts/GhostD1.png").convert_alpha(),
                pygame.image.load("images/Ghosts/GhostD2.png").convert_alpha())

            self.alive[Directions.LEFT] = (
                pygame.image.load("images/Ghosts/GhostL1.png").convert_alpha(),
                pygame.image.load("images/Ghosts/GhostL2.png").convert_alpha())

            self.frightened = ((
                pygame.image.load(
                    "images/Ghosts/GhostFrightenedB1.png").convert_alpha(),
                pygame.image.load(
                    "images/Ghosts/GhostFrightenedB2.png").convert_alpha()),
                    (pygame.image.load(
                        "images/Ghosts/GhostFrightenedW1.png").convert_alpha(),
                     pygame.image.load("images/Ghosts/GhostFrightenedW2.png"
                                       ).convert_alpha()))

            self.eyes[Directions.UP] = (
                pygame.image.load("images/Ghosts/GhostEyesU.png"
                                  ).convert_alpha())
            self.eyes[Directions.RIGHT] = (
                pygame.image.load("images/Ghosts/GhostEyesR.png"
                                  ).convert_alpha())
            self.eyes[Directions.DOWN] = (
                pygame.image.load("images/Ghosts/GhostEyesD.png"
                                  ).convert_alpha())
            self.eyes[Directions.LEFT] = (
                pygame.image.load("images/Ghosts/GhostEyesL.png"
                                  ).convert_alpha())

    starting_pos: Coordinates
    pos: CoordinatesFloat
    cell: Coordinates
    dir: Directions
    map_dimensions: Coordinates

    state: GhostState
    heading_to: Coordinates | None
    target: Coordinates | None
    style: GhostStyle
    timer: float
    frozen: bool

    base_color: Color
    sprites: GhostSprites
    sprite_state: int
    step: float

    def __init__(self, color: Color, pos: Coordinates,
                 map_dimensions: Coordinates,
                 dir: Directions = Directions.RIGHT,
                 style: GhostStyle = GhostStyle.DIRECT) -> None:
        """
        Create a ghost standing on pos (its respawn)
        """
        self.base_color = color
        self.starting_pos = pos
        self.map_dimensions = map_dimensions
        self.start_dir = dir
        self.style = style
        self.frozen = False
        self._wander: Coordinates | None = None
        self.reset()
        self.sprites = self.GhostSprites()
        self.sprites.alive = {dir: self.swap_color(sprites)
                              for dir, sprites in self.sprites.alive.items()}
        self.sprite_state = 1
        self.step = 0.0

    def swap_color(self, surfaces: tuple[Surface, Surface]
                   ) -> tuple[Surface, Surface]:
        """
        Change sprite color when initializing ghost sprites
        """

        if self.base_color == (127, 127, 127):
            return surfaces
        if self.base_color == (255, 255, 255):
            self.base_color = (254, 254, 254)
        img_copy_1 = pygame.Surface(surfaces[0].get_size())
        img_copy_1.fill(self.base_color)
        surfaces[0].set_colorkey((127, 127, 127))
        img_copy_1.blit(surfaces[0], (0, 0))
        surfaces[0].set_colorkey((255, 255, 255))

        img_copy_2 = pygame.Surface(surfaces[1].get_size())
        img_copy_2.fill(self.base_color)
        surfaces[1].set_colorkey((127, 127, 127))
        img_copy_2.blit(surfaces[1], (0, 0))
        surfaces[1].set_colorkey((255, 255, 255))

        return img_copy_1, img_copy_2

    def update_sprite_state(self) -> None:
        if 0.1 <= time.time() - self.step:
            self.sprite_state = (self.sprite_state + 1) % 4
            self.step = time.time()

    @property
    def color(self) -> Color:
        """
        Colors:
        - normal
        - blue (edible)
        - grey (eaten)
        """
        if self.state == GhostState.EATEN:
            return EATEN_COLOR
        if self.state == GhostState.FRIGHTENED:
            if self.timer < BLINK_TIME and int(self.timer * 4) % 2 == 0:
                return BLINK_COLOR
            return FRIGHTENED_COLOR
        return self.base_color

    def reset(self) -> None:
        """
        Put ghost back to respawn
        Then put in CHASE state
        """
        self.pos = CoordinatesFloat(*self.starting_pos)
        self.cell = self.starting_pos
        self.heading_to = None
        self.dir = self.start_dir
        self.target = None
        self.state = GhostState.CHASE
        self.timer = 0.0
        self._wander = None

    def change_dir(self, dir: Directions) -> None:
        """
        Set direction ghost is facing
        """
        self.dir = dir

    def frighten(self, duration: float = FRIGHTENED_TIME) -> None:
        """
        Make ghost edible (eaten ones not affected)
        """
        if self.state == GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.timer = duration

    def die(self, respawn_time: float = RESPAWN_TIME) -> None:
        """
        Get eaten = walk to respawn,
        then wait until respawn_time over
        """
        self.state = GhostState.EATEN
        self.timer = respawn_time
        self.target = self.starting_pos

    def update(self, maze: MazeObj, player: Player,
               movement: float, dt: float) -> None:
        """Advance ghost by 1 frame

        Args:
            maze: current maze
            player: Pacman (position/direction are read)
            movement: Cells pacman moves current frame,
                ghost moves a fraction of it (depend on state)
            dt: Seconds of game time that passed
        """
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
        """
        Count timers down
        Switch state when run out
        """
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
        """
        Move to heading;
        return movement left over
        """
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
        """
        Choose next cell on the way to target,
        or None to wait
        """
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
        """
        Return cells to aim,
        best first (later ones are backup)

        Goal with no route (ex: blocked cell) skipped,
        which is why chasing styles always keeps pacman cell as backup
        """
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
        """
        Return corners, farthest from pacman first
        """
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
        """
        Return cell a few steps in front of pacman (in grid)
        """
        dx, dy = _AHEAD.get(player_dir, (0, 0))
        x = player_cell.x + dx * AMBUSH_DISTANCE
        y = player_cell.y + dy * AMBUSH_DISTANCE
        return Coordinates(min(max(x, 0), maze.size.x - 1),
                           min(max(y, 0), maze.size.y - 1))

    def _wander_goal(self, maze: MazeObj) -> Coordinates:
        """
        Return random open cell,
        kept until ghost reaches it
        """
        if self._wander is None or self._wander == self.cell:
            open_cells = [cell.loc for row in maze.maze for cell in row
                          if not all(cell.walls)]
            self._wander = random.choice(open_cells)
        return self._wander
