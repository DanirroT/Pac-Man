from __future__ import annotations
from src import (WindowedVisualizer, PMArgs, Maze, Screens, CloseProgram,
                 get_from_json_file, Directions)
from typing import TYPE_CHECKING
import json
import pygame

if TYPE_CHECKING:
    from pygame.event import Event


class PacMan:

    args: PMArgs
    maze: Maze
    highscore: list[tuple[str, int]]

    current_screen: Screens
    visualizer: WindowedVisualizer

    def __init__(self, args: PMArgs) -> None:
        self.args = args

        self.load_highscore()

        self.visualizer = WindowedVisualizer()
        self.visualizer.show_start(self.highscore)
        self.current_screen = Screens.START

        # self.maze = Maze(self.args)

    def load_highscore(self) -> None:
        try:
            self.highscore = get_from_json_file(
                self.args.highscore_filename)
        except FileNotFoundError:
            with open(self.args.highscore_filename, "x"):
                pass
            self.highscore = []

    def add_highscore(self, name: str, score: int) -> None:
        self.highscore.append((name, score))
        self.highscore.sort(key=lambda x: x[1], reverse=True)

    def save_highscore(self) -> None:

        with open(self.args.highscore_filename, "w") as file:
            json.dump(self.highscore, file, indent=4)

    def run_program(self) -> None:
        import pygame
        # print("Start Sim")
        # self.visualizer.screen.blit(self.visualizer.background, (0, 0))

        # input()
        # terminal_clear()

        self.turn = 0

        self.control: bool = False
        self.paused: bool = False
        try:
            while True:
                resize = False
                for event in pygame.event.get():
                    if event.type != pygame.MOUSEMOTION:
                        print(event)
                    if (event.type == pygame.QUIT):
                        raise CloseProgram
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LCTRL:
                            self.control = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LCTRL:
                            self.control = True
                        if (self.control and event.key == pygame.K_c):
                            raise KeyboardInterrupt

                    if event.type == pygame.VIDEORESIZE and not resize:
                        # print("VIDEORESIZE", event.w, event.h)
                        # print()
                        self.visualizer.resize(event.w, event.h,
                                               self.current_screen)
                        resize = True
                    elif event.type == pygame.WINDOWSIZECHANGED and not resize:
                        # print("WINDOWSIZECHANGED", event.x, event.y)
                        self.visualizer.resize(event.x, event.y,
                                               self.current_screen)
                        resize = True

                    if self.current_screen in [Screens.START,
                                               Screens.LOSE,
                                               Screens.WIN]:
                        self.process_menu_events(event)
                    else:
                        self.process_game_events(event)
        except CloseProgram:
            self.visualizer.terminate()

    def process_menu_events(self, event: Event) -> None:

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RETURN):
                self.start_game()
                self.paused = False
                self.current_screen = Screens.GAME
            elif (event.key == pygame.K_ESCAPE):
                raise CloseProgram

    def process_game_events(self, event: Event) -> None:

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                self.paused = not self.paused
                if self.paused:
                    self.visualizer.pause()
                else:
                    self.visualizer.update_display()
            if self.paused:
                return

            if (event.key == pygame.K_w or event.key == pygame.K_UP):
                self.maze.player.handle_input(Directions.UP)
            elif (event.key == pygame.K_d or event.key == pygame.K_RIGHT):
                self.maze.player.handle_input(Directions.RIGHT)
            elif (event.key == pygame.K_s or event.key == pygame.K_DOWN):
                self.maze.player.handle_input(Directions.DOWN)
            elif (event.key == pygame.K_a or event.key == pygame.K_LEFT):
                self.maze.player.handle_input(Directions.LEFT)

    def start_game(self) -> None:
        self.maze = Maze(self.args)
        self.visualizer.build_map(self.maze)
