from pathlib import Path

import pytest

from analysis.src.python.utils.df_utils import append_df, equal_df, read_df, write_df
from analysis.src.python.utils.extension_utils import AnalysisExtension, get_restricted_extension
from analysis.src.python.utils.file_utils import remove_file
from analysis.test.python.utils import DF_UTILS_DATA_FOLDER

RESOURCES_PATH = DF_UTILS_DATA_FOLDER / 'append_df'


@pytest.mark.parametrize('in_file', ['in_1.csv', 'in_2.xlsx'])
def test(in_file: Path):
    in_df = read_df(RESOURCES_PATH / in_file)

    ext = get_restricted_extension(in_file, [AnalysisExtension.CSV, AnalysisExtension.XLSX])
    tmp_file_path = RESOURCES_PATH / f'tmp{ext.value}'
    remove_file(tmp_file_path)
    write_df(in_df, tmp_file_path)
    append_df(in_df, tmp_file_path)
    out_df = read_df(tmp_file_path)
    remove_file(tmp_file_path)

    assert in_df.shape[0] * 2 == out_df.shape[0]
    assert equal_df(in_df, out_df.head(in_df.shape[0]))
    assert equal_df(in_df, out_df.tail(in_df.shape[0]))
