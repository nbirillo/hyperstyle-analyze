import argparse
import sys
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.search.search_submissions import add_issue_info_comment_to_code
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import filter_df_by_single_value, merge_dfs, read_df, write_df
from analysis.src.python.utils.file_utils import create_file


def save_submission_series_to_files(submission_series: pd.DataFrame,
                                    submission_series_path: str,
                                    issue_name: str,
                                    first_attempt_with_issue: bool,
                                    last_attempt_with_issue: bool
                                    ):
    first = 'true' if first_attempt_with_issue else 'false'
    last = 'true' if last_attempt_with_issue else 'false'
    base_dir_path = Path(submission_series_path) / f'{issue_name}_{first}_{last}'

    for i, submission in submission_series.iterrows():
        submission = add_issue_info_comment_to_code(submission, 'hyperstyle_issues', issue_name)
        lang = submission[SubmissionColumns.LANG.value]
        extension = get_language_version(lang).extension_by_language()
        attempt = submission[SubmissionColumns.ATTEMPT.value]
        submission_id = submission[SubmissionColumns.ID.value]
        step_id = submission[SubmissionColumns.STEP_ID.value]
        code = submission[SubmissionColumns.CODE.value]
        group = submission[SubmissionColumns.GROUP.value]

        file_name = f'code_{step_id}_{attempt}_{submission_id}{extension.value}'
        file_path = base_dir_path / f'{step_id}_{group}'
        next(create_file(file_path / file_name, content=code))

    write_df(submission_series, base_dir_path / f'{step_id}_{group}' / 'submission.csv')


def check_submission_series_match(submission_series: pd.DataFrame,
                                  issue_name: str,
                                  first_attempt_with_issue: bool,
                                  last_attempt_with_issue: bool) -> bool:
    first_attempt = submission_series[submission_series[SubmissionColumns.ATTEMPT.value] == 1].iloc[0]
    last_attempt = submission_series[submission_series[SubmissionColumns.ATTEMPT.value] ==
                                     submission_series[SubmissionColumns.TOTAL_ATTEMPTS.value]].iloc[0]

    return (first_attempt[issue_name] > 0) == first_attempt_with_issue and \
           (last_attempt[issue_name] > 0) == last_attempt_with_issue


def main(submission_path: str,
         submission_issues_path: str,
         submission_series_path: str,
         issue_name: str,
         step_id: str,
         first_attempt_with_issue: bool,
         last_attempt_with_issue: bool):
    df_submission = read_df(submission_path)
    df_submission_issues = read_df(submission_issues_path)

    if step_id is not None:
        df_submission = filter_df_by_single_value(df_submission, SubmissionColumns.STEP_ID.value, step_id)

    df_submission = df_submission[df_submission[SubmissionColumns.TOTAL_ATTEMPTS.value] > 1]
    df_submission = merge_dfs(df_submission, df_submission_issues[[SubmissionColumns.ID.value, issue_name]],
                              left_on=SubmissionColumns.ID.value,
                              right_on=SubmissionColumns.ID.value)

    df_submission_groups = df_submission.groupby([SubmissionColumns.USER_ID.value, SubmissionColumns.STEP_ID.value])

    count = 0
    for _, g in df_submission_groups:
        if check_submission_series_match(g, issue_name=issue_name,
                                         first_attempt_with_issue=first_attempt_with_issue,
                                         last_attempt_with_issue=last_attempt_with_issue):
            save_submission_series_to_files(g, submission_series_path=submission_series_path,
                                            issue_name=issue_name,
                                            first_attempt_with_issue=first_attempt_with_issue,
                                            last_attempt_with_issue=last_attempt_with_issue)
            count += 1
        if count == 5:
            return

    print(count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submission_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('submission_issues_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('submission_series_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('issue_name', type=str, help='')
    parser.add_argument('--step_id', type=int, default=None, help='')
    parser.add_argument('--first_attempt_with_issue', action='store_true', help='')
    parser.add_argument('--last_attempt_with_issue', action='store_true', help='')

    args = parser.parse_args(sys.argv[1:])

    main(args.submission_path,
         args.submission_issues_path,
         args.submission_series_path,
         args.issue_name,
         args.step_id,
         args.first_attempt_with_issue,
         args.last_attempt_with_issue)
