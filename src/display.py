from __future__ import annotations
from src import (Screens, CellState, Overlays, SqPOI,
                 Coordinates, CoordinatesFloat,
                 Maze, MazeObj)
from typing import TYPE_CHECKING
import pygame


if TYPE_CHECKING:
    # from pygame.rect import Rect
    from pygame.surface import Surface
    from pygame.font import Font


class WindowedVisualizer():

    screen: Surface
    # dimensions: Coordinates = Coordinates(2200, 1400)
    dimensions: Coordinates = Coordinates(1200, 700)
    margins: Coordinates = Coordinates(100, 100)
    font: Font
    scale: Coordinates

    start_static: Surface
    highscore: list[tuple[str, int]]
    win_static: Surface
    lose_static: Surface

    starting_overlay: Surface
    pause_overlay: Surface

    maze_manager: Maze
    maze_obj: MazeObj
    maze_background: Surface
    middle_map: CoordinatesFloat

    def __init__(self) -> None:
        pygame.init()

        self.highscore = []

        self.screen = pygame.display.set_mode(self.dimensions,
                                              pygame.RESIZABLE)
        self.screen.fill((0, 0, 0))

        pygame.font.init()
        pygame.display.set_caption("Pac-Man")
        self.build_menus()

        self.clock = pygame.time.Clock()

        pacman_png = pygame.image.load("images/pacman.png").convert_alpha()

        pygame.display.set_icon(pygame.transform.scale(pacman_png,
                                                       (64, 64)))

        pygame.display.update()

    def get_sq_poi(self, pos: Coordinates | CoordinatesFloat,
                   poi: SqPOI = SqPOI.C) -> Coordinates:
        """
        Converts a cell position to a pixel position on the display,
        based on the specified point of interest (POI) within the cell.
        """

        """
       - print()
       - print()
       - print("original list", pos)

       - print("to cell relative", (pos.x - self.middle_map.x),
              (pos.y - self.middle_map.y))

       - print("to pixel relative",
              (pos.x - self.middle_map.x) * self.cell_size,
              (pos.y - self.middle_map.y) * self.cell_size)
       - print()
       - print("absolute pixel pos", Coordinates(
            round(((pos.x - self.middle_map.x) * self.cell_size)
                  + self.dimensions.x/2),
            round(((pos.y - self.middle_map.y) * self.cell_size)
                  + self.dimensions.y/2)
        ))

        pygame.draw.circle(
            self.maze_background, (255, 0, 0),
            (int(((pos.x - self.middle_map.x) * self.cell_size)
            + self.dimensions.x/2),
            int(((pos.y - self.middle_map.y) * self.cell_size)
            + self.dimensions.y/2)),
            5)

       - print("absolute pixel pos TL", Coordinates(
            round(((pos.x - self.middle_map.x) * self.cell_size)
                  + self.dimensions.x/2 - (self.cell_size / 2)),
            round(((pos.y - self.middle_map.y) * self.cell_size)
                  + self.dimensions.y/2 - (self.cell_size / 2))
        ))

        pygame.draw.circle(
            self.maze_background, (0, 255, 0),
            (int(((pos.x - self.middle_map.x) * self.cell_size) +
            self.dimensions.x/2 - (self.cell_size / 2)),
            int(((pos.y - self.middle_map.y) * self.cell_size) +
            self.dimensions.y/2 - (self.cell_size / 2))),
            5)

        input()
        """

        return Coordinates(
            round((pos.x - self.middle_map.x) * self.cell_size
                  + self.dimensions.x/2
                  + ((self.cell_size / 2) if "r" in poi.value else 0)
                  - ((self.cell_size / 2) if "l" in poi.value else 0)),
            round(((pos.y - self.middle_map.y) * self.cell_size)
                  + self.dimensions.y/2
                  + ((self.cell_size / 2) if "b" in poi.value else 0)
                  - ((self.cell_size / 2) if "t" in poi.value else 0)))

    def build_menus(self) -> None:

        self.text_size = (self.dimensions.y - 2 * self.margins.y) // 15

        self.title_1_font = pygame.font.SysFont(
            'freesanbold.ttf', self.text_size * 2, bold=True)
        self.title_2_font = pygame.font.SysFont(
            'freesanbold.ttf', round(self.text_size * 1.2))
        self.r_text_font = pygame.font.SysFont(
            'freesanbold.ttf', self.text_size)

        self.start_static = pygame.Surface(self.dimensions)

        self.start_static.fill((0, 0, 30))

        start_title = self.title_1_font.render("Pac-Man", True, (255, 255, 0))
        self.start_static.blit(start_title, start_title.get_rect(
            center=(self.dimensions.x // 2, self.margins.y + self.text_size)))

        start_hs = self.title_2_font.render("HighScore", True, (255, 255, 255))
        self.start_static.blit(start_hs, start_hs.get_rect(
            center=(self.dimensions.x // 2,
                    self.margins.y + self.text_size * 3)))
        # start_hs_list = [self.r_text_font.render(
        #     f"{n} {s}", True, (255, 255, 255))
        #     for n, s in self.high_scores[10:]]

        self.win_static = pygame.Surface(self.dimensions)
        self.win_static.fill((0, 0, 0))

        win_title = self.title_1_font.render("Congratulations!",
                                             True, (0, 255, 255))
        self.win_static.blit(win_title, win_title.get_rect(
            center=(self.dimensions.x // 2,
                    self.dimensions.y // 2 - self.text_size * 5)))

        win_score = self.title_2_font.render("Your Score", True, (0, 255, 255))
        self.win_static.blit(win_score, win_score.get_rect(
            center=(self.dimensions.x // 2, self.dimensions.y // 2)))

        self.lose_static = pygame.Surface(self.dimensions)
        self.lose_static.fill((0, 0, 0))

        lose_title = self.title_1_font.render("Game Over", True, (0, 0, 255))
        self.lose_static.blit(lose_title, lose_title.get_rect(
            center=(self.dimensions.x // 2,
                    self.dimensions.y // 2 - self.text_size * 5)))

        lose_score = self.title_2_font.render("Your Score", True, (0, 0, 255))
        self.lose_static.blit(lose_score, lose_score.get_rect(
            center=(self.dimensions.x // 2, self.dimensions.y // 2)))

        self.pause_overlay = pygame.Surface(self.dimensions)
        self.pause_overlay.set_alpha(128)
        self.pause_overlay.fill((0, 0, 0))
        pause_text = self.title_1_font.render("Paused", True, (255, 255, 255))
        self.pause_overlay.blit(pause_text, pause_text.get_rect(
            center=(self.dimensions.x // 2, self.dimensions.y // 2)))

        self.starting_overlay = pygame.Surface(self.dimensions)
        self.starting_overlay.set_alpha(128)
        self.starting_overlay.fill((0, 0, 0))
        pause_text = self.title_1_font.render(
            "Press any key to start", True, (255, 255, 255))
        self.starting_overlay.blit(pause_text, pause_text.get_rect(
            center=(self.dimensions.x // 2, self.dimensions.y // 2)))

        self.scoring_static = pygame.Surface(self.dimensions)
        self.scoring_static.fill((0, 0, 0))
        enquiry = self.title_2_font.render(
            "Register Score?", True, (255, 255, 255))
        self.scoring_static.blit(enquiry, enquiry.get_rect(
            center=(self.dimensions.x // 2,
                    self.dimensions.y // 2 - self.text_size * 3)))
        instructions = self.r_text_font.render(
            "Write your name and press Enter. Press Esc to skip.",
            True, (255, 255, 255))
        self.scoring_static.blit(instructions, instructions.get_rect(
            center=(self.dimensions.x // 2, self.dimensions.y // 2)))

    def build_map(self) -> None:
        # self.maze_size = Coordinates(len(map_obj[0]), len(map_obj))
        self.maze_background = pygame.Surface(self.dimensions)

        self.maze_background.fill((0, 0, 0))

        self.middle_map = (
            CoordinatesFloat((self.maze_obj.size.x - 1) / 2,
                             (self.maze_obj.size.y - 1) / 2))

        self.margins = Coordinates(100, 100)

        self.cell_size = min(
            round((self.dimensions.x - (2 * self.margins.x))
                  / self.maze_obj.size.x),
            round((self.dimensions.y - (2 * self.margins.y))
                  / self.maze_obj.size.y)
        )

        self.s_obj_size = round(self.cell_size / 6)
        self.l_obj_size = round(self.s_obj_size * 2)
        self.text_size = 20

        self.text_margin = int(self.text_size * 0.75)

        self.font = pygame.font.SysFont('freesanbold.ttf', self.text_size)

        """
        # print("cell_size:", self.cell_size)
        # print("s_obj_size:", self.s_obj_size)
        # print("l_obj_size:", self.l_obj_size)
        # print("middle_map:", self.middle_map)

        # pygame.draw.circle(self.maze_background, (0, 255, 255),
        #                    (self.dimensions.x // 2, self.dimensions.y // 2),
        #                    15)

        pygame.draw.circle(self.maze_background, (255, 255, 0),
                           self.get_sq_poi(self.middle_map),
                           10)

        # pygame.draw.circle(self.maze_background, (255, 255, 0),
        #                    self.get_sq_poi(self.middle_map, SqPOI.TR),
        #                    10)

        # pygame.draw.circle(self.maze_background, (255, 255, 0),
        #                    self.get_sq_poi(self.middle_map, SqPOI.TL),
        #                    10)

        # pygame.draw.circle(self.maze_background, (255, 255, 0),
        #                    self.get_sq_poi(self.middle_map, SqPOI.BL),
        #                    10)

        # pygame.draw.circle(self.maze_background, (255, 255, 0),
        #                    self.get_sq_poi(self.middle_map, SqPOI.BR),
        #                    10)
        """

        """

        middle_display = Coordinates(round(self.dimensions.x/2),
                                     round(self.dimensions.y/2))

       - print()
       - print("scale:", self.scale)
       - print()
       - print("middle-display:", middle_display)
       - print()
       - print("middle-map:", self.middle_map)
       - print()
       - print("middle-convert:", self.pos_to_display(self.middle_map))
       - print()
        pygame.draw.line(self.screen, (0, 0, 0),
                         self.dimensions, (0, 0), 5)
        pygame.draw.line(self.screen, (0, 0, 0),
                         (0, self.dimensions.y), (self.dimensions.x, 0), 5)

        pygame.draw.line(self.screen, (0, 0, 0),
                         (self.dimensions.x, middle_display.y),
                         (0, middle_display.y), 5)
        pygame.draw.line(self.screen, (0, 0, 0),
                         (middle_display.x, self.dimensions.y),
                         (middle_display.x, 0), 5)
        """

        for line in self.maze_obj.maze:
            for cell in line:
                # print("top  " if cell.walls.up else "     ", end="")
                # print("right" if cell.walls.right else "     ", end="")
                # print("down " if cell.walls.down else "     ", end="")
                # print("left " if cell.walls.left else "     ", end="")
                # print(" Blocked" if cell.state == CellState.BLOCKED
                #       else "", end="")
                # print()
                if cell.state == CellState.BLOCKED:
                    pygame.draw.rect(
                        self.maze_background, (0, 0, 128),
                        pygame.Rect(
                            self.get_sq_poi(cell.loc, SqPOI.TL),
                            (self.cell_size, self.cell_size))
                        )
                if cell.walls.left:  # left wall
                    pygame.draw.line(
                        self.maze_background, (0, 0, 255),
                        self.get_sq_poi(cell.loc, SqPOI.BL),
                        self.get_sq_poi(cell.loc, SqPOI.TL),
                        self.s_obj_size)
                if cell.walls.up:  # top wall
                    pygame.draw.line(
                        self.maze_background, (0, 0, 255),
                        self.get_sq_poi(cell.loc, SqPOI.TR),
                        self.get_sq_poi(cell.loc, SqPOI.TL),
                        self.s_obj_size)
                if cell.walls.right:  # right wall
                    pygame.draw.line(
                        self.maze_background, (0, 0, 255),
                        self.get_sq_poi(cell.loc, SqPOI.BR),
                        self.get_sq_poi(cell.loc, SqPOI.TR),
                        self.s_obj_size)
                if cell.walls.down:  # bottom wall
                    pygame.draw.line(
                        self.maze_background, (0, 0, 255),
                        self.get_sq_poi(cell.loc, SqPOI.BR),
                        self.get_sq_poi(cell.loc, SqPOI.BL),
                        self.s_obj_size)

    def put_map_obj(self) -> None:

        for gum in self.maze_manager.pacgum:
            pygame.draw.circle(self.screen, (255, 184, 174),
                               self.get_sq_poi(gum), self.s_obj_size)
        for supergum in self.maze_manager.supergum:
            pygame.draw.circle(self.screen, (255, 184, 174),
                               self.get_sq_poi(supergum), self.l_obj_size)
        for ghost in self.maze_manager.ghosts:
            pygame.draw.circle(self.screen, ghost.color,
                               self.get_sq_poi(ghost.pos), self.l_obj_size)
        pygame.draw.circle(self.screen, (255, 255, 0), self.get_sq_poi(
            self.maze_manager.player.pos), self.l_obj_size)
        # pygame.draw.circle(self.screen, (255, 255, 0), self.get_sq_poi(
        #     Coordinates(self.maze_manager.maze.size.x // 2,
        #                 self.maze_manager.maze.size.y // 2)),
        #                 self.s_obj_size)

    def update_display(self, current_screen: Screens,
                       dimensions: Coordinates | bool = False,
                       player_name: str = ""
                       ) -> None:

        if len(player_name):
            print(f"Player Name: {player_name}")

        if dimensions and isinstance(dimensions, Coordinates):
            self.dimensions = dimensions
            # print("resize to:", w, h)

        elif current_screen == Screens.GAME:
            if dimensions:
                self.build_map()
            self.screen.blit(self.maze_background, (0, 0))
            self.put_map_obj()

        if dimensions:
            self.build_menus()

        if current_screen == Screens.START:
            self.show_start()

        elif current_screen == Screens.LOSE:
            self.show_end(self.maze_manager.score, Overlays.LOSE)

        elif current_screen == Screens.WIN:
            self.show_end(self.maze_manager.score, Overlays.WIN)

        elif current_screen == Screens.SCORING:
            self.show_scoring(player_name)

        pygame.display.update()

    def overlay(self, overlay: Overlays) -> None:
        if overlay == Overlays.PAUSE:
            self.screen.blit(self.pause_overlay, (0, 0))
        elif overlay == Overlays.LOSE:
            self.screen.blit(self.lose_static, (0, 0))
        elif overlay == Overlays.WIN:
            self.screen.blit(self.win_static, (0, 0))
        elif overlay == Overlays.STARTING:  # pyright: ignore
            self.screen.blit(self.starting_overlay, (0, 0))
        pygame.display.update()

    def show_start(self, high_scores: list[tuple[str, int]] = []) -> None:
        if len(high_scores):
            self.highscore = high_scores[:10]
        self.screen.blit(self.start_static, (0, 0))

        for i, (name, score) in enumerate(self.highscore):
            # print(f"{i + 1}. {name}: {score}")
            text = self.r_text_font.render(f"{i + 1}. {name}: {score}",
                                           True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(
                center=(self.dimensions.x // 2,
                        self.margins.y + self.text_size * (5 + i))))

        pygame.display.update()

    def show_scoring(self, player_name: str) -> None:
        self.screen.blit(self.scoring_static, (0, 0))

        text = self.title_2_font.render(player_name,
                                        True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(
            center=(self.dimensions.x // 2,
                    self.dimensions.y // 2 + self.text_size * 3)))

        pygame.display.update()

    def show_end(self, score: int, screen: Overlays) -> None:
        if screen == Overlays.WIN:
            self.screen.blit(self.win_static, (0, 0))
        elif screen == Overlays.LOSE:
            self.screen.blit(self.lose_static, (0, 0))

        text = self.title_2_font.render(f"Final Score: {score}",
                                        True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(
            center=(self.dimensions.x // 2,
                    self.dimensions.y // 2 + self.text_size * 3)))

        pygame.display.update()

    def terminate(self) -> None:
        pygame.quit()
