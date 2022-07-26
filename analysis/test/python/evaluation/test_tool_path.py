import pytest
from hyperstyle.src.python import MAIN_FOLDER

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation import XLSX_DATA_FOLDER


def test_correct_tool_path():
    config = HyperstyleEvaluationConfig(docker_path=None,
                                        tool_path=HYPERSTYLE_RUNNER_PATH,
                                        allow_duplicates=False,
                                        with_all_categories=False,
                                        new_format=True,
                                        )

    test_file = XLSX_DATA_FOLDER / 'test_unsorted_order.xlsx'
    in_df = read_df(test_file)
    evaluate_hyperstyle(in_df, config)


def test_incorrect_tool_path():
    with pytest.raises(Exception):
        config = HyperstyleEvaluationConfig(docker_path=None,
                                            tool_path=MAIN_FOLDER.parent / 'review/incorrect_path.py',
                                            allow_duplicates=False,
                                            with_all_categories=False,
                                            new_format=True,
                                            )

        test_file = XLSX_DATA_FOLDER / 'test_unsorted_order.xlsx'
        in_df = read_df(test_file)
        assert evaluate_hyperstyle(in_df, config)
