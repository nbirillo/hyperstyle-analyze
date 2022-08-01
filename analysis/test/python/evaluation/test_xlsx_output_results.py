import pytest

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.src.python.utils.file_utils import create_directory, remove_directory
from analysis.src.python.utils.xlsx_utils import read_df_from_xlsx
from analysis.test.python.evaluation import TARGET_XLSX_DATA_FOLDER, TMP_DIR_PATH, XLSX_DATA_FOLDER

FILE_NAMES = [
    ('test_sorted_order.xlsx', 'target_sorted_order.xlsx'),
    ('test_unsorted_order.xlsx', 'target_unsorted_order.xlsx'),
]


@pytest.mark.parametrize(('test_file', 'target_file'), FILE_NAMES)
def test_correct_output(test_file: str, target_file: str):
    tmp_path = create_directory(TMP_DIR_PATH, clear=True)
    config = HyperstyleEvaluationConfig(docker_path=None,
                                        tool_path=HYPERSTYLE_RUNNER_PATH,
                                        allow_duplicates=False,
                                        with_all_categories=False,
                                        new_format=True,
                                        tmp_path=tmp_path)
    in_df = read_df(XLSX_DATA_FOLDER / test_file)
    inspected_df = evaluate_hyperstyle(in_df, config)
    out_df = read_df_from_xlsx(TARGET_XLSX_DATA_FOLDER / target_file, sheet_name='hyperstyle_issues')
    remove_directory(tmp_path)

    assert equal_df(out_df, inspected_df)
