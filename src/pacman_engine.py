from __future__ import annotations
from src import WindowedVisualizer, PMArgs, Maze, get_from_json_file
from typing import TYPE_CHECKING
import json
from enum import Enum

if TYPE_CHECKING:
    import pygame
    from pygame.event import Event


class Screens(Enum):
    START = 1
    GAME = 2
    WIN = 3
    LOSE = 4


class CloseProgram(Exception):
    pass


class PacMan:

    args: PMArgs
    maze: Maze
    highscore: list[tuple[str, int]]

    current_screen: Screens
    visualizer: WindowedVisualizer

    def __init__(self, args: PMArgs):
        self.args = args

        self.load_highscore()

        self.visualizer = WindowedVisualizer(self.highscore)

        # self.maze = Maze(self.args)

    def load_highscore(self):
        try:
            self.highscore = get_from_json_file(
                self.args.highscore_filename)
        except FileNotFoundError:
            with open(self.args.highscore_filename, "x"):
                pass
            self.highscore = []

    def add_highscore(self, name: str, score: int):
        self.highscore.append((name, score))
        self.highscore.sort(key=lambda x: x[1], reverse=True)

    def save_highscore(self):

        with open(self.args.highscore_filename, "w") as file:
            json.dump(self.highscore, file, indent=4)

    def run_program(self) -> None:
        # print("Start Sim")
        # self.visualizer.screen.blit(self.visualizer.background, (0, 0))

        # input()
        # terminal_clear()

        run = True
        self.turn = 0

        self.visualizer.show_start()
        self.current_screen = Screens.START

        control: bool = False
        while run:
            for event in pygame.event.get():
                # print(event)
                if (event.type == pygame.QUIT):
                    run = False
                    continue
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        control = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        control = True
                    if (control and event.key == pygame.K_c):
                        raise KeyboardInterrupt

                if event.type == pygame.VIDEORESIZE:
                    # print("VIDEORESIZE", event.w, event.h)
                    # print()
                    self.visualizer.resize(event.w, event.h, self.turn)
                elif event.type == pygame.WINDOWSIZECHANGED:
                    # print("WINDOWSIZECHANGED", event.x, event.y)
                    self.visualizer.resize(event.x, event.y, self.turn)

                try:
                    if self.current_screen in [Screens.START,
                                               Screens.LOSE,
                                               Screens.WIN]:
                        self.process_menu_events(event, control)
                    else:
                        self.process_game_events(event, control)
                except CloseProgram:
                    run = False

    def process_menu_events(self, event: Event, control: bool):

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RETURN):
                self.visualizer.show_game()
                self.current_screen = Screens.GAME
            elif (event.key == pygame.K_ESCAPE):
                raise CloseProgram

    def process_game_events(self, event: Event, control: bool):

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RETURN):
                self.visualizer.show_game()
                self.current_screen = Screens.GAME
            elif (event.key == pygame.K_ESCAPE):
                raise CloseProgram
