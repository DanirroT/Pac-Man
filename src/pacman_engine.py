from __future__ import annotations
from src import (Overlays, Screens, Directions,
                 Coordinates,
                 PMArgs, CloseProgram,
                 WindowedVisualizer, Maze, get_from_json_file)
from typing import TYPE_CHECKING
import json
import pygame

if TYPE_CHECKING:
    from pygame.event import Event


class PacMan:

    args: PMArgs
    maze: Maze
    highscore: list[tuple[str, int]]
    player_name: str = ""

    current_screen: Screens
    visualizer: WindowedVisualizer

    def __init__(self, args: PMArgs) -> None:
        self.args = args

        self.load_highscore()

        self.visualizer = WindowedVisualizer()

        self.maze = Maze(self.args)

    def load_highscore(self) -> None:
        try:
            self.highscore = [(n, s) for n, s in (
                get_from_json_file(self.args.highscore_filename))]
        except FileNotFoundError:
            with open(self.args.highscore_filename, "x"):
                pass
            self.highscore = []

    def add_highscore(self, name: str, score: int) -> None:
        self.highscore.append((name, score))
        self.highscore.sort(key=lambda x: x[1], reverse=True)

    def save_highscore(self) -> None:

        with open(self.args.highscore_filename, "w") as file:
            json.dump(self.highscore[:100], file, indent=4)

    def run_program(self) -> None:
        # print("Start Sim")
        # self.visualizer.screen.blit(self.visualizer.background, (0, 0))

        # input()
        # terminal_clear()

        self.visualizer.show_start(self.highscore)
        self.current_screen = Screens.START

        self.control: bool = False
        self.overlay: Overlays | None = None
        try:
            while True:
                resize = False
                frame_step = self.visualizer.clock.get_rawtime()
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEMOTION:
                        continue
                    else:
                        print(event)

                    if (event.type == pygame.QUIT):
                        raise CloseProgram
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_LCTRL:
                            self.control = False
                            continue
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LCTRL:
                            self.control = True
                            continue
                        if (self.control and event.key == pygame.K_c):
                            raise KeyboardInterrupt

                    elif ((event.type == pygame.VIDEORESIZE)
                          and not resize):
                        # or event.type == pygame.WINDOWSIZECHANGED

                        # print("VIDEORESIZE", event.w, event.h)
                        # print()
                        self.visualizer.update_display(
                            self.current_screen, Coordinates(event.w, event.h))
                        resize = True
                        continue

                    else:
                        continue

                    if self.current_screen in [Screens.START,
                                               Screens.LOSE,
                                               Screens.WIN]:
                        self.process_menu_events(event)
                    elif self.current_screen in [Screens.SCORING]:
                        self.process_scoring_events(event)
                    else:
                        self.process_game_events(event)
                if (self.current_screen == Screens.GAME and  # pyright: ignore
                        not self.overlay and frame_step):
                    print(
                        self.maze.player.pos, self.maze.player.dir.value,
                        (self.maze.player.dir_queue.value
                         if self.maze.player.dir_queue else None),
                        self.maze.player.pos.x == int(self.maze.player.pos.x),
                        self.maze.player.pos.y == int(self.maze.player.pos.y),
                        end="")
                    if (self.maze.player.pos.x ==
                        int(self.maze.player.pos.x) and
                        self.maze.player.pos.y ==
                            int(self.maze.player.pos.y)):
                        self.maze.player.change_dir(
                            self.maze.maze.maze[
                                int(self.maze.player.pos.y)][
                                    int(self.maze.player.pos.x)])
                    self.maze.player.move(
                        1/2, self.maze.maze.maze[
                            int(self.maze.player.pos.y)][
                                int(self.maze.player.pos.x)].walls
                        if (self.maze.player.pos.y.is_integer() and
                            self.maze.player.pos.x.is_integer()) else None)
                    self.detect_obj_collisions()
                    self.visualizer.update_display(self.current_screen)

                self.visualizer.clock.tick(5)
                print()

        except CloseProgram:
            self.visualizer.terminate()

    def process_menu_events(self, event: Event) -> None:

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RETURN):
                if self.current_screen == Screens.START:
                    self.maze.current_map = -1
                try:
                    self.next_game()
                except IndexError:
                    self.current_screen = Screens.SCORING
                    self.player_name = ""
                    self.visualizer.update_display(self.current_screen)
                    return
                self.current_screen = Screens.GAME
            elif (event.key == pygame.K_ESCAPE and
                  self.current_screen == Screens.START):
                raise CloseProgram

    def process_scoring_events(self, event: Event) -> None:

        if event.type == pygame.KEYDOWN:

            if (event.key == pygame.K_ESCAPE):
                self.player_name = ""
                self.maze.score = 0
                self.current_screen = Screens.START

            elif (event.key == pygame.K_RETURN):
                if self.player_name:
                    self.add_highscore(self.player_name, self.maze.score)
                self.player_name = ""
                self.maze.score = 0
                self.current_screen = Screens.START

            elif (event.key == pygame.K_BACKSPACE):
                self.player_name = self.player_name[:-1]
            else:
                self.player_name += event.unicode

            if self.current_screen == Screens.START:
                print("Start")
                print(self.highscore)
                self.visualizer.show_start(self.highscore)
            else:
                print("continue")
                self.visualizer.update_display(
                    self.current_screen, player_name=self.player_name)

    def process_game_events(self, event: Event) -> None:

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                if not self.overlay:
                    self.overlay = Overlays.PAUSE
                    self.visualizer.overlay(self.overlay)
                else:
                    self.visualizer.update_display(self.current_screen)
                    self.overlay = None
                    return
            if self.overlay == Overlays.PAUSE:
                if (event.key == pygame.K_RETURN):
                    self.visualizer.update_display(self.current_screen)
                    self.overlay = None
                return
            if self.overlay == Overlays.STARTING:
                self.visualizer.update_display(self.current_screen)
                self.overlay = None
                return

            if (event.key == pygame.K_w or event.key == pygame.K_UP):
                self.maze.player.handle_input(Directions.UP)
                # self.maze.player.pos = (
                #     CoordinatesFloat(self.maze.player.pos.x,
                #                      self.maze.player.pos.y - 1))
            elif (event.key == pygame.K_d or event.key == pygame.K_RIGHT):
                self.maze.player.handle_input(Directions.RIGHT)
                # self.maze.player.pos = (
                #     CoordinatesFloat(self.maze.player.pos.x + 1,
                #                      self.maze.player.pos.y))
            elif (event.key == pygame.K_s or event.key == pygame.K_DOWN):
                self.maze.player.handle_input(Directions.DOWN)
                # self.maze.player.pos = (
                #     CoordinatesFloat(self.maze.player.pos.x,
                #                      self.maze.player.pos.y + 1))
            elif (event.key == pygame.K_a or event.key == pygame.K_LEFT):
                self.maze.player.handle_input(Directions.LEFT)
                # self.maze.player.pos = (
                #     CoordinatesFloat(self.maze.player.pos.x - 1,
                #                      self.maze.player.pos.y))
            elif (event.key == pygame.K_p):
                self.maze.player.wall_phase = not self.maze.player.wall_phase

            elif (event.key == pygame.K_i):
                self.maze.player.invincibility = (
                    not self.maze.player.invincibility)

            elif (event.key == pygame.K_o):
                self.maze.player.extra_speed = not self.maze.player.extra_speed

            self.visualizer.update_display(self.current_screen)

    def next_game(self) -> None:
        self.current_screen = Screens.GAME
        self.maze.load_next_map()
        # self.maze.get_wall_less()
        self.visualizer.maze_manager = self.maze
        self.visualizer.maze_obj = self.maze.maze
        self.visualizer.update_display(self.current_screen,
                                       True)
        self.overlay = Overlays.STARTING
        self.visualizer.overlay(Overlays.STARTING)

    def detect_obj_collisions(self) -> None:
        for ghost in self.maze.ghosts:
            if (pow(ghost.pos.x - self.maze.player.pos.x, 2) +
                    pow(ghost.pos.y - self.maze.player.pos.y, 2) < 0.5):
                if self.maze.player.supergum_power:
                    ghost.die()
                    self.maze.score += self.args.points_per_ghost
                elif not self.maze.player.invincibility:
                    self.maze.player.lives -= 1
                    if self.maze.player.lives <= 0:
                        self.current_screen = Screens.LOSE
                    else:
                        self.maze.player.reset()
                    return

        if len(self.maze.pacgum):
            for pacgum in self.maze.pacgum.copy():
                if (pow(pacgum.x - self.maze.player.pos.x, 2) +
                        pow(pacgum.y - self.maze.player.pos.y, 2) < (1/100)):
                    self.maze.pacgum.remove(pacgum)
                    self.maze.score += self.args.points_per_pacgum

        if len(self.maze.supergum):
            for supergum in self.maze.supergum.copy():
                if (pow(supergum.x - self.maze.player.pos.x, 2) +
                        pow(supergum.y - self.maze.player.pos.y, 2) < (1/16)):
                    self.maze.supergum.remove(supergum)
                    self.maze.score += self.args.points_per_super_pacgum
                    self.maze.player.supergum_power = True

        # if len(self.maze.supergum) + len(self.maze.pacgum) == 0:
        if len(self.maze.pacgum) == 0:
            self.current_screen = Screens.WIN
