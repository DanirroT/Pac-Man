from src import Maze, get_from_json_file
from typing import Any
import json


class PacMan:

    args: dict[str, Any]
    maze: Maze
    highscore: list[tuple[str, int]]

    def __init__(self, args: dict[str, Any]):
        self.args = args

        self.load_highscore()

        self.maze = Maze(self.args)

    def run(self):
        # Placeholder for the game logic
        print(f"Running Pac-Man with arguments: {self.args}")

    def load_highscore(self):
        try:
            self.highscore = get_from_json_file(
                self.args["highscore_filename"])
        except FileNotFoundError:
            with open(self.args["highscore_filename"], "x"):
                pass
            self.highscore = []

    def add_highscore(self, name: str, score: int):
        self.highscore.append((name, score))
        self.highscore.sort(key=lambda x: x[1], reverse=True)

    def save_highscore(self):

        with open(self.args["highscore_filename"], "w") as file:
            json.dump(self.highscore, file, indent=4)

    # "highscore_filename": "highscore.txt",
    # "levels": [],
    # "lives" : 3,
    # "pacgum" : 42,
    # "points_per_pacgum" : 10,
    # "points_per_super_pacgum" : 50,
    # "points_per_ghost" : 200,
    # "seed" : 42,
    # "level_max_time" : 90
