import argparse
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.template_errors.template_matching import equal_char_by_char, match
from analysis.src.python.data_analysis.template_errors.template_utils import parse_template_issue_positions, \
    parse_templates_code
from analysis.src.python.data_analysis.utils.analysis_issue import parse_report
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.utils.df_utils import filter_df_by_single_value, merge_dfs, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('templates_issues_path', type=str, help='Path to .csv file with issues in templates.')
    parser.add_argument('submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to file with submissions.')
    parser.add_argument('filtered_submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('issues_column', type=str, help='Path to file with submissions.')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


def filter_template_issues_from_submission(submission: pd.Series,
                                           df_templates_issues: pd.DataFrame,
                                           issues_column: str) -> pd.Series:
    """
    Filter all template issues from submission.
    Build matching for submission's code lines with it's template code lines char by char.
    Filter submission issue in case of matching line in template contains such issue.
    """

    report = parse_report(submission, issues_column)
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
    lang = submission[SubmissionColumns.LANG.value]

    template_issues = []

    df_step_templates_issues = filter_df_by_single_value(df_templates_issues,
                                                         SubmissionColumns.STEP_ID.value,
                                                         submission[SubmissionColumns.STEP_ID.value])

    for _, templates_issue in df_step_templates_issues.iterrows():

        template_issue_name = templates_issue[IssuesColumns.NAME.value]
        template_issue_positions = templates_issue[TemplateColumns.POS_IN_TEMPLATE.value]
        template_code_lines = templates_issue[StepColumns.CODE_TEMPLATES.value][lang]

        matching = match(code_lines, template_code_lines, equal_char_by_char)
        matched_template_issue_positions = []

        for issue in report.issues:

            if issue.name != template_issue_name:
                continue

            for template_issue_position in template_issue_positions:
                matched_issues_position = matching[issue.line_number - 1]

                if matched_issues_position == template_issue_position:
                    template_issues.append(issue)
                    matched_template_issue_positions.append(template_issue_position)

        logging.info(f'{len(matched_template_issue_positions)}/{len(template_issue_positions)} '
                     f'template issues {template_issue_name} was matched '
                     f'in step {submission[SubmissionColumns.STEP_ID.value]}.')

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[issues_column + '_diff'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[issues_column + '_all'] = report.to_json()

    return submission


def filter_template_issues(df_templates_issues: pd.DataFrame,
                           df_submissions: pd.DataFrame,
                           df_steps: pd.DataFrame,
                           issues_column: str) -> pd.DataFrame:
    """ Filter all template issues from all submission. Skipping templates with undefined position. """

    df_templates_issues = merge_dfs(df_templates_issues,
                                    df_steps[[StepColumns.ID.value, StepColumns.CODE_TEMPLATES.value]],
                                    left_on=SubmissionColumns.STEP_ID.value,
                                    right_on=StepColumns.ID.value)

    df_templates_issues = df_templates_issues.dropna(subset=[TemplateColumns.POS_IN_TEMPLATE.value])

    df_templates_issues[TemplateColumns.POS_IN_TEMPLATE.value] = \
        df_templates_issues[TemplateColumns.POS_IN_TEMPLATE.value].apply(parse_template_issue_positions)

    df_templates_issues[StepColumns.CODE_TEMPLATES.value] = \
        df_templates_issues[StepColumns.CODE_TEMPLATES.value].apply(parse_templates_code)

    df_submissions = df_submissions.apply(filter_template_issues_from_submission,
                                          df_templates_issues=df_templates_issues,
                                          issues_column=issues_column,
                                          axis=1)

    return df_submissions


def main(templates_issues_path: str,
         submissions_path: str,
         steps_path: str,
         filtered_submissions_path: str,
         issues_column: str):
    df_templates_issues = read_df(templates_issues_path)
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_submissions = filter_template_issues(df_templates_issues, df_submissions, df_steps, issues_column)
    write_df(df_submissions, filtered_submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.filtered_submissions_path, 'template', args.log_path)

    main(args.templates_issues_path,
         args.submissions_path,
         args.steps_path,
         args.filtered_submissions_path,
         args.issues_column)
