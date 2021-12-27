from enum import Enum, unique
from pathlib import Path
from typing import Union

import pandas as pd
from hyperstyle.src.python.review.common.file_system import Encoding


def write_dataframe_to_csv(csv_file_path: Union[str, Path], df: pd.DataFrame) -> None:
    # Get error with this encoding=ENCODING on several fragments. So change it then to 'utf8'
    try:
        df.to_csv(csv_file_path, encoding=Encoding.ISO_ENCODING.value, index=False)
    except UnicodeEncodeError:
        df.to_csv(csv_file_path, encoding=Encoding.UTF_ENCODING.value, index=False)


def append_dataframe_to_csv(csv_file_path: Union[str, Path], df: pd.DataFrame) -> None:
    # Get error with this encoding=ENCODING on several fragments. So change it then to 'utf8'
    try:
        df.to_csv(csv_file_path, encoding=Encoding.ISO_ENCODING.value, index=False, mode='a', header=False)
    except UnicodeEncodeError:
        df.to_csv(csv_file_path, encoding=Encoding.UTF_ENCODING.value, index=False, mode='a', header=False)


@unique
class ColumnName(Enum):
    CODE = 'code'
    LANG = 'lang'
    LANGUAGE = 'language'
    GRADE = 'grade'
    ID = 'id'
    COLUMN = 'column'
    ROW = 'row'
    OLD = 'old'
    NEW = 'new'
    IS_PUBLIC = 'is_public'
    DECREASED_GRADE = 'decreased_grade'
    PENALTY = 'penalty'
    USER = 'user'
    HISTORY = 'history'
    TIME = 'time'
    TRACEBACK = 'traceback'
