import pytest

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.test.python.evaluation import TARGET_XLSX_DATA_FOLDER, XLSX_DATA_FOLDER
from analysis.test.python.evaluation.utils.evaluation_configs import get_default_hyperstyle_config
from analysis.test.python.evaluation.utils.evaluation_test_utils import run_evaluation_test

FILE_NAMES = [
    ('test_sorted_order.xlsx', 'target_sorted_order.xlsx'),
    ('test_unsorted_order.xlsx', 'target_unsorted_order.xlsx'),
]


@pytest.mark.parametrize(('test_file', 'target_file'), FILE_NAMES)
def test_correct_output(test_file: str, target_file: str):
    config = get_default_hyperstyle_config(
        docker_path=None,
        tool_path=HYPERSTYLE_RUNNER_PATH,
        new_format=True)

    run_evaluation_test(XLSX_DATA_FOLDER / test_file,
                        TARGET_XLSX_DATA_FOLDER / target_file,
                        config,
                        evaluate_hyperstyle)
