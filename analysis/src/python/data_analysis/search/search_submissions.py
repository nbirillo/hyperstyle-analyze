import argparse
import logging
import os
import sys
from typing import List

import pandas as pd
from hyperstyle.src.python.review.common.file_system import Extension

from analysis.src.python.data_analysis.model.column_name import StepsStatsColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger
from analysis.src.python.data_analysis.utils.parsing_utils import parse_qodana_issues_to_objects, \
    parse_raw_issues_to_objects
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, create_directory


def write_submissions_to_files(df_submissions: pd.DataFrame, output_dir: str):
    """ Save submission to file with extension. Easy to compare diffs. """

    create_directory(output_dir)
    output_file = os.path.join(output_dir, f'submissions{AnalysisExtension.CSV.value}')
    write_df(df_submissions, output_file)

    for _, submission in df_submissions.iterrows():
        file_path = os.path.join(output_dir, f'{submission[SubmissionColumns.ID.value]}{Extension.JAVA.value}')
        with open(file_path, 'w+') as f:
            f.write(submission[SubmissionColumns.CODE.value])


def split_code_to_lines(submission: pd.DataFrame) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without /r). """

    return submission[SubmissionColumns.CODE.value].replace('\r', '').split('\n')


def merge_lines_to_code(code_lines: List[str]) -> str:
    """ Merge lines to code. """

    return '\n'.join(code_lines)


def get_comment_to_code_line(issue: str, line: int, col: int) -> str:
    """ Add comment to given code line. """

    return f' // {issue} line={line} col={col}'


def add_raw_issue_info_comment_to_code(submission: pd.DataFrame, issue: str) -> pd.DataFrame:
    """ Add comment to row where specific raw issue appears in solution. """

    code_lines = split_code_to_lines(submission)
    raw_issues = parse_raw_issues_to_objects(submission[SubmissionColumns.RAW_ISSUES.value])
    for raw_issue in raw_issues:
        if raw_issue.origin_class == issue:
            code_lines[raw_issue.line_no - 1] += get_comment_to_code_line(raw_issue.origin_class,
                                                                          raw_issue.line_no,
                                                                          raw_issue.column_no)
    submission[SubmissionColumns.CODE.value] = merge_lines_to_code(code_lines)
    return submission


def add_qodana_issue_info_comment_to_code(submission: pd.DataFrame, issue: str) -> pd.DataFrame:
    """ Add comment to row where specific qodana issue appears in solution. """

    code_lines = split_code_to_lines(submission)
    qodana_issues = parse_qodana_issues_to_objects(submission[SubmissionColumns.QODANA_ISSUES.value])
    for qodana_issue in qodana_issues:
        if qodana_issue.problem_id == issue:
            code_lines[qodana_issue.line - 1] += get_comment_to_code_line(qodana_issue.problem_id,
                                                                          qodana_issue.line,
                                                                          qodana_issue.offset)
    submission[SubmissionColumns.CODE.value] = merge_lines_to_code(code_lines)
    return submission


def search_submissions_by_step_issue(df_submissions: pd.DataFrame, issues_type: str, step: int, issue: str, count: int,
                                     output_dir: str):
    """ Search and save to `output_dir` examples of submissions for given `step` with and without given `issue`. """

    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID.value] == step]

    issue_column = SubmissionColumns(issues_type).value
    if issue_column == SubmissionColumns.QODANA_ISSUES.value:
        add_comment_to_code = add_qodana_issue_info_comment_to_code
    else:
        add_comment_to_code = add_raw_issue_info_comment_to_code

    df_submissions_with_issue = df_submissions[df_submissions[issue_column].str.contains(issue)].head(count)
    df_submissions_with_issue = df_submissions_with_issue.apply(add_comment_to_code, axis=1, issue=issue)

    df_submissions_without_issue = df_submissions[
        ~df_submissions[issue_column].str.contains(issue)] \
        .head(count)

    step_issue_output_dir = os.path.join(output_dir, f'{issue}_{step}_{count}')
    write_submissions_to_files(df_submissions_with_issue, os.path.join(step_issue_output_dir, 'with_issue'))
    write_submissions_to_files(df_submissions_without_issue, os.path.join(step_issue_output_dir, 'without_issue'))


def search_submissions(submissions_path: str, issues_type: str, steps_issues_path: str, step: int, issue: str,
                       count: int, output_dir: str):
    """ Search and save to `output_dir` examples of steps submissions with and without issue.
    Pairs of step and issue can be provided directly or listed in `steps_issues_path` csv file. """

    create_directory(output_dir)
    df_submissions = read_df(submissions_path)

    if steps_issues_path is None:
        search_submissions_by_step_issue(df_submissions, issues_type, step, issue, count, output_dir)
    else:
        df_issues_steps = read_df(steps_issues_path)
        for _, row in df_issues_steps.iterrows():
            search_submissions_by_step_issue(df_submissions,
                                             issues_type,
                                             row[SubmissionColumns.STEP_ID.value],
                                             row[StepsStatsColumns.ISSUE.value],
                                             count, output_dir)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('output_dir', type=str, help='Path to directory with output')
    parser.add_argument('issues_type', type=str, help='Type of issue to analyse',
                        choices=[SubmissionColumns.RAW_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--steps-issues-path', type=str, default=None,
                        help='Path to .csv file with pairs fo steps and issues for examples finding')
    parser.add_argument('--issue', type=str, default=None, help='Issue example to search for')
    parser.add_argument('--step', type=int, default=None, help='Step to search submissions for')
    parser.add_argument('--count', type=int, default=5, help='Size of search output')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.output_dir, 'search', args.log_path)

    search_submissions(args.submissions_path,
                       args.issues_type,
                       args.steps_issues_path,
                       args.step,
                       args.issue,
                       args.count,
                       args.output_dir)
