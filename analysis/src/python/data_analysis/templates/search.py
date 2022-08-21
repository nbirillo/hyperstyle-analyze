import argparse
import sys
from collections import defaultdict
from typing import Callable, List, Tuple

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.templates.template_matching import EQUAL, match_code_with_template
from analysis.src.python.data_analysis.templates.utils.template_utlis import parse_template_code_from_step
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_repetitive_issues(submission_series: pd.DataFrame,
                          template_lines: List[str],
                          issues_column: str,
                          equal: Callable[[str], bool]) -> List[Tuple[str, int]]:
    """ Get issue name and position in template for issues that appear in every attempt in submission series. """

    attempts_with_issue_count = defaultdict(int)
    submission_series = submission_series.sort_values(SubmissionColumns.ATTEMPT.value)

    for _, submission in submission_series.iterrows():
        code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
        code_to_template, _ = match_code_with_template(code_lines, template_lines, equal)

        report = parse_report(submission, issues_column)
        for issue in report.get_issues():
            issue_name = issue.get_name()
            # In issues line count starts with 1
            code_line_number = issue.get_line_number() - 1
            if code_line_number < 0:
                # Some issues have zero line number meaning they do not have exact position and line
                issue_info = (issue_name, None, None)
            else:
                template_line_number = code_to_template[code_line_number]
                line_with_issue = code_lines[code_line_number] if template_line_number is None else \
                    template_lines[template_line_number]
                issue_info = (issue_name, line_with_issue, template_line_number)
            attempts_with_issue_count[issue_info] += 1

    total_attempts_count = submission_series.shape[0]

    # Repetitive issues are which appear in all attempts
    repetitive_issues = [issue for issue, attempts_count in attempts_with_issue_count.items() if
                         attempts_count == total_attempts_count]

    return repetitive_issues


def get_template_issues_by_step(df_submissions: pd.DataFrame,
                                step: pd.Series,
                                issues_column: str,
                                equal: Callable[[str], bool]) -> pd.DataFrame:
    """ Search template issues in submissions with given step. """

    step_ids = df_submissions[SubmissionColumns.STEP_ID.value].unique()
    assert len(step_ids) == 1, "All submissions should be for single step"

    langs = df_submissions[SubmissionColumns.LANG.value].unique()
    assert len(langs) == 1, "Can not process search for submissions with different language version"

    template = parse_template_code_from_step(step, langs[0])
    repetitive_issues_count = defaultdict(int)

    df_submission_series = df_submissions.groupby(SubmissionColumns.GROUP.value)
    for _, submission_series in df_submission_series:
        repetitive_issues = get_repetitive_issues(submission_series, template, issues_column, equal)
        for issue in repetitive_issues:
            repetitive_issues_count[issue] += 1

    template_issues = []

    for issue_info, issue_count in repetitive_issues_count.items():
        issue_name, line_with_issue, issue_line_number = issue_info
        template_issue = {IssuesColumns.NAME.value: issue_name,
                          TemplateColumns.LINE.value: line_with_issue,
                          TemplateColumns.POS_IN_TEMPLATE.value: issue_line_number,
                          TemplateColumns.COUNT.value: issue_count}
        template_issues.append(pd.Series(template_issue))

    df_template_issues = pd.DataFrame(template_issues, columns=[IssuesColumns.NAME.value,
                                                                TemplateColumns.LINE.value,
                                                                TemplateColumns.POS_IN_TEMPLATE.value,
                                                                TemplateColumns.COUNT.value])

    df_template_issues[TemplateColumns.POS_IN_TEMPLATE.value] = \
        df_template_issues[TemplateColumns.POS_IN_TEMPLATE.value].astype('Int64')

    df_template_issues[TemplateColumns.TOTAL_COUNT.value] = df_submissions.shape[0]
    df_template_issues[SubmissionColumns.STEP_ID.value] = step[StepColumns.ID.value]

    df_template_issues[TemplateColumns.FREQUENCY.value] = \
        df_template_issues[TemplateColumns.COUNT.value] / df_template_issues[TemplateColumns.TOTAL_COUNT.value]

    return df_template_issues.sort_values(by=TemplateColumns.COUNT.value, ascending=False)


def search_template_issues(df_submissions: pd.DataFrame,
                           df_steps: pd.DataFrame,
                           issues_column: str,
                           equal: Callable[[str], bool]) -> pd.DataFrame:
    """ Get `issues_count` most frequent uncorrected issues for every step in submissions. """

    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())

    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    return df_submissions \
        .groupby([SubmissionColumns.STEP_ID.value], as_index=False) \
        .apply(lambda df_step_submissions: get_template_issues_by_step(df_step_submissions,
                                                                       # name is group key (step id)
                                                                       step=df_steps.loc[df_step_submissions.name],
                                                                       issues_column=issues_column,
                                                                       equal=equal))


def main(submissions_path: str, steps_path: str, template_issues_path: str, issues_column: str, equal_type: str):
    """ Get uncorrected issues for every step in submissions and save them to template_issues_path. """

    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    equal = EQUAL[equal_type]

    df_template_issues = search_template_issues(df_submissions, df_steps, issues_column, equal)
    write_df(df_template_issues, template_issues_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('template_issues_path', type=str, help='Path to resulting .csv file with issues ranking.')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--equal', type=str, default='char_by_char',
                        help='Function for lines comparing.',
                        choices=['char_by_char', 'edit_distance', 'edit_ratio', 'substring'])
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.template_issues_path, 'templates', args.log_path)

    main(args.submissions_path, args.steps_path, args.template_issues_path, args.issues_column, args.equal)
