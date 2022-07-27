import argparse
from pathlib import Path

from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('-o', '--output-path',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to the directory where to save evaluation results')

    parser.add_argument('--with-custom-profile',
                        help='Run qodana only in inspections listed in language specific profile.xml',
                        action='store_true')

    parser.add_argument('-dp', '--tmp-directory',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to tmp directory to save temporary files')
