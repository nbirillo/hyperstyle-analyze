import pandas as pd
import pytest
from analysis.src.python.evaluation.evaluation_config import EvaluationConfig
from analysis.src.python.evaluation.evaluation_run_tool import get_solutions_df, inspect_solutions_df
from analysis.test.python.evaluation import TARGET_XLSX_DATA_FOLDER, XLSX_DATA_FOLDER
from analysis.test.python.evaluation.testing_config import get_testing_arguments
from analysis.src.python.evaluation.common.pandas_util import equal_df

# We don't check the full traceback since the main target is supporting csv files and edit
# xlsx files is very hard on unix laptops. However, hyperstyle often change the text of
# the issues messages and it is inconvenient to support it.
FILE_NAMES = [
    ('test_sorted_order.xlsx', 'target_sorted_order.xlsx', False),
    ('test_unsorted_order.xlsx', 'target_unsorted_order.xlsx', False),
]


@pytest.mark.parametrize(('test_file', 'target_file', 'output_type'), FILE_NAMES)
def test_correct_output(test_file: str, target_file: str, output_type: bool):

    testing_arguments_dict = get_testing_arguments(to_add_tool_path=True)
    testing_arguments_dict.solutions_file_path = XLSX_DATA_FOLDER / test_file
    testing_arguments_dict.traceback = output_type

    config = EvaluationConfig(testing_arguments_dict)
    lang_code_dataframe = get_solutions_df(config.extension, config.solutions_file_path)
    test_dataframe = inspect_solutions_df(config, lang_code_dataframe)

    sheet_name = 'grades'
    if output_type:
        sheet_name = 'traceback'
    target_dataframe = pd.read_excel(TARGET_XLSX_DATA_FOLDER / target_file, sheet_name=sheet_name)

    assert equal_df(target_dataframe, test_dataframe)
