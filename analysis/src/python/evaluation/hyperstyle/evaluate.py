import argparse
import logging
import sys
import time

import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluation_args import configure_arguments
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.evaluation.hyperstyle.utils.parsing_utils import dump_hyperstyle_file_report, \
    parse_hyperstyle_report
from analysis.src.python.evaluation.utils.evaluation_utils import save_solution_to_file
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_output_filename, get_output_path, \
    remove_directory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

HYPERSTYLE_OUTPUT_SUFFIX = '_hyperstyle'


def evaluate_by_lang(df_solutions: pd.DataFrame, lang: str, config: HyperstyleEvaluationConfig):
    """ Run hyperstyle tool on directory with solutions written on same language version. """

    language_version = get_language_version(lang)
    # Directory to inspect is tmp_directory/LANGUAGE_VERSION
    solution_dir_path = config.tmp_directory / language_version.value
    create_directory(solution_dir_path)

    # Solutions are saved to tmp_directory/LANGUAGE_VERSION/SOLUTION_ID/code.EXT
    df_solutions.apply(save_solution_to_file, dst_directory=solution_dir_path, axis=1)

    logger.info(f"Start inspecting solutions with language {language_version.value}")
    start = time.time()

    command = config.build_command(solution_dir_path, language_version)
    logger.info('Executing command' + (' '.join(command)))
    results = run_in_subprocess(command)

    end = time.time()
    logger.info(f"Finish inspecting solutions with language {language_version.value} "
                f"time={end - start}s "
                f"output={len(results)}")

    remove_directory(solution_dir_path)
    return results


def merge_results_with_solutions(df_solutions: pd.DataFrame, results: str) -> pd.DataFrame:
    """ Parse results for batch of solution and merge each solution with its result. """

    hyperstyle_report = parse_hyperstyle_report(results)
    results_to_solutions = {
        SubmissionColumns.ID.value: [],
        SubmissionColumns.HYPERSTYLE_ISSUES.value: [],
    }
    for file_report in hyperstyle_report.file_review_results:
        # As solution path is SOLUTION_ID/code.EXT
        solution_id = int(file_report.file_name.split('/')[0])
        results_to_solutions[SubmissionColumns.ID.value].append(solution_id)

        issues = dump_hyperstyle_file_report(file_report)
        results_to_solutions[SubmissionColumns.HYPERSTYLE_ISSUES.value].append(issues)

    df_results_to_solutions = pd.DataFrame.from_dict(results_to_solutions)

    return merge_dfs(df_solutions, df_results_to_solutions,
                     left_on=SubmissionColumns.ID.value,
                     right_on=SubmissionColumns.ID.value,
                     )


def evaluate(df_solutions: pd.DataFrame, config: HyperstyleEvaluationConfig) -> pd.DataFrame:
    """ All solutions are grouped by language version and inspected by groups by hyperstyle tool. """

    solutions_with_results = []
    for lang, df_lang_solutions in df_solutions.groupby(SubmissionColumns.LANG.value):
        results = evaluate_by_lang(df_lang_solutions, lang, config)
        solutions_with_results.append(merge_results_with_solutions(df_lang_solutions, results))

    df_solutions_with_results = pd.concat(solutions_with_results)

    return df_solutions_with_results


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
                                        # new_format is True for batching evaluation
                                        new_format=True)

    logger.info(f'Start processing:')
    results = evaluate(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
