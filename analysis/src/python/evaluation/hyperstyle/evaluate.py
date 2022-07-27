import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluation_args import configure_arguments
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleNewFormatReport, HyperstyleReport
from analysis.src.python.evaluation.utils.evaluation_utils import evaluate_by_language, evaluate_by_solution
from analysis.src.python.evaluation.utils.solutions_saving_utils import get_solution_id_by_file_path
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import get_output_filename, get_output_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

HYPERSTYLE_OUTPUT_SUFFIX = '_hyperstyle'


def parse_hyperstyle_new_format_result(results_path: Path) -> pd.DataFrame:
    """ Parse results for group of solution and split by solution id. """

    results_dict = {
        SubmissionColumns.ID.value: [],
        SubmissionColumns.HYPERSTYLE_ISSUES.value: [],
    }

    try:
        with open(results_path, 'r') as f:
            hyperstyle_report = HyperstyleNewFormatReport.from_str(f.read())

        for file_report in hyperstyle_report.file_review_results:
            solution_id = get_solution_id_by_file_path(file_report.file_name)
            results_dict[SubmissionColumns.ID.value].append(solution_id)

            issues = file_report.to_hyperstyle_report().to_str()
            results_dict[SubmissionColumns.HYPERSTYLE_ISSUES.value].append(issues)

    except Exception as e:
        logging.error(f"Can not parse new format report from hyperstyle output: {e}")

    return pd.DataFrame.from_dict(results_dict)


def parse_hyperstyle_result(results_path: Path) -> pd.Series:
    """ Parse result for single solution. """

    result = ''

    try:
        with open(results_path, 'r') as f:
            hyperstyle_report = HyperstyleReport.from_str(f.read())
            result = hyperstyle_report.to_str()

    except Exception as e:
        logging.error(f"Can not parse new format report from hyperstyle output: {e}")

    return pd.Series({SubmissionColumns.HYPERSTYLE_ISSUES.value: result})


def evaluate_hyperstyle(df_solutions: pd.DataFrame, config: HyperstyleEvaluationConfig) -> pd.DataFrame:
    """ Run hyperstyle tool on solutions. """

    if config.new_format:
        df_solutions = evaluate_by_language(df_solutions, config, parse_hyperstyle_new_format_result)
    else:
        df_solutions = evaluate_by_solution(df_solutions, config, parse_hyperstyle_result)
    return df_solutions


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    start = time.time()
    args = parser.parse_args()

    df_solutions = read_df(args.solutions_file_path)
    config = HyperstyleEvaluationConfig(docker_path=None if args.docker_path == 'None' else args.docker_path,
                                        tool_path=args.tool_path,
                                        allow_duplicates=args.allow_duplicates,
                                        with_all_categories=args.with_all_categories,
                                        # new_format is True for batching evaluation
                                        new_format=True)

    logger.info('Start processing:')
    results = evaluate_hyperstyle(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
