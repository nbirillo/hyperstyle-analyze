import argparse
import logging
import time
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Callable, Optional, Set

import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.tools.hyperstyle.evaluate import parse_hyperstyle_result
from analysis.src.python.evaluation.tools.hyperstyle.evaluation_config import HYPERSTYLE_DOCKER_PATH, \
    HYPERSTYLE_TOOL_PATH, \
    HyperstyleEvaluationConfig
from analysis.src.python.evaluation.tools.qodana.evaluate import parse_qodana_result
from analysis.src.python.evaluation.tools.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.src.python.evaluation.tools.utils.saving_utils import save_solutions_to_files, \
    save_template_to_files
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_tmp_directory
from analysis.src.python.utils.logging_utils import configure_logger
from analysis.src.python.utils.numpy_utils import AggregateFunction

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
    def values(cls) -> Set[str]:
        return {cls.HYPERSTYLE.value, cls.QODANA.value}


def measure_run_time(
        f: Callable[[], Any],
        repeat: int,
        aggregate: AggregateFunction = AggregateFunction.MEAN,
        output_path: Optional[Path] = None,
        parser: Optional[Callable[[Path], Any]] = None,
) -> float:
    aggregate_function = aggregate.to_function()

    repeat_times = []
    for i in range(repeat):
        logger.info(f'Time measuring attempt={i + 1}')

        start_time = time.time()
        f()
        end_time = time.time()

        difference = end_time - start_time
        logger.info(f'Time: {difference}')

        if output_path is not None and parser is not None:
            logger.info(parser(output_path))

        repeat_times.append(difference)

    return aggregate_function(repeat_times)


def time_benchmark_row(
        row: pd.Series,
        analyzer: Optional[Analyzer],
        repeat: int,
        aggregate: AggregateFunction,
        n_cpu: Optional[int],
        tmp_path: Path,
        with_custom_profile: bool,
        empty: bool,
) -> float:
    submission_id = row[SubmissionColumns.ID.value]
    tmp_path = tmp_path / f'submission_{submission_id}'

    if analyzer == Analyzer.HYPERSTYLE:
        config = HyperstyleEvaluationConfig(
            docker_path=HYPERSTYLE_DOCKER_PATH,
            tool_path=HYPERSTYLE_TOOL_PATH,
            allow_duplicates=False,
            with_all_categories=False,
            new_format=False,
            n_cpu=n_cpu,
            tmp_path=tmp_path,
        )
        parser = parse_hyperstyle_result
    elif analyzer == Analyzer.QODANA:
        config = QodanaEvaluationConfig(tmp_path=tmp_path,
                                        with_custom_profile=with_custom_profile)
        parser = parse_qodana_result
    else:
        raise NotImplementedError(f'Benchmark for {analyzer} is not implemented.')

    logger.info(f'Benchmarking {row[SubmissionColumns.ID.value]} ...')

    language_version = get_language_version(row[SubmissionColumns.LANG.value])

    input_path = create_directory(config.tmp_path / f'input_{submission_id}', clear=True)
    output_path = create_directory(config.tmp_path / f'output_{submission_id}', clear=True)

    if empty and config.with_template:
        save_template_to_files(language_version, input_path)
    else:
        save_solutions_to_files(row.to_frame().T, language_version, input_path, config.with_template)

    command = config.build_command(input_path, output_path, language_version)

    mean_time = measure_run_time(
        partial(run_in_subprocess, command=command),
        repeat,
        aggregate,
        output_path / config.result_path,
        parser,
    )

    logger.info(f'Mean time: {mean_time}')
    return mean_time


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file with submissions.')

    parser.add_argument('output_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file where to save submissions with timings.')

    parser.add_argument('--analyzer', type=str, required=True, choices=Analyzer.values(),
                        help='Name of the analyzer that needs to be benchmarked.')

    parser.add_argument('--repeat', type=int, default=3, help='Times to repeat time evaluation for averaging.')

    parser.add_argument('--empty', action='store_true', help='Run on empty project.')

    parser.add_argument('--with-custom-profile',
                        help='Run qodana only in inspections listed in language specific profile.xml',
                        action='store_true')

    parser.add_argument('--aggregate', type=str, default=AggregateFunction.MEAN.value,
                        choices=AggregateFunction.values(),
                        help='The function that will be used to aggregate the values from the different iterations.')

    parser.add_argument('--n-cpu', type=int, help='Number of cpu that can be used to run analyzer.')

    parser.add_argument('--log-path', type=lambda value: Path(value).absolute(), help='Path to log file')

    parser.add_argument('--tmp-path', type=lambda value: Path(value).absolute(), default=get_tmp_directory(),
                        help='The path to the directory with the temporary files.')


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    submissions = read_df(args.submissions_path)
    analyzer = Analyzer.from_value(args.analyzer)
    aggregate = AggregateFunction(args.aggregate)

    configure_logger(args.submissions_path, f'{args.analyzer}_benchmark', args.log_path)

    submissions[f'{args.analyzer}_time'] = submissions.apply(time_benchmark_row,
                                                             analyzer=analyzer,
                                                             repeat=args.repeat,
                                                             aggregate=aggregate,
                                                             n_cpu=args.n_cpu,
                                                             tmp_path=args.tmp_path,
                                                             with_custom_profile=args.with_custom_profile,
                                                             empty=args.empty,
                                                             axis=1)

    write_df(submissions, args.output_path)


if __name__ == '__main__':
    main()
