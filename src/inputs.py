import sys
import json
from typing import Any
from pathlib import Path


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


def input_args() -> dict[str, Any]:
    if len(sys.argv) != 2:
        print("Usage: python pac-man.py <config_file>")
        sys.exit(1)

    return get_from_json_file(sys.argv[1])
