import pytest

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation import XLSX_DATA_FOLDER

FILE_NAMES = [
    'test_wrong_column_name.xlsx',
    'test_java_no_version.xlsx',
    'test_empty_table.xlsx',
]


@pytest.mark.parametrize('file_name', FILE_NAMES)
def test_wrong_column(file_name: str):
    with pytest.raises(KeyError):
        config = HyperstyleEvaluationConfig(docker_path=None,
                                            tool_path=HYPERSTYLE_RUNNER_PATH,
                                            allow_duplicates=False,
                                            with_all_categories=False,
                                            new_format=True,
                                            )

        in_df = read_df(XLSX_DATA_FOLDER / file_name)
        assert evaluate_hyperstyle(in_df, config)
