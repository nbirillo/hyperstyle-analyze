import argparse
import logging
import random
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import get_code_with_issue_comment
from analysis.src.python.evaluation.tools.utils.saving_utils import save_submission_series_to_files
from analysis.src.python.utils.df_utils import filter_df_by_single_value, read_df
from analysis.src.python.utils.file_utils import create_directory
from analysis.src.python.utils.logging_utils import configure_logger


def search_submission_series(df_submission: pd.DataFrame, total_attempts: int, count: int) -> List[pd.DataFrame]:
    """ Build submissions series groups and select first `count` with `total_attempts` attempts. """

    df_submission_with_attempts = filter_df_by_single_value(df_submission,
                                                            SubmissionColumns.TOTAL_ATTEMPTS.value,
                                                            total_attempts)

    df_submission_series = df_submission_with_attempts.groupby(
        [SubmissionColumns.USER_ID.value, SubmissionColumns.STEP_ID.value])

    submission_series_list = list(df_submission_series)
    logging.info(f'Found {len(submission_series_list)} series with total attempts {total_attempts}')

    return random.sample(submission_series_list, min(len(submission_series_list), count))


def main(submission_path: str, issues_column: str, total_attempts: int, count: int, result_path: str):
    df_submission = read_df(submission_path)
    submission_series_list = search_submission_series(df_submission, total_attempts, count)

    result_path = create_directory(result_path)

    for _, submission_series in submission_series_list:
        submission_series[SubmissionColumns.CODE.value] = \
            submission_series.apply(get_code_with_issue_comment, issues_column=issues_column, axis=1)
        save_submission_series_to_files(submission_series, result_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submission_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('results_path', type=str, help='Path to directory where to save submission series')
    parser.add_argument('issues_column', type=str, help='Issue column name to add issues comment',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--total-attempts', type=int, help='Issue example to search for')
    parser.add_argument('--count', type=int, default=1, help='Step to search templates for')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    configure_logger(args.results_path, 'search', args.log_path)

    main(args.submission_path,
         args.issues_column,
         args.total_attempts,
         args.count,
         args.results_path)
