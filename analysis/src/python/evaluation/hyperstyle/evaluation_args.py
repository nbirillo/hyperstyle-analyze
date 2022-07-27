import argparse
from pathlib import Path

from analysis.src.python.evaluation.hyperstyle.evaluation_config import HYPERSTYLE_DOCKER_PATH, HYPERSTYLE_TOOL_PATH
from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('-o', '--output-path',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to the directory where to save evaluation results')

    parser.add_argument('-dp', '--docker-path',
                        default=HYPERSTYLE_DOCKER_PATH,
                        type=str,
                        help='Path to docker (USER/NAME:VERSION) to run evaluation on. '
                             'If `None` hyperstyle will run locally.')

    parser.add_argument('-tp', '--tool-path',
                        default=HYPERSTYLE_TOOL_PATH,
                        type=str,
                        help='Path to script inside docker (or locally) to run on files.')

    parser.add_argument('--allow-duplicates',
                        help='Allow duplicate issues found by different linters. By default, duplicates are skipped.',
                        action='store_true')

    parser.add_argument('--with-all-categories',
                        help='Without this flag, all issues will be categorized into 5 main categories: '
                             'CODE_STYLE, BEST_PRACTICES, ERROR_PRONE, COMPLEXITY, INFO.',
                        action='store_true')

    parser.add_argument('-td', '--tmp-directory',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to tmp directory to save temporary files')
