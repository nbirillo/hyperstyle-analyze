import argparse
import json
import logging
import os
import sys

import pandas as pd
from hyperstyle.src.python.review.common.file_system import Extension

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger
from analysis.src.python.data_analysis.utils.parsing_utils import parse_qodana_issues_to_objects, \
    parse_raw_issues_to_objects
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, create_directory
from analysis.src.python.evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder


def write_submissions_to_files(df_submissions: pd.DataFrame, output_dir: str):
    create_directory(output_dir)
    output_file = os.path.join(output_dir, f'submissions{AnalysisExtension.CSV.value}')
    write_df(df_submissions, output_file)

    for i, submission in df_submissions.iterrows():
        file_path = os.path.join(output_dir, f'{submission[SubmissionColumns.ID.value]}{Extension.JAVA.value}')
        with open(file_path, 'w+') as f:
            f.write(submission[SubmissionColumns.CODE.value])


def add_raw_issue_info_comment_to_code(submission: pd.DataFrame, issue: str) -> pd.DataFrame:
    code_lines = submission[SubmissionColumns.CODE.value].replace('\r', '').split('\n')
    raw_issues = parse_raw_issues_to_objects(submission[SubmissionColumns.RAW_ISSUES.value])
    for raw_issue in raw_issues:
        if raw_issue.origin_class == issue:
            code_lines[raw_issue.line_no - 1] += f' // {raw_issue.origin_class} ' \
                                                 f'line={raw_issue.line_no} ' \
                                                 f'col={raw_issue.column_no}'
    submission[SubmissionColumns.CODE.value] = '\n'.join(code_lines)
    return submission


def add_qodana_issue_info_comment_to_code(submission: pd.DataFrame, issue: str) -> pd.DataFrame:
    code_lines = submission[SubmissionColumns.CODE.value].replace('\r', '').split('\n')
    qodana_issues = parse_qodana_issues_to_objects(submission[SubmissionColumns.QODANA_ISSUES.value])
    for raw_issue in raw_issues:
        if raw_issue.origin_class == issue:
            code_lines[raw_issue.line_no - 1] += f' // {raw_issue.origin_class} ' \
                                                 f'line={raw_issue.line_no} ' \
                                                 f'col={raw_issue.column_no}'
    submission[SubmissionColumns.CODE.value] = '\n'.join(code_lines)
    return submission


def search_submissions(submissions_path: str, issue: str, step: int, count: int, output_dir: str):
    output_dir = os.path.join(output_dir, f'{issue}_{step}_{count}')
    create_directory(output_dir)

    df_submissions = read_df(submissions_path)
    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID.value] == step]

    df_submissions_with_issue = df_submissions[df_submissions[SubmissionColumns.RAW_ISSUES.value].str.contains(issue)] \
        .head(count)
    df_submissions_with_issue = df_submissions_with_issue.apply(add_raw_issue_info_comment_to_code, axis=1, issue=issue)
    write_submissions_to_files(df_submissions_with_issue, os.path.join(output_dir, f'with_issue'))

    df_submissions_without_issue = df_submissions[
        ~df_submissions[SubmissionColumns.RAW_ISSUES.value].str.contains(issue)] \
        .head(count)
    write_submissions_to_files(df_submissions_without_issue, os.path.join(output_dir, f'without_issue'))


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issue', type=str, help='Issue example to search for')
    parser.add_argument('step', type=int, help='Step to search submissions for')
    parser.add_argument('output_dir', type=str, help='Path to directory with output')
    parser.add_argument('--count', type=int, default=5, help='Size of search output')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.output_dir, 'search', args.log_path)

    search_submissions(args.submissions_path,
                       args.issue,
                       args.step,
                       args.count,
                       args.output_dir)
