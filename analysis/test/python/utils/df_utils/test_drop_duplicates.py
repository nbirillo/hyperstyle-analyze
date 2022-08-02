from pathlib import Path

import pytest

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.utils.df_utils import drop_duplicates, equal_df, read_df
from analysis.src.python.evaluation.utils.args_utils import get_in_and_out_list
from analysis.test.python.utils import DF_UTILS_DATA_FOLDER

RESOURCES_PATH = DF_UTILS_DATA_FOLDER / 'drop_duplicates'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test(in_file: Path, out_file: Path):
    in_df = read_df(in_file)
    out_df = read_df(out_file)
    filtered_df = drop_duplicates(in_df, ColumnName.CODE.value)
    assert equal_df(out_df, filtered_df)
