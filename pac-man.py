from src import PacMan, input_args
import json


def main() -> int:
    try:
        args = input_args()
        game = PacMan(args)
        game.run()
    except (FileNotFoundError, json.JSONDecodeError):
        return 1
    return 0


if __name__ == "__main__":
    main()
