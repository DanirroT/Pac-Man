from typing import Any


class PacMan:

    args: dict[str, Any]
    maze: Maze
    highscore: dict[str, int]

    def __init__(self, args: dict[str, Any]):
        self.args = args

        self.load_highscore()

        self.maze = Maze(self.args)

    def run(self):
        # Placeholder for the game logic
        print(f"Running Pac-Man with arguments: {self.args}")

    def load_highscore(self):
        self.highscore = {}
        try:
            with open(self.args["highscore_filename"], "r") as file:
                file_lines = file.read().splitlines()
            for line in file_lines:
                split_line = line.split()
                try:
                    self.highscore[split_line[0]] = int(split_line[1])
                except (ValueError, IndexError):
                    print(f"Invalid line '{line}' in highscore file. Skipping.")
        except FileNotFoundError:
            pass

    def save_highscore(self):
        out_list: list[tuple[str, int]] = []

        for name, score in self.highscore.items():
            out_list.append((name, score))
        out_list.sort(key=lambda x: x[1], reverse=True)

        with open(self.args["highscore_filename"], "w") as file:
            for name, score in out_list:
                file.write(f"{name} {score}\n")

    "highscore_filename": "highscore.txt",
    "levels": [],
    "lives" : 3,
    "pacgum" : 42,
    "points_per_pacgum" : 10,
    "points_per_super_pacgum" : 50,
    "points_per_ghost" : 200,
    "seed" : 42,
    "level_max_time" : 90
