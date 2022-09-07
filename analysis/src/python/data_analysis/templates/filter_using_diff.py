import argparse
import sys
from typing import List, Tuple

import pandas as pd
from diff_match_patch import diff_match_patch

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns
from analysis.src.python.data_analysis.templates.utils.template_utils import parse_template_code_from_step
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.evaluation.tools.model.report import BaseIssue, BaseReport
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_issues_with_offset(report: BaseReport, code_lines: List[str]) -> List[Tuple[int, BaseIssue]]:
    """ For each issue calculate offset in code written in one line and return as pairs sorted in ascending order."""

    code_prefix_length = [0]
    for code_line in code_lines:
        code_prefix_length.append(code_prefix_length[-1] + len(code_line))

    issues_with_offset = []
    for issue in report.get_issues():
        issue_offset = code_prefix_length[issue.get_line_number() - 1] + issue.get_column_number()
        issues_with_offset.append((issue_offset, issue))

    issues_with_offset.sort(key=lambda i: i[0])

    return issues_with_offset


def get_template_to_code_diffs(template_lines: List[str], code_lines: List[str]) -> List[Tuple[int, int, int]]:
    """
    Get template to students code diff in format of list of tuples (tag, start, end) where:
    tag - type of change where 0 (code not changed), 1 (code added). Tag -1 (code deleted) is ignored.
    start - position of change start (included)
    end - position of change end (excluded)
    """

    matcher = diff_match_patch()
    patches = matcher.diff_main(''.join(template_lines), ''.join(code_lines))

    diffs = []
    start = 0

    for tag, patch in patches:
        if tag != -1:
            end = start + len(patch)
            diffs.append((tag, start, end))
            start = end

    return diffs


def get_template_issues(issues_with_offset: List[Tuple[int, BaseIssue]], diff: List[Tuple[int, int, int]]) \
        -> List[BaseIssue]:
    """
    Get template issues from list of issues.
    Issues considered as template if it's position inside change in diff with type 0 - code not changed from template.
    """

    i = 0
    template_issues = []
    for offset, issue in issues_with_offset:
        while i < len(diff) and diff[i][2] < offset:
            i += 1
        # If tag is 0 the part of code was not changed from template
        if diff[i][0] == 0:
            template_issues.append(issue)

    return template_issues


def filter_in_single_submission(submission: pd.Series, step: pd.Series, issues_column: str) -> pd.Series:
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value], keep_ends=True)
    lang = submission[SubmissionColumns.LANG.value]
    template_lines = parse_template_code_from_step(step, lang, keep_ends=True)

    report = parse_report(submission, issues_column)

    issues_with_offset = get_issues_with_offset(report, code_lines)
    diff = get_template_to_code_diffs(template_lines, code_lines)

    template_issues = get_template_issues(issues_with_offset, diff)

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[issues_column + '_diff'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[issues_column + '_all'] = report.to_json()

    return submission


def filter_template_issues_using_diff(df_submissions: pd.DataFrame, df_steps: pd.DataFrame,
                                      issues_column: str) -> pd.DataFrame:
    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())

    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    return df_submissions.apply(lambda submission:
                                filter_in_single_submission(submission, issues_column=issues_column,
                                                            step=df_steps.loc[submission[
                                                                SubmissionColumns.STEP_ID.value]]), axis=1)


def main(submissions_path: str, steps_path: str, filtered_submissions_path: str, issues_column: str):
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_filtered_submissions = filter_template_issues_using_diff(df_submissions, df_steps, issues_column)
    write_df(df_filtered_submissions, filtered_submissions_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('filtered_submissions_path', type=str,
                        help='Path .csv file with submissions with filtered template issues.')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.repetitive_issues_path, f'template_issues_filtering_{args.equal}', args.log_path)

    main(args.submissions_path, args.steps_path, args.filtered_submissions_path, args.issues_column)
