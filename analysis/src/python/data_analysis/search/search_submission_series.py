import argparse
import logging
import sys
from pathlib import Path
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.search.utils.comment_utils import add_issues_comments_to_code
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import filter_df_by_single_value, read_df
from analysis.src.python.utils.file_utils import create_file
from analysis.src.python.utils.logging_utils import configure_logger


def save_submission_series_to_files(submission_series: pd.DataFrame,
                                    submission_series_path: str,
                                    issues_column: str):
    """ Save submission series to files. """

    for i, submission in submission_series.iterrows():
        add_issues_comments_to_code(submission, issues_column)
        lang = submission[SubmissionColumns.LANG.value]
        extension = get_language_version(lang).extension_by_language()
        attempt = submission[SubmissionColumns.ATTEMPT.value]
        step_id = submission[SubmissionColumns.STEP_ID.value]
        user_id = submission[SubmissionColumns.USER_ID.value]
        code = submission[SubmissionColumns.CODE.value]

        file_name = f'attempt_{attempt}{extension.value}'
        file_path = Path(submission_series_path) / f'user_{user_id}' / f'step_{step_id}'
        next(create_file(file_path / file_name, content=code))


def search_submission_series(df_submission: pd.DataFrame, total_attempts: int, count: int) -> List[pd.DataFrame]:
    """ Build submissions series groups and select first `count` with `total_attempts` attempts. """

    df_submission_with_attempts = filter_df_by_single_value(df_submission,
                                                            SubmissionColumns.TOTAL_ATTEMPTS.value,
                                                            total_attempts)

    df_submission_series = df_submission_with_attempts.groupby(
        [SubmissionColumns.USER_ID.value, SubmissionColumns.STEP_ID.value])

    submission_series_list = list(df_submission_series)
    logging.info(f'Found {len(submission_series_list)} series with total attempts {total_attempts}')

    return submission_series_list[:count]


def main(submission_path: str, issues_column: str, total_attempts: int, count: int, submission_series_path: str):
    df_submission = read_df(submission_path)
    submission_series_list = search_submission_series(df_submission, total_attempts, count)

    for _, submission_series in submission_series_list:
        save_submission_series_to_files(submission_series, submission_series_path, issues_column)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submission_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('submission_series_path', type=str, help='Path to directory where to save submission series')
    parser.add_argument('issues_column', type=str, help='Issue column name to add issues comment',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--total-attempts', type=int, help='Issue example to search for')
    parser.add_argument('--count', type=int, default=1, help='Step to search templates for')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.submission_series_path, 'search', args.log_path)

    main(args.submission_path,
         args.issues_column,
         args.total_attempts,
         args.count,
         args.submission_series_path, )
