import argparse
import logging
import time
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Callable, Optional, Set

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluate import parse_hyperstyle_result
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HYPERSTYLE_TOOL_PATH, HyperstyleEvaluationConfig
from analysis.src.python.evaluation.qodana.evaluate import parse_qodana_result
from analysis.src.python.evaluation.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.evaluation.utils.solutions_saving_utils import save_solutions_to_files
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import create_directory

logger = logging.getLogger(__name__)


class Analyzer(Enum):
    HYPERSTYLE = 'hyperstyle'
    QODANA = 'qodana'

    @classmethod
    def from_value(cls, value: str) -> Optional['Analyzer']:
        try:
            return Analyzer(value)
        except ValueError:
            return None

    @classmethod
    def available_values(cls) -> Set[str]:
        return {cls.HYPERSTYLE.value, cls.QODANA.value}


def measure_run_time(f: Callable[[], Any], repeat: int, output_path: Path, parser: Callable[[Path], Any]) -> float:
    repeat_times = []
    for i in range(1, repeat + 1):
        logger.info(f'Time measuring attempt={i}')

        start_time = time.time()
        f()
        end_time = time.time()

        difference = end_time - start_time
        logger.info(f'Time: {difference}')
        logger.info(parser(output_path))

        repeat_times.append(difference)

    return np.array(repeat_times).mean()


def time_benchmark_row(
    row: pd.Series,
    docker_path: str,
    analyzer: Optional[Analyzer],
    repeat: int,
    n_cpu: Optional[int],
    tmp_directory: Path,
) -> float:
    if analyzer == Analyzer.HYPERSTYLE:
        config = HyperstyleEvaluationConfig(
            docker_path=docker_path,
            tool_path=HYPERSTYLE_TOOL_PATH,
            allow_duplicates=False,
            with_all_categories=False,
            new_format=False,
            n_cpu=n_cpu,
            tmp_directory=tmp_directory,
        )
        parser = parse_hyperstyle_result
    elif analyzer == Analyzer.QODANA:
        config = QodanaEvaluationConfig(tmp_directory=tmp_directory)
        parser = parse_qodana_result
    else:
        raise NotImplementedError(f'Benchmark for {analyzer} is not implemented.')

    logger.info(f'Benchmarking {row[SubmissionColumns.ID.value]} ...')

    language_version = get_language_version(row[SubmissionColumns.LANG.value])
    input_path = create_directory(config.tmp_path / 'input', clear=True)
    output_path = create_directory(config.tmp_path / 'output', clear=True)

    save_solutions_to_files(row.to_frame().T, language_version, input_path, config.with_template)

    command = config.build_command(input_path, output_path, language_version)

    mean_time = measure_run_time(
        partial(run_in_subprocess, command=command),
        repeat,
        output_path / config.result_path,
        parser,
    )

    logger.info(f'Mean time: {mean_time}')
    return mean_time


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        'output_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file where to save submissions with timings.',
    )

    parser.add_argument(
        '--analyzer',
        type=str,
        required=True,
        choices=Analyzer.available_values(),
        help='Name of the analyzer that needs to be benchmarked.',
    )

    parser.add_argument(
        '--docker-path',
        type=str,
        required=True,
        help='Path to docker (USER/NAME:VERSION) with the analyzer.',
    )

    parser.add_argument('--repeat', type=int, default=3, help='Times to repeat time evaluation for averaging.')

    parser.add_argument('--n-cpu', type=int, help='Number of cpu that can be used to run analyzer.')

    parser.add_argument(
        '--time-column',
        type=str,
        help=(
            'Name of the column where the time will be saved. '
            'By default, the time will be saved in the <analyzer_name>_time column.'
        ),
    )

    parser.add_argument(
        '--log-path',
        type=lambda value: Path(value).absolute(),
        help='Path to log file',
    )

    parser.add_argument(
        '--tmp-dir',
        type=lambda value: Path(value).absolute(),
        help='The path to the directory with the temporary files.',
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    if args.time_column is None:
        args.time_column = f'{args.analyzer}_time'

    if args.log_path is not None:
        args.log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.INFO, filename=args.log_path, filemode='w')

    submissions = read_df(args.submissions_path)
    submissions[args.time_column] = submissions.apply(
        lambda row: time_benchmark_row(
            row,
            args.docker_path,
            Analyzer.from_value(args.analyzer),
            args.repeat,
            args.n_cpu,
            args.tmp_dir,
        ),
        axis=1,
    )

    write_df(submissions, args.output_path)


if __name__ == '__main__':
    main()
