from src import Coordinates, MazeGenerator
from src.map_generator import MazeGenerationError
import copy

g = MazeGenerator(Coordinates(20, 15), 42)
grid = g.generate_maze()
print(len(grid), len(grid[0]))

good = g.generate_maze()

short_row = copy.deepcopy(good)
short_row[3].pop()            # one row now has 19 cells

bad_cell = copy.deepcopy(good)
bad_cell[3][4] = 99           # one cell has an impossible value


for name, bad in (("short row", short_row), ("bad cell", bad_cell)):
    try:
        g._validate(bad)
        print(name, "NOT caught!")
    except MazeGenerationError as e:
        print(name, "caught:", e)

print(MazeGenerator(Coordinates(1, 1)).configs.width)
