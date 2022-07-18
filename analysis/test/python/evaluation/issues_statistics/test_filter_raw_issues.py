from pathlib import Path

import pytest

from analysis.src.python.evaluation.issues_statistics.filter_raw_issues import filter_raw_issues
from analysis.src.python.evaluation.utils.args_utils import get_in_and_out_list
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.test.python.evaluation import ISSUES_STATISTICS_DIR_PATH

RESOURCES_PATH = ISSUES_STATISTICS_DIR_PATH / 'filter_raw_issues'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test(in_file: Path, out_file: Path):
    in_df = read_df(in_file)

    filtered_df = filter_raw_issues(in_df)
    out_df = read_df(out_file)
    assert equal_df(out_df, filtered_df)
