from pathlib import Path
from typing import Optional, Tuple

import pytest

from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.utils import DF_UTILS_DATA_FOLDER

RESOURCES_PATH = DF_UTILS_DATA_FOLDER / 'read_df'

INPUT_DATA = [
    ('in_1.csv', (3, 4)),
    ('in_2.xlsx', (3, 4)),
    ('in_3.json', None)
]


@pytest.mark.parametrize(('in_file', 'shape'), INPUT_DATA)
def test(in_file: Path, shape: Optional[Tuple[int, int]]):
    if shape is not None:
        in_df = read_df(RESOURCES_PATH / in_file)
        assert in_df.shape == shape
    else:
        with pytest.raises(ValueError):
            read_df(RESOURCES_PATH / in_file)
