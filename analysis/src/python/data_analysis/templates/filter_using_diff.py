import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Tuple

import pandas as pd
from dataclasses_json import dataclass_json
from diff_match_patch import diff_match_patch

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns
from analysis.src.python.data_analysis.templates.utils.template_utils import parse_template_code_from_step
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.evaluation.tools.model.report import BaseIssue, BaseReport
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger
from evaluation.tools.hyperstyle.model.report import HyperstyleIssue
from evaluation.tools.qodana.model.report import Problem


@unique
class DiffTag(Enum):
    ADDITION = 1
    EQUAL = 0
    DELETION = -1


@dataclass(frozen=True)
class DiffResult:
    """
        tag - type of change where 0 (code not changed), 1 (code added).
        start - position of change start (included)
        end - position of change end (excluded)
        """
    tag: DiffTag
    start: int
    end: int


@dataclass_json
@dataclass(frozen=True)
class TemplateIssueResult:
    issue: BaseIssue
    position: int

    def build_row(self, step_id: int) -> dict:
        return {
            SubmissionColumns.STEP_ID.value: step_id,
            IssuesColumns.NAME.value: self.issue.get_name(),
            IssuesColumns.CATEGORY.value: self.issue.get_category(),
            IssuesColumns.TEXT.value: self.issue.get_text(),
            StepColumns.POSITION.value: self.position,
        }


@dataclass_json
@dataclass(frozen=True)
class TemplateIssueResultList:
    results: List[TemplateIssueResult]


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


def get_template_to_code_diffs(template_lines: List[str], code_lines: List[str]) -> List[DiffResult]:
    """
    Get template to students code diff in format of list of tuples (tag, start, end).
     Tag -1 (code deleted) is ignored.
    """

    matcher = diff_match_patch()
    patches = matcher.diff_main(''.join(template_lines), ''.join(code_lines))

    diffs = []
    start = 0

    for tag, patch in patches:
        if tag != DiffTag.DELETION.value:
            end = start + len(patch)
            diffs.append(DiffResult(tag, start, end))
            start = end

    return diffs


def get_template_index(current_index: int, template_lines: List[str], row_with_issue: str) -> int:
    for i in range(current_index, len(template_lines)):
        if row_with_issue in template_lines[i]:
            return i
    return -1


def get_template_issues(
        issues_with_offset: List[Tuple[int, BaseIssue]],
        diff: List[DiffResult],
        template_lines: List[str],
        code_lines: List[str],
) -> List[TemplateIssueResult]:
    """
    Get template issues from list of issues.
    Issues considered as template if it's position inside change in diff with type 0 - code not changed from template.
    """

    # template_lines.index(code_lines[issue.get_line_number() - 1])

    current_template_index = 0
    i = 0
    template_issues = []
    for offset, issue in issues_with_offset:
        while i < len(diff) and diff[i].end < offset:
            i += 1
        # If tag is 0 (equal) the part of code was not changed from template
        if i >= len(diff) or diff[i].tag == DiffTag.EQUAL.value:
            row_with_issue = code_lines[issue.get_line_number() - 1]
            current_template_index = get_template_index(current_template_index, template_lines, row_with_issue)
            if current_template_index == -1:
                raise ValueError(f'Did not found "{row_with_issue}" in the template')
            template_issues.append(TemplateIssueResult(issue, current_template_index))

    return template_issues


def filter_in_single_submission(
        submission: pd.Series,
        step: pd.Series,
        issues_column: str,
) -> pd.Series:
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value], keep_ends=True)
    lang = submission[SubmissionColumns.LANG.value]
    template_lines = parse_template_code_from_step(step, lang, keep_ends=True)

    report = parse_report(submission, issues_column)

    issues_with_offset = get_issues_with_offset(report, code_lines)
    diff = get_template_to_code_diffs(template_lines, code_lines)
    template_issues_with_positions = get_template_issues(issues_with_offset, diff, template_lines, code_lines)

    template_issues = list(map(lambda r: r.issue, template_issues_with_positions))

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[f'{issues_column}_diff'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[f'{issues_column}_all'] = report.to_json()
    submission[f'{issues_column}_templates'] = TemplateIssueResultList(template_issues_with_positions).to_json()

    return submission


def filter_template_issues_using_diff(
        df_submissions: pd.DataFrame,
        df_steps: pd.DataFrame,
        issues_column: str,
) -> pd.DataFrame:
    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())
    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    def apply_algo(submission):
        return filter_in_single_submission(submission, issues_column=issues_column,
                                           step=df_steps.loc[submission[
                                               SubmissionColumns.STEP_ID.value]])

    return df_submissions.apply(lambda submission: apply_algo(submission), axis=1)


def parse_template_issue_result_list(dumped: str, issues_column: str) -> TemplateIssueResultList:
    issues_with_positions = json.loads(dumped)
    issues = []
    for res in issues_with_positions['results']:
        issue = json.dumps(res['issue'])
        if issues_column == SubmissionColumns.HYPERSTYLE_ISSUES.value:
            issues.append(TemplateIssueResult(HyperstyleIssue.from_json(issue), res['position']))
        elif issues_column == SubmissionColumns.QODANA_ISSUES.value:
            issues.append(TemplateIssueResult(Problem.from_json(issue), res['position']))
    return TemplateIssueResultList(issues)


def build_empty_template_issues_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        SubmissionColumns.STEP_ID.value,
        IssuesColumns.NAME.value,
        IssuesColumns.CATEGORY.value,
        IssuesColumns.POSITION.value,
    ])


def extract_template_issues(df_filtered_submissions: pd.DataFrame, issues_column: str) -> pd.DataFrame:
    column = f'{issues_column}_templates'
    template_issues_df = build_empty_template_issues_df()

    def handle_one_submission(submission: pd.Series, template_issues_df: pd.DataFrame) -> pd.DataFrame:
        issues_with_positions = parse_template_issue_result_list(submission[column], issues_column)
        for res in issues_with_positions.results:
            template_issues_df = template_issues_df.append(
                res.build_row(submission[SubmissionColumns.STEP_ID.value]),
                ignore_index=True,
            )
        return template_issues_df

    for _, submission in df_filtered_submissions.iterrows():
        template_issues_df = handle_one_submission(submission, template_issues_df)

    return template_issues_df.sort_values(SubmissionColumns.STEP_ID.value) \
        .drop_duplicates(subset=[
            SubmissionColumns.STEP_ID.value,
            IssuesColumns.NAME.value,
            IssuesColumns.CATEGORY.value,
            IssuesColumns.POSITION.value,
        ], keep='last')


def main(
        submissions_path: str,
        steps_path: str,
        filtered_submissions_path: str,
        template_issues_path: str,
        issues_column: str,
):
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_filtered_issues = filter_template_issues_using_diff(
        df_submissions,
        df_steps,
        issues_column,
    )
    df_filtered_issues = extract_template_issues(df_filtered_issues, issues_column)
    write_df(df_filtered_issues, filtered_submissions_path)
    write_df(df_filtered_issues, template_issues_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('filtered_submissions_path', type=str,
                        help='Path .csv file with submissions with filtered template issues.')
    parser.add_argument('template_issues_path', type=str,
                        help='Path .csv file with template issues with their positions.')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.filtered_submissions_path, 'template_issues_filtering_using_diff', args.log_path)

    main(
        args.submissions_path,
        args.steps_path,
        args.filtered_submissions_path,
        args.template_issues_path,
        args.issues_column,
    )
