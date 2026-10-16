from src import (Coordinates, MazeGenerator, Maze, WindowedVisualizer,
                 input_args)
from time import sleep


if __name__ == "__main__":
    maze_gen = MazeGenerator(Coordinates(1, 1))
    maze_int = maze_gen.use_preset_maze()

    # maze_int = [[11, 13, 3],
    #             [10, 8, 2],
    #             [12, 6, 14]]

    maze_obj = Maze(input_args())
    maze_obj.load_pre_set()

    print(maze_obj.maze)

    visualizer = WindowedVisualizer([])
    visualizer.show_start()
    print("\nShowing Start Screen")
    sleep(1)
    visualizer.build_map(maze_obj)
    visualizer.update_display(0)
    input("\nShowing Map")
    visualizer.terminate()
