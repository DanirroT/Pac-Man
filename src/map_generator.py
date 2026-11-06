from src import Coordinates
from pydantic import BaseModel, Field, field_validator

import logging
from mazegenerator import (  # pyright: ignore
    MazeGenerator as ExternalMazeGenerator)
logger = logging.getLogger(__name__)
MIN_WIDTH, MIN_HEIGHT = 14, 10
MAX_WIDTH, MAX_HEIGHT = 50, 40


class MazeGenerationError(Exception):
    """usable maze cannot be produced"""


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

    def _clamp_size(self, size: Coordinates) -> Coordinates:
        """Force the size into [MIN, MAX]"""
        width = max(MIN_WIDTH, min(size.x, MAX_WIDTH))
        height = max(MIN_HEIGHT, min(size.y, MAX_HEIGHT))
        if (width, height) != (size.x, size.y):
            logger.warning("Maze size %dx%d out of range, using %dx%d",
                           size.x, size.y, width, height)
        return Coordinates(width, height)

    def _validate(self, grid: list[list[int]]) -> None:
        """Raise MazeGenerationError if the grid is not usable."""
        if len(grid) != self.configs.height:
            raise MazeGenerationError("maze has the wrong number of rows")
        for row in grid:
            if len(row) != self.configs.width:
                raise MazeGenerationError("row has the wrong length number")
            for cell in row:
                if not 0 <= cell <= 15:
                    raise MazeGenerationError(
                        f"invalid cell value {cell}, expected 0-15"
                    )

    def __init__(self, lvl_layout: Coordinates, seed: int | None = None):
        size = self._clamp_size(lvl_layout)
        self.configs = MazeConfigs(
            width=size.x, height=size.y,
            entry=Coordinates(0, 0),
            exit=Coordinates(size.x - 1, size.y - 1),
            perfect=False,
            seed=seed)

    def generate_maze(self) -> list[list[int]]:
        cfg = self.configs
        try:
            gen = ExternalMazeGenerator(
                size=(cfg.width, cfg.height), perfect=cfg.perfect,
                entry_cell=(cfg.entry.x, cfg.entry.y),
                exit_cell=(cfg.exit.x, cfg.exit.y),
                seed=cfg.seed or 0)
            grid: list[list[int]] = gen.maze
        except Exception as err:
            raise MazeGenerationError(f"Maze generator failed: {err}") from err
        self._validate(grid)
        return grid

    def use_preset_maze(self) -> list[list[int]]:

        self.configs = MazeConfigs(
            width=20,
            height=15,
            entry=Coordinates(0, 0),
            exit=Coordinates(19, 14),
            perfect=False,
            seed=42
        )

        return [[int(c, 16) for c in line] for line in (
            "B9555395555395515553\n"
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
            "C5554556D45546D54456").splitlines()]

        # self.configs = MazeConfigs(
        #     width=3,
        #     height=3,
        #     entry=Coordinates(0, 0),
        #     exit=Coordinates(2, 2),
        #     perfect=False,
        #     seed=42
        # )

        # return [[11, 13, 3],
        #         [10, 8, 2],
        #         [12, 6, 14]]
