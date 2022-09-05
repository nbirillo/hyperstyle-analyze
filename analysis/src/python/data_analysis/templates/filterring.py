import argparse
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.templates.template_matching import match_code_with_template
from analysis.src.python.data_analysis.templates.utils.code_compare_utils import CodeComparator
from analysis.src.python.data_analysis.templates.utils.template_utils import parse_template_code_from_step
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.utils.df_utils import filter_df_by_single_value, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def filter_template_issues_from_submission(submission: pd.Series,
                                           df_steps: pd.DataFrame,
                                           df_templates_issues: pd.DataFrame,
                                           issues_column: str,
                                           code_comparator: CodeComparator) -> pd.Series:
    """
    Filter all template issues from submission.
    Build matching for submission's code lines with its template code lines char by char.
    Filter submission issue in case of matching line in template contains such issue.
    """

    logging.info(f'Processing submission {submission[SubmissionColumns.ID.value]}.')

    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
    lang = submission[SubmissionColumns.LANG.value]
    step_id = submission[SubmissionColumns.STEP_ID.value]

    step = df_steps.loc[step_id]
    template_lines = parse_template_code_from_step(step, lang)
    code_to_template, _ = match_code_with_template(code_lines, template_lines,
                                                   code_comparator.is_equal,
                                                   code_comparator.is_empty)

    df_templates_issues = filter_df_by_single_value(df_templates_issues, SubmissionColumns.STEP_ID.value, step_id)
    template_issues = []

    report = parse_report(submission, issues_column)

    for _, templates_issue in df_templates_issues.iterrows():
        template_issue_name = templates_issue[IssuesColumns.NAME.value]
        template_issue_positions = templates_issue[TemplateColumns.POS_IN_TEMPLATE.value]
        template_line_with_issue = templates_issue[TemplateColumns.LINE.value]

        for issue in report.get_issues():
            code_issue_position = issue.get_line_number() - 1
            code_line_with_issue = code_lines[code_issue_position]

            if issue.get_name() == template_issue_name and \
                    code_issue_position == template_issue_positions and \
                    code_comparator.is_equal(template_line_with_issue, code_line_with_issue):
                template_issues.append(issue)
                break

        logging.info(f'Issue {template_issue_name} in line {template_issue_positions} is unmatched.')

    logging.info(f'{len(template_issues)}/{df_templates_issues.shape[0]} template issues was matched.')

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[issues_column + '_diff'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[issues_column + '_all'] = report.to_json()

    return submission


def filter_template_issues(df_templates_issues: pd.DataFrame,
                           df_submissions: pd.DataFrame,
                           df_steps: pd.DataFrame,
                           issues_column: str,
                           code_comparator: CodeComparator) -> pd.DataFrame:
    """ Filter all template issues from all submission. Skipping templates with undefined position. """

    df_templates_issues = df_templates_issues.dropna(subset=[TemplateColumns.POS_IN_TEMPLATE.value])
    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    df_submissions = df_submissions.apply(filter_template_issues_from_submission,
                                          df_steps=df_steps,
                                          df_templates_issues=df_templates_issues,
                                          issues_column=issues_column,
                                          code_comparator=code_comparator,
                                          axis=1)

    return df_submissions


def main(templates_issues_path: str,
         submissions_path: str,
         steps_path: str,
         filtered_submissions_path: str,
         issues_column: str,
         equal_type: str,
         ignore_trailing_comments: bool,
         ignore_trailing_whitespaces: bool):
    df_templates_issues = read_df(templates_issues_path)
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    code_comparator = CodeComparator(equal_type, ignore_trailing_comments, ignore_trailing_whitespaces)

    df_submissions = filter_template_issues(df_templates_issues, df_submissions, df_steps, issues_column,
                                            code_comparator)
    write_df(df_submissions, filtered_submissions_path)


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('templates_issues_path', type=str, help='Path to .csv file with issues in templates.')
    parser.add_argument('submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to file with submissions.')
    parser.add_argument('filtered_submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('issues_column', type=str, help='Path to file with submissions.')

    parser.add_argument('--equal', type=str, default='edit_distance',
                        help='Function for lines comparing.',
                        choices=['edit_distance', 'edit_ratio', 'substring'])
    parser.add_argument('-ic', '--ignore-trailing-comments', action='store_false',
                        help='Ignore trailing comments in code compare. True by default.')
    parser.add_argument('-iw', '--ignore-trailing-whitespaces', action='store_false',
                        help='Ignore trailing whitespaces in code compare. True by default.')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.filtered_submissions_path, 'template_issues_filtering', args.log_path)

    main(args.templates_issues_path,
         args.submissions_path,
         args.steps_path,
         args.filtered_submissions_path,
         args.issues_column,
         args.equal_type,
         args.ignore_trailing_comments,
         args.ignore_trailing_whitespaces)
