from argparse import Namespace
from pathlib import Path

import pytest

from analysis.src.python.evaluation.hyperstyle.evaluate import run_evaluation
from analysis.src.python.evaluation.hyperstyle.evaluation_args import HYPERSTYLE_DOCKER_PATH, HYPERSTYLE_TOOL_PATH
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.evaluation.utils.args_util import get_in_and_out_list
from analysis.src.python.utils.df_utils import equal_df, read_df, write_df
from analysis.test.python.evaluation import HYPERSTYLE_DIR_PATH

RESOURCES_PATH = HYPERSTYLE_DIR_PATH / 'evaluation'

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test(in_file: Path, out_file: Path):
    in_df = read_df(in_file)

    testing_arguments = Namespace(docker_path=HYPERSTYLE_DOCKER_PATH,
                                  tool_path=HYPERSTYLE_TOOL_PATH,
                                  allow_duplicates=False,
                                  with_all_categories=False,
                                  )

    testing_config = HyperstyleEvaluationConfig(testing_arguments)
    inspected_df = run_evaluation(in_df, testing_config)
    write_df(inspected_df, out_file)
    out_df = read_df(out_file)
    assert equal_df(out_df, inspected_df)
