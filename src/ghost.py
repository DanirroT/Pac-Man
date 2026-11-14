"""Ghosts: states, targets and cell-to-cell movement.

A ghost always walks from one cell centre to the next along a shortest path
(``maze_graph.find_path``). It only decides where to go while it stands
exactly on a cell centre, so it can never cut a corner or enter a wall, and
its speed can change freely without breaking that.

States:
    CHASE       walks towards a target that depends on its style
    FRIGHTENED  edible, runs to the corner farthest from the player
    EATEN       walks back to its starting corner, then waits to respawn

Timers count game time (the ``dt`` given to ``update``), so they stop while
the game is paused, because the engine stops calling ``update`` then.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import TYPE_CHECKING

from .helper import Coordinates, CoordinatesFloat, Directions, s_round
from .maze_graph import direction_between, find_path

if TYPE_CHECKING:
    from .map_manager import MazeObj, Player

Color = tuple[int, int, int]

FRIGHTENED_TIME = 8.0    # seconds a ghost stays edible
BLINK_TIME = 2.0         # edible ghosts blink during the last seconds
RESPAWN_TIME = 5.0       # seconds before an eaten ghost chases again
AMBUSH_DISTANCE = 4      # cells ahead of the player that AMBUSH aims at
SHY_DISTANCE = 8         # SHY ghosts back off when closer than this
WANDER_DISTANCE = 5      # WANDER ghosts chase when the player is this close
EPSILON = 1e-9

FRIGHTENED_COLOR: Color = (33, 33, 255)
BLINK_COLOR: Color = (255, 255, 255)
EATEN_COLOR: Color = (90, 90, 90)


class GhostState(Enum):
    """What a ghost is currently doing."""

    CHASE = "ch"
    FRIGHTENED = "fr"
    EATEN = "ea"

    def __str__(self) -> str:
        return self.value


class GhostStyle(Enum):
    """How a ghost picks its target while chasing."""

    DIRECT = "direct"    # goes straight for the player
    AMBUSH = "ambush"    # aims a few cells ahead of the player
    WANDER = "wander"    # roams randomly until the player gets close
    SHY = "shy"          # chases from far away, backs off when close

    def __str__(self) -> str:
        return self.value


# Ghost speed as a fraction of the movement the player gets each frame.
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
    """Return the Manhattan distance between two cells (walls ignored)."""
    return abs(a.x - b.x) + abs(a.y - b.y)


class Ghost:
    """One ghost: where it is, what it is doing and where it is heading.

    ``pos`` is what gets drawn and used for collisions. ``cell`` is the last
    cell centre the ghost reached, and ``heading_to`` the next one (or None
    when it is standing on a centre). A ghost is only ever on the straight
    line between those two cells.
    """

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
        """Create a ghost standing on ``pos``, which is also its home."""
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
        """Colour to draw: normal, blue when edible, grey when eaten."""
        if self.state == GhostState.EATEN:
            return EATEN_COLOR
        if self.state == GhostState.FRIGHTENED:
            if self.timer < BLINK_TIME and int(self.timer * 4) % 2 == 0:
                return BLINK_COLOR
            return FRIGHTENED_COLOR
        return self.base_color

    def reset(self) -> None:
        """Put the ghost back home, in CHASE state (frozen is kept)."""
        self.pos = CoordinatesFloat(*self.starting_pos)
        self.cell = self.starting_pos
        self.heading_to = None
        self.dir = self.start_dir
        self.target = None
        self.state = GhostState.CHASE
        self.timer = 0.0
        self._wander = None

    def change_dir(self, dir: Directions) -> None:
        """Set the direction the ghost is facing."""
        self.dir = dir

    def frighten(self, duration: float = FRIGHTENED_TIME) -> None:
        """Make the ghost edible (an eaten ghost is not affected)."""
        if self.state == GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.timer = duration

    def die(self, respawn_time: float = RESPAWN_TIME) -> None:
        """Get eaten: walk home, then wait until ``respawn_time`` is over."""
        self.state = GhostState.EATEN
        self.timer = respawn_time
        self.target = self.starting_pos

    def update(self, maze: MazeObj, player: Player,
               movement: float, dt: float) -> None:
        """Advance the ghost by one frame.

        Args:
            maze: The current maze.
            player: The player (its position and direction are read).
            movement: Cells the player moves this frame; the ghost moves a
                fraction of it depending on its state (see ``SPEED``).
            dt: Seconds of game time that passed, used for the timers.
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
        """Count the timers down and switch state when they run out."""
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
        """Move towards ``heading``; return the movement left over."""
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
        """Choose the next cell on the way to a goal, or None to wait."""
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
        """Return the cells to aim for, best first (later ones are backups).

        A goal with no route (for example a blocked cell) is skipped, which
        is why chasing styles always keep the player's cell as a backup.
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
        """Return the corners, farthest from the player first."""
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
        """Return the cell a few steps in front of the player (in the grid)."""
        dx, dy = _AHEAD.get(player_dir, (0, 0))
        x = player_cell.x + dx * AMBUSH_DISTANCE
        y = player_cell.y + dy * AMBUSH_DISTANCE
        return Coordinates(min(max(x, 0), maze.size.x - 1),
                           min(max(y, 0), maze.size.y - 1))

    def _wander_goal(self, maze: MazeObj) -> Coordinates:
        """Return a random open cell, kept until the ghost reaches it."""
        if self._wander is None or self._wander == self.cell:
            open_cells = [cell.loc for row in maze.maze for cell in row
                          if not all(cell.walls)]
            self._wander = random.choice(open_cells)
        return self._wander
