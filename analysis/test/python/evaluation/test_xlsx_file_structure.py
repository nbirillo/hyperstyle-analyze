import pytest

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation import XLSX_DATA_FOLDER
from analysis.test.python.evaluation.utils.evaluation_configs import get_default_hyperstyle_config

FILE_NAMES = [
    'test_wrong_column_name.xlsx',
    'test_java_no_version.xlsx',
    'test_empty_table.xlsx',
]


@pytest.mark.parametrize('file_name', FILE_NAMES)
def test_wrong_column(file_name: str):
    with pytest.raises(KeyError):
        in_df = read_df(XLSX_DATA_FOLDER / file_name)
        config = get_default_hyperstyle_config(docker_path=None,
                                               tool_path=HYPERSTYLE_RUNNER_PATH,
                                               new_format=True)
        assert evaluate_hyperstyle(in_df, config)
