import argparse
import logging
import os
import sys
import time
from pathlib import Path

import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluation_args import configure_arguments
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.evaluation.utils.pandas_util import get_language_version
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, create_file, get_output_filename, get_output_path, \
    remove_directory, \
    remove_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

HYPERSTYLE_OUTPUT_SUFFIX = '_hyperstyle'
HYPERSTYLE_TRACEBACK = f'traceback{HYPERSTYLE_OUTPUT_SUFFIX}'


def solution_to_file(df_solution: pd.DataFrame, base_directory: Path) -> Path:
    solution_id = df_solution[SubmissionColumns.ID.value]
    code = df_solution[SubmissionColumns.CODE.value]
    language = df_solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(language)

    solution_dir_path = base_directory / f'solution_{solution_id}'
    os.chmod(solution_dir_path, 0o777)
    solution_file_path = solution_dir_path / f'code{language_version.extension_by_language().value}'
    os.chmod(solution_file_path, 0o777)

    return next(create_file(solution_file_path, code))


def inspect_solution(df_solution: pd.DataFrame, config: HyperstyleEvaluationConfig):
    language = df_solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(language)

    base_directory = config.tmp_directory / language_version.value

    try:
        solution_file_path = solution_to_file(df_solution, base_directory)
        command = config.build_command(solution_dir_path, language_version)

        logger.info(f"Start processing solution {solution_id}")
        start = time.time()
        logger.info('Executing command' + (' '.join(command)))

        results = run_in_subprocess(command)

        end = time.time()
        logger.info(f"Finish processing solution {solution_id} time={end - start}s output={len(results)}")

        remove_file(solution_file_path)
        remove_directory(solution_dir_path)

    except Exception as e:
        logger.error(e)
        return ''

    return results


def run_evaluation(df_solutions: pd.DataFrame, config: HyperstyleEvaluationConfig):
    df_solutions[HYPERSTYLE_TRACEBACK] = df_solutions.apply(inspect_solution, axis=1, config=config)
    return df_solutions


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    start = time.time()
    args = parser.parse_args()

    df_solutions = read_df(args.solutions_file_path)
    config = HyperstyleEvaluationConfig(docker_path=args.docker_path,
                                        tool_path=args.tool_path,
                                        allow_duplicates=args.allow_duplicates,
                                        with_all_categories=args.with_all_categories,
                                        )

    logger.info(f'Start processing:')
    results = run_evaluation(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
