import argparse
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.template_errors.template_matching import equal_char_by_char, match, \
    parse_template_code, parse_template_issues_positions
from analysis.src.python.data_analysis.utils.analysis_issue import AnalysisReport
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def configure_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('templates_issues_path', type=str, help='Path to .csv file with issues in templates.')
    parser.add_argument('submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('filtered_submissions_path', type=str, help='Path to file with submissions.')
    parser.add_argument('issues_column', type=str, help='Path to file with submissions.')
    parser.add_argument('template_lang', type=str, help='Language to select template for')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


def filter_template_issues_from_submission(submission: pd.Series,
                                           df_templates_issues: pd.DataFrame,
                                           issues_column: str) -> pd.Series:
    report = AnalysisReport.from_json(submission[issues_column])
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])

    template_issues_report = AnalysisReport([])

    for _, templates_issue in df_templates_issues.iterrows():

        if templates_issue[SubmissionColumns.STEP_ID.value] != submission[SubmissionColumns.STEP_ID.value]:
            continue

        template_issue_name = templates_issue[IssuesColumns.NAME.value]
        template_issue_positions = templates_issue[TemplateColumns.POS_IN_TEMPLATE.value]
        template_lines = templates_issue[StepColumns.CODE_TEMPLATES.value]

        matching = match(code_lines, template_lines, equal_char_by_char)

        if len(template_issue_positions) == 0:
            continue

        for issue in report.issues:
            if issue.name != template_issue_name:
                continue
            for template_issue_position in template_issue_positions:
                if matching[issue.line_number] == template_issue_position:
                    template_issues_report.issues.append(issue)

    filtered_report = AnalysisReport(issues=[issue for issue in report.issues if issue not in template_issues_report])
    submission[issues_column] = filtered_report.to_json()
    submission[issues_column + '_all'] = report.to_json()
    submission[issues_column + 'diff'] = template_issues_report.to_json()

    return submission


def filter_template_issues(df_templates_issues: pd.DataFrame,
                           df_submissions: pd.DataFrame,
                           df_steps: pd.DataFrame,
                           issues_column: str,
                           template_lang: str) -> pd.DataFrame:
    df_templates_issues = merge_dfs(df_templates_issues,
                                    df_steps[[StepColumns.ID.value, StepColumns.CODE_TEMPLATES.value]],
                                    left_on=SubmissionColumns.STEP_ID.value,
                                    right_on=StepColumns.ID.value)

    df_templates_issues[StepColumns.CODE_TEMPLATES.value] = \
        df_templates_issues[StepColumns.CODE_TEMPLATES.value].apply(parse_template_code, lang=template_lang)

    df_templates_issues[TemplateColumns.POS_IN_TEMPLATE.value] = \
        df_templates_issues[TemplateColumns.POS_IN_TEMPLATE.value].apply(parse_template_issues_positions)

    df_submissions = df_submissions.apply(filter_template_issues_from_submission,
                                          df_templates_issues=df_templates_issues,
                                          issues_column=issues_column,
                                          axis=1)

    return df_submissions


def main(templates_issues_path: str,
         submissions_path: str,
         steps_path: str,
         filtered_submissions_path: str,
         issues_column: str,
         template_lang: str):
    df_templates_issues = read_df(templates_issues_path)
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_submissions = filter_template_issues(df_templates_issues, df_submissions, df_steps, issues_column, template_lang)
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
         args.issues_column,
         args.template_lang)
