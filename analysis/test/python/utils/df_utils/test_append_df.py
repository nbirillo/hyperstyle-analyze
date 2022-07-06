from pathlib import Path
from typing import Tuple

import pytest

from analysis.src.python.evaluation.utils.args_util import get_in_and_out_list
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.src.python.utils.extension_utils import get_restricted_extension
from analysis.test.python.utils import DF_UTILS_DATA_FOLDER

RESOURCES_PATH = DF_UTILS_DATA_FOLDER / 'append_df'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)

INPUT_DATA = [
    ('in_1.csv', (3, 4)),
    ('in_2.xlsx', (3, 4)),
    ('in_2.json', None),
]


@pytest.mark.parametrize(('in_file', 'shape'), INPUT_DATA)
def test(in_file: Path, shape: Tuple[int, int]):
    in_df = read_df(RESOURCES_PATH / in_file)
    if get_restricted_extension(in_df)
    assert equal_df(out_df, filtered_df)
