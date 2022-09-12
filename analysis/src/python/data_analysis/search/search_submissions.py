import argparse
import logging
import os
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepsStatsColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code, split_code_to_lines
from analysis.src.python.evaluation.tools.model.report import BaseIssue
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.evaluation.tools.utils.saving_utils import save_solution_to_file
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import AnalysisExtension, create_directory
from analysis.src.python.utils.logging_utils import configure_logger


def write_submissions_to_files(df_submissions: pd.DataFrame, output_dir: str):
    """ Save submission to file with extension. Easy to compare diffs. """

    output_dir = create_directory(output_dir)
    output_file = output_dir / f'submissions{AnalysisExtension.CSV.value}'
    write_df(df_submissions, output_file)

    df_submissions.apply(save_solution_to_file, input_path=output_dir, axis=1)


def get_comment_to_code_line(issue: BaseIssue) -> str:
    """ Add comment to given code line. """

    return f' // {issue.get_name()} line={issue.get_line_number()} offset={issue.get_column_number()}'


def add_issue_info_comment_to_code(submission: pd.Series, issues_column: str, issue_name: str) -> pd.Series:
    """ Add comment to row where specific issue appears in solution. """

    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])

    report = parse_report(submission, issues_column)
    for issue in report.get_issues():
        if issue.get_name() == issue_name:
            code_lines[issue.get_line_number() - 1] += get_comment_to_code_line(issue)

    submission[SubmissionColumns.CODE.value] = merge_lines_to_code(code_lines)

    return submission


def search_submissions_by_step_issue(df_submissions: pd.DataFrame, issues_column: str, step: int, issue_name: str,
                                     count: int, output_dir: str):
    """
    Search and save to `output_dir` examples of submissions for given `step`
    with and without given `issue_name`.
    """

    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID.value] == step]

    def check_contains_issue(submission: pd.Series):
        report = parse_report(submission, issues_column)
        return report.has_issue(issue_name)

    df_submissions_with_issue = df_submissions[df_submissions.apply(check_contains_issue, axis=1)].head(count)
    df_submissions_with_issue = df_submissions_with_issue.apply(add_issue_info_comment_to_code,
                                                                issues_column=issues_column,
                                                                issue_name=issue_name,
                                                                axis=1)

    df_submissions_without_issue = df_submissions[~df_submissions.apply(check_contains_issue, axis=1)].head(count)

    step_issue_output_dir = os.path.join(output_dir, f'{issue_name}_{step}_{count}')
    write_submissions_to_files(df_submissions_with_issue, os.path.join(step_issue_output_dir, 'with_issue'))
    write_submissions_to_files(df_submissions_without_issue, os.path.join(step_issue_output_dir, 'without_issue'))


def search_submissions(submissions_path: str, issues_column: str, steps_issues_path: str, step: int, issue_name: str,
                       count: int, output_dir: str):
    """
    Search and save to `output_dir` examples of steps submissions with and without issue.
    Pairs of step and issue can be provided directly or listed in `steps_issues_path` csv file.
    """

    create_directory(output_dir)
    df_submissions = read_df(submissions_path)

    if steps_issues_path is None:
        search_submissions_by_step_issue(df_submissions, issues_column, step, issue_name, count, output_dir)
    else:
        df_issues_steps = read_df(steps_issues_path)
        df_issues_steps.apply(lambda row: search_submissions_by_step_issue(df_submissions,
                                                                           issues_column,
                                                                           row[SubmissionColumns.STEP_ID.value],
                                                                           row[StepsStatsColumns.ISSUE.value],
                                                                           count,
                                                                           output_dir), axis=1)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('output_dir', type=str, help='Path to directory with output')
    parser.add_argument('issues_type', type=str, help='Type of issue to analyse',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--steps-issues-path', type=str, default=None,
                        help='Path to .csv file with pairs fo steps and issues for examples finding')
    parser.add_argument('--issue-name', type=str, default=None, help='Issue example to search for')
    parser.add_argument('--step', type=int, default=None, help='Step to search submissions for')
    parser.add_argument('--count', type=int, default=5, help='Size of search output')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.output_dir, 'search', args.log_path)

    search_submissions(args.submissions_path,
                       args.issues_type,
                       args.steps_issues_path,
                       args.step,
                       args.issue_name,
                       args.count,
                       args.output_dir)
