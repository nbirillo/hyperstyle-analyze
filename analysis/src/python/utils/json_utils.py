import json
from pathlib import Path
from typing import Any, Union


def parse_json(path: Union[Path, str]) -> Any:
    with open(path) as file:
        return json.load(file)
