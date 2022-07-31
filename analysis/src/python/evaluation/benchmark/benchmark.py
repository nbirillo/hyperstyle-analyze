import argparse
import logging
import time
from functools import partial
from pathlib import Path
from typing import Any, Callable, Literal

import numpy as np
import pandas as pd

from analysis.src.python.evaluation.hyperstyle.evaluate import parse_hyperstyle_result
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HYPERSTYLE_TOOL_PATH, HyperstyleEvaluationConfig
from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.qodana.evaluate import parse_qodana_result
from analysis.src.python.evaluation.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.src.python.evaluation.utils.evaluation_utils import evaluate
from analysis.src.python.utils.df_utils import read_df, write_df

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def measure_run_time(f: Callable[[], Any], repeat: int) -> float:
    repeat_times = []
    for i in range(1, repeat + 1):
        logger.info(f'Time measuring attempt={i}')

        start_time = time.time()
        logger.info(f())
        end_time = time.time()

        repeat_times.append(end_time - start_time)

    mean_time = np.array(repeat_times).mean()
    logger.info(f'Mean time: {mean_time}')
    return mean_time


def time_benchmark_row(
    row: pd.Series,
    docker_path: str,
    analyzer: Literal['hyperstyle', 'qodana'],
    repeat: int,
    n_cpu: int,
    tmp_directory: Path,
) -> float:
    if analyzer == 'hyperstyle':
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
    else:
        config = QodanaEvaluationConfig(tmp_directory=tmp_directory)
        parser = parse_qodana_result

    logger.info(f'Benchmarking {row[ColumnName.ID.value]}...')

    return measure_run_time(
        partial(evaluate, df_solutions=row.to_frame().T, config=config, parse_result=parser),
        repeat,
    )


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
        choices=['hyperstyle', 'qodana'],
        help='Name of the analyzer that needs to be benchmarked.',
    )

    parser.add_argument(
        '--docker-path',
        type=str,
        required=True,
        help='Path to docker (USER/NAME:VERSION) with the analyzer.',
    )

    parser.add_argument('--repeat', type=int, default=3, help='Times to repeat time evaluation for averaging.')

    parser.add_argument('--n-cpu', type=int, default=1, help='Number of cpu that can be used to run analyzer.')

    parser.add_argument(
        '--time-column',
        type=str,
        help=(
            'Name of the column where the time will be saved. '
            'By default, the time will be saved in the <analyzer_name>_time column.'
        ),
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

    submissions = read_df(args.submissions_path)
    submissions[args.time_column] = submissions.apply(
        lambda row: time_benchmark_row(row, args.docker_path, args.analyzer, args.repeat, args.n_cpu, args.tmp_dir),
        axis=1,
    )

    write_df(submissions, args.output_path)


if __name__ == '__main__':
    main()
