from pathlib import Path

import pytest

from analysis.src.python.evaluation.qodana.evaluate import evaluate_qodana
from analysis.src.python.evaluation.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.src.python.evaluation.utils.args_utils import get_in_and_out_list
from analysis.src.python.utils.df_utils import equal_df, read_df, write_df
from analysis.test.python.evaluation import QODANA_DIR_PATH

RESOURCES_PATH = QODANA_DIR_PATH / 'docker_evaluation'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.skip(reason="No docker inside CI container")
@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test_with_batching(in_file: Path, out_file: Path):
    in_df = read_df(in_file)
    testing_config = QodanaEvaluationConfig()
    inspected_df = evaluate_qodana(in_df, testing_config)
    out_df = read_df(out_file)
    assert equal_df(out_df, inspected_df)
