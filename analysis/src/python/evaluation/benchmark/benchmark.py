import argparse
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Optional, Set

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


def get_tool_config(analyzer: Optional[Analyzer],
                    n_cpu: Optional[int],
                    tmp_path: Path,
                    cache_path: Optional[Path],
                    profile_path: Optional[Path],
                    profile_name: Optional[str]):
    if analyzer == Analyzer.HYPERSTYLE:
        return HyperstyleEvaluationConfig(
            docker_path=HYPERSTYLE_DOCKER_PATH,
            tool_path=HYPERSTYLE_TOOL_PATH,
            allow_duplicates=False,
            with_all_categories=False,
            new_format=False,
            n_cpu=n_cpu,
            tmp_path=tmp_path,
        )
    if analyzer == Analyzer.QODANA:
        return QodanaEvaluationConfig(tmp_path=tmp_path,
                                      cache_path=cache_path,
                                      profile_path=profile_path,
                                      profile_name=profile_name)

    raise NotImplementedError(f'Config for {analyzer} is not implemented.')


def get_tool_parser(analyzer: Optional[Analyzer]):
    if analyzer == Analyzer.HYPERSTYLE:
        return parse_hyperstyle_result
    if analyzer == Analyzer.QODANA:
        return parse_qodana_result

    raise NotImplementedError(f'Config for {analyzer} is not implemented.')


def time_benchmark_row(
        row: pd.Series,
        analyzer: Optional[Analyzer],
        repeat: int,
        aggregate: AggregateFunction,
        n_cpu: Optional[int],
        tmp_path: Path,
        cache_path: Optional[Path],
        profile_path: Optional[Path],
        profile_name: Optional[str],
        empty_project: bool,
) -> float:
    submission_id = row[SubmissionColumns.ID.value]
    logger.info(f'Benchmarking {submission_id} ...')

    tmp_path = tmp_path / f'submission_{submission_id}'
    config = get_tool_config(analyzer=analyzer, n_cpu=n_cpu, tmp_path=tmp_path,
                             cache_path=cache_path, profile_path=profile_path, profile_name=profile_name)
    parser = get_tool_parser(analyzer=analyzer)

    language_version = get_language_version(row[SubmissionColumns.LANG.value])
    aggregate_function = aggregate.to_function()
    attempt_times = []

    for i in range(repeat):
        logger.info(f'Time measuring attempt={i + 1}')
        input_path = create_directory(config.tmp_path / f'input_{submission_id}_{i}', clear=True)
        output_path = create_directory(config.tmp_path / f'output_{submission_id}_{i}', clear=True)

        if empty_project and config.with_template:
            logger.info('Save only project template to files ...')
            save_template_to_files(language_version, input_path)
        else:
            logger.info('Save solution with project template to files ...')
            save_solutions_to_files(row.to_frame().T, language_version, input_path, config.with_template)

        command = config.build_command(input_path, output_path, language_version)
        logger.info('Command: ' + (' '.join(command)))

        start_time = time.time()
        run_in_subprocess(command)
        end_time = time.time()

        attempt_time = end_time - start_time
        logger.info(f'Time: {attempt_time}')
        attempt_times.append(attempt_time)

        if output_path is not None and parser is not None:
            logger.info(parser(output_path / config.result_path))

    result_time = aggregate_function(attempt_times)
    logger.info(f'Result time: {result_time}')

    return result_time


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file with submissions.')

    parser.add_argument('output_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file where to save submissions with timings.')

    parser.add_argument('--analyzer', type=str, required=True, choices=Analyzer.values(),
                        help='Name of the analyzer that needs to be benchmarked.')

    parser.add_argument('--repeat', type=int, default=3, help='Times to repeat time evaluation for averaging.')

    parser.add_argument('--aggregate', type=str, default=AggregateFunction.MEAN.value,
                        choices=AggregateFunction.values(),
                        help='The function that will be used to aggregate the values from the different iterations.')

    parser.add_argument('--n-cpu', type=int, help='Number of cpu that can be used to run analyzer.')

    parser.add_argument('--log-path', type=lambda value: Path(value).absolute(), help='Path to log file')

    parser.add_argument('--tmp-path', type=lambda value: Path(value).absolute(), default=get_tmp_directory(),
                        help='The path to the directory with the temporary files.')

    parser.add_argument('--cache-path',
                        type=lambda value: None if value is None else Path(value).absolute(),
                        default=None)

    parser.add_argument('--profile-path',
                        type=lambda value: None if value is None else Path(value).absolute(),
                        default=None)

    parser.add_argument('--profile-name', type=str, default=None,
                        help='Name of profile to run qodana inspections from.')

    parser.add_argument('--empty-project', action='store_true', help='Run on empty project.')


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
                                                             cache_path=args.cache_path,
                                                             profile_path=args.profile_path,
                                                             profile_name=args.profile_name,
                                                             empty_project=args.empty_project,
                                                             axis=1)

    write_df(submissions, args.output_path)


if __name__ == '__main__':
    main()
