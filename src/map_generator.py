from src import Coordinates
from pydantic import BaseModel, Field, field_validator


class MazeConfigs(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    entry: Coordinates = Field()
    exit: Coordinates = Field()
    perfect: bool = Field()
    seed: int | None = Field(default=None)

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, v: str | Coordinates | tuple[int, int]
                          ) -> Coordinates:
        """Parse coordinate strings like 'x,y' into coordinate tuples."""
        if isinstance(v, str):
            x, y = v.split(",")
            out = Coordinates(int(x), int(y))
        elif isinstance(v, tuple) and len(v) == 2:  # pyright: ignore
            out = Coordinates(*v)
        else:
            out = v
        if out.x < 0 or out.y < 0:
            raise ValueError("Coordinates must be non-negative.")
        return out


class MazeGenerator:

    configs: MazeConfigs

    def __init__(self, lvl_layout: Coordinates, seed: int | None = None):
        self.configs = MazeConfigs(
            width=lvl_layout.x,
            height=lvl_layout.y,
            entry=Coordinates(0, 0),
            exit=Coordinates(lvl_layout.x - 1, lvl_layout.y - 1),
            perfect=True,
            seed=seed
        )

    def generate_maze(self) -> list[list[int]]:
        return []

    def use_preset_maze(self) -> list[list[int]]:

        self.configs = MazeConfigs(
            width=20,
            height=15,
            entry=Coordinates(0, 0),
            exit=Coordinates(19, 14),
            perfect=True,
            seed=42
        )

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
