import pytest
from analysis.src.python.evaluation.evaluation_config import EvaluationConfig
from analysis.src.python.evaluation.evaluation_run_tool import inspect_solutions_df
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation import XLSX_DATA_FOLDER
from analysis.test.python.evaluation.testing_config import get_testing_arguments


def test_incorrect_data_path():
    with pytest.raises(FileNotFoundError):
        testing_arguments_dict = get_testing_arguments(to_add_traceback=True, to_add_tool_path=True)
        testing_arguments_dict.solutions_file_path = XLSX_DATA_FOLDER / 'do_not_exist.xlsx'
        config = EvaluationConfig(testing_arguments_dict)
        lang_code_dataframe = read_df(config.solutions_file_path)
        assert inspect_solutions_df(config, lang_code_dataframe)
