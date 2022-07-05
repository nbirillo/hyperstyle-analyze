import os
import pickle
from pathlib import Path
from typing import Any, Union

from analysis.src.python.utils.file_utils import get_parent_folder


def serialize_data_and_write_to_file(path: Union[Path, str], data: Any) -> None:
    os.makedirs(get_parent_folder(path), exist_ok=True)
    with open(path, 'wb') as f:
        p = pickle.Pickler(f)
        p.dump(data)


def deserialize_data_from_file(path: Union[Path, str]) -> Any:
    with open(path, 'rb') as f:
        u = pickle.Unpickler(f)
        return u.load()
