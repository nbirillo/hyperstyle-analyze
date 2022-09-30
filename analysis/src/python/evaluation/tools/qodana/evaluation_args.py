import argparse
from pathlib import Path

from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument
from analysis.src.python.utils.file_utils import get_tmp_directory


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('-o', '--output-path',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to the directory where to save evaluation results')

    parser.add_argument('-tp', '--tmp-path',
                        default=get_tmp_directory(),
                        type=lambda value: Path(value).absolute(),
                        help='Path to tmp directory to save temporary files')

    parser.add_argument('-pp', '--profile-path',
                        type=lambda value: None if value is None else Path(value).absolute(), default=None,
                        help='Path to inspection profile configuration')

    parser.add_argument('-cp', '--cache-path',
                        type=lambda value: None if value is None else Path(value).absolute(), default=None,
                        help='Path to directory to save caches')

    parser.add_argument('-pn', '--profile-name', type=str, default=None,
                        help='Name of default profile to run')
