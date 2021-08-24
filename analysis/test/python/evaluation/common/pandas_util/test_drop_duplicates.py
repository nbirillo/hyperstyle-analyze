from pathlib import Path

import pytest
from analysis.src.python.evaluation.common.pandas_util import drop_duplicates, equal_df, get_solutions_df_by_file_path
from analysis.test.python.evaluation import PANDAS_UTIL_DIR_PATH
from analysis.src.python.evaluation.common.util import get_in_and_out_list

RESOURCES_PATH = PANDAS_UTIL_DIR_PATH / 'drop_duplicates'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test(in_file: Path, out_file: Path):
    in_df = get_solutions_df_by_file_path(in_file)
    out_df = get_solutions_df_by_file_path(out_file)
    filtered_df = drop_duplicates(in_df)
    assert equal_df(out_df, filtered_df)
