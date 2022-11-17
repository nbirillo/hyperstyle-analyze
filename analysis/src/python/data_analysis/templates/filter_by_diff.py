import argparse
import bisect
import sys
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Tuple

import pandas as pd
from diff_match_patch import diff_match_patch

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns
from analysis.src.python.data_analysis.templates.utils.template_utils import parse_template_code_from_step
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.evaluation.tools.model.report import BaseIssue
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


@unique
class DiffTag(Enum):
    ADDITION = 1
    EQUAL = 0
    DELETION = -1


@dataclass(frozen=True)
class DiffInterval:
    """
        start - position of change start (included)
        end - position of change end (excluded)
    """
    start: int
    end: int


@dataclass(frozen=True)
class DiffResult:
    """
        tag - type of change where 0 (code not changed), 1 (code added), -1 (code deleted)
        patch - part of code which was changes
        template_interval - changed interval in template
        code_interval - changed interval in code
    """
    tag: DiffTag
    patch: str
    template_interval: DiffInterval
    code_interval: DiffInterval


def get_code_prefix_lengths(code_lines: List[str]) -> List[int]:
    code_prefix_length = [0]
    for code_line in code_lines:
        code_prefix_length.append(code_prefix_length[-1] + len(code_line))

    return code_prefix_length


def issues_positions_to_offsets(issues: List[BaseIssue], code_lines: List[str]) -> List[int]:
    """ For each issue calculate offset in code written in one line and return as pairs sorted in ascending order."""

    code_prefix_lengths = get_code_prefix_lengths(code_lines)

    issues_offsets = []
    for issue in issues:
        if issue.get_line_number() == 0:
            issues_offsets.append(0)
        issue_offset = code_prefix_lengths[issue.get_line_number() - 1] + issue.get_column_number()
        issues_offsets.append(issue_offset)

    return issues_offsets


def issues_offsets_to_positions(offsets: List[int], code_lines: List[str]) -> List[Tuple[int, int]]:
    code_prefix_lengths = get_code_prefix_lengths(code_lines)

    issues_positions = []
    for offset in offsets:
        line_number = bisect.bisect_right(code_prefix_lengths, offset)
        if line_number == 0:
            column_number = offset
        else:
            column_number = offset - code_prefix_lengths[line_number - 1]
        issues_positions.append((line_number, column_number))

    return issues_positions


def get_template_to_code_diffs(template_lines: List[str], code_lines: List[str]) -> List[DiffResult]:
    """ Get template to students code diffs. """

    matcher = diff_match_patch()
    patches = matcher.diff_main(''.join(template_lines), ''.join(code_lines))

    diffs = []
    code_start, code_end = 0, 0
    template_start, template_end = 0, 0

    for tag, patch in patches:
        if tag == DiffTag.ADDITION.value:
            code_end = code_start + len(patch)

        if tag == DiffTag.EQUAL.value:
            code_end = code_start + len(patch)
            template_end = template_start + len(patch)

        if tag == DiffTag.DELETION.value:
            template_end = template_start + len(patch)

        diffs.append(
            DiffResult(tag, patch, DiffInterval(template_start, template_end), DiffInterval(code_start, code_end)))
        code_start = code_end
        template_start = template_end

    return diffs


def get_template_issues(issues: List[BaseIssue], issues_offsets: List[int], diffs: List[DiffResult]) \
        -> Tuple[List[BaseIssue], List[int]]:
    """
    Get template issues from list of issues.
    Issues considered as template if it's position inside change in diff with type 0 - code not changed from template.
    """

    i = 0
    template_issues = []
    template_issues_offsets = []

    for issue, offset in sorted(zip(issues, issues_offsets), key=lambda p: p[1]):
        while i < len(diffs):
            diff = diffs[i]

            # If code interval is before issue offset continue
            if diff.code_interval.end < offset or diff.tag != DiffTag.EQUAL.value:
                i += 1
                continue

            # If issue is inside code interval and tag is "equal" consider issue as template
            interval_offset = offset - diff.code_interval.start
            template_offset = diff.template_interval.start + interval_offset
            template_issues.append(issue)
            template_issues_offsets.append(template_offset)
            break

    return template_issues, template_issues_offsets


def filter_in_single_submission(submission: pd.Series, step: pd.Series, issues_column: str) -> pd.Series:
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value], keep_ends=True)
    lang = submission[SubmissionColumns.LANG.value]
    template_lines = parse_template_code_from_step(step, lang, keep_ends=True)

    report = parse_report(submission, issues_column)
    issues = report.get_issues()
    issues_offsets = issues_positions_to_offsets(issues, code_lines)
    diff = get_template_to_code_diffs(template_lines, code_lines)
    template_issues, template_issues_offsets = get_template_issues(issues, issues_offsets, diff)
    template_issues_positions = issues_offsets_to_positions(template_issues_offsets, template_lines)

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[f'{issues_column}_diff'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[f'{issues_column}_all'] = report.to_json()
    submission[f'{issues_column}_diff_template_positions'] = str(template_issues_positions)

    return submission


def filter_template_issues_using_diff(df_submissions: pd.DataFrame, df_steps: pd.DataFrame, issues_column: str) \
        -> pd.DataFrame:
    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())
    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    def apply_filter(submission):
        return filter_in_single_submission(submission,
                                           issues_column=issues_column,
                                           step=df_steps.loc[submission[SubmissionColumns.STEP_ID.value]])

    return df_submissions.apply(lambda submission: apply_filter(submission), axis=1)


def main(submissions_path: str, steps_path: str, filtered_submissions_path: str, issues_column: str):
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_filtered_issues = filter_template_issues_using_diff(
        df_submissions,
        df_steps,
        issues_column,
    )
    write_df(df_filtered_issues, filtered_submissions_path)


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
    configure_logger(args.filtered_submissions_path, 'template_issues_filtering_by_diff', args.log_path)

    main(
        args.submissions_path,
        args.steps_path,
        args.filtered_submissions_path,
        args.issues_column,
    )
