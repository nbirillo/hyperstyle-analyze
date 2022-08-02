from pathlib import Path

import pytest

from analysis.src.python.evaluation.hyperstyle.evaluate import evaluate_hyperstyle
from analysis.src.python.evaluation.utils.args_utils import get_in_and_out_list
from analysis.test.python.evaluation import HYPERSTYLE_DIR_PATH
from analysis.test.python.evaluation.utils.evaluation_configs import get_default_hyperstyle_config
from analysis.test.python.evaluation.utils.evaluation_test_utils import run_evaluation_test

RESOURCES_PATH = HYPERSTYLE_DIR_PATH / 'docker_evaluation'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.skip(reason="No docker inside CI container")
@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test_with_batching(in_file: Path, out_file: Path):
    run_evaluation_test(in_file,
                        out_file,
                        get_default_hyperstyle_config(new_format=True),
                        evaluate_hyperstyle)


@pytest.mark.skip(reason="No docker inside CI container")
@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test_without_batching(in_file: Path, out_file: Path):
    run_evaluation_test(in_file,
                        out_file,
                        get_default_hyperstyle_config(),
                        evaluate_hyperstyle)
