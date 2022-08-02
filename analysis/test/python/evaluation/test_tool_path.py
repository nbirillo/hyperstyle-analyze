import pytest
from hyperstyle.src.python import MAIN_FOLDER

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation import XLSX_DATA_FOLDER
from analysis.test.python.evaluation.utils.evaluation_configs import get_default_hyperstyle_config


def test_correct_tool_path():
    in_df = read_df(XLSX_DATA_FOLDER / 'test_unsorted_order.xlsx')
    config = get_default_hyperstyle_config(docker_path=None,
                                           tool_path=HYPERSTYLE_RUNNER_PATH)
    evaluate_hyperstyle(in_df, config)


def test_incorrect_tool_path():
    with pytest.raises(Exception):
        in_df = read_df(XLSX_DATA_FOLDER / 'test_unsorted_order.xlsx')
        config = get_default_hyperstyle_config(docker_path=None,
                                               tool_path=MAIN_FOLDER.parent / 'review/incorrect_path.py')
        assert evaluate_hyperstyle(in_df, config)
