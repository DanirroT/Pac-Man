from typing import Any


class MazeGenerator:

    configs: dict[str, Any]

    def __init__(self, configs: dict[str, Any]):
        self.configs = configs

    def generate_maze(self) -> list[list[int]]:
        pass

    def use_preset_maze(self) -> list[list[int]]:

        self.configs = {
            "WIDTH": 20,
            "HEIGHT": 15,
            "ENTRY": (0, 0),
            "EXIT": (19, 14),
            "PERFECT": True
        }

        maze_lines = ("B9555395555395515553\n"
                      "C6D396E9553C693E953A\n"
                      "9552C53853C556C3AD42\n"
                      "AD54396ABC397956853A\n"
                      "A9396C3C07AC5453C7AA\n"
                      "86AC17AFAFAFFFBC556A\n"
                      "ABAD696FEF857F851396\n"
                      "AAC556BFFFAFFF87AAC3\n"
                      "C4393943BFAFD5296E96\n"
                      "956AC6BAAFAFFFAC556B\n"
                      "C5569786856953A95152\n"
                      "D3954569453AD6AE96BA\n"
                      "92A95396956855696946\n"
                      "AEC696E9697C3956BAD3\n"
                      "C5554556D45546D54456").splitlines()

        return [[int(c, 16) for c in line] for line in maze_lines]
