import sys
import json
from typing import Any
from pathlib import Path
from pydantic import BaseModel, Field
from src import Coordinates
from dotenv import load_dotenv


class PMArgs(BaseModel):
    highscore_filename: str = Field(min_length=1)
    # levels: list[Coordinates] = Field(min_length=10)
    levels: list[Coordinates] = Field()
    lives: int = Field(gt=0)
    pacgum: int = Field(gt=0)
    points_per_pacgum: int = Field(gt=0)
    points_per_super_pacgum: int = Field(gt=0)
    points_per_ghost: int = Field(gt=0)
    seed: int
    level_max_time: int = Field(gt=0)


def get_from_json_file(file_path: str | Path,
                       encoding: str | None = None) -> Any:

    try:
        with open(file_path, encoding=encoding) as file_obj:
            output = json.load(file_obj)
    except FileNotFoundError:
        print(f"File '{file_path}' not found. "
              "Please create the file and try again.")
        raise
    except OSError:
        print(f"File '{file_path}' is not accessible. "
              "Please check File Permissions.")
        raise FileNotFoundError
    except json.JSONDecodeError as e:
        print(f"File '{file_path}' is not valid JSON.", e, sep="\n")
        raise

    return output


def input_args() -> PMArgs:
    if len(sys.argv) != 2:
        print("Usage: python pac-man.py <config_file>")
        sys.exit(1)

    load_dotenv()

    return PMArgs(**get_from_json_file(sys.argv[1]))
