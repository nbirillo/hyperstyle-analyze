import argparse
import ast
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns, TemplateColumns
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_template_issues(submission: pd.Series, issues_column: str) -> pd.DataFrame:
    step_id = submission[SubmissionColumns.STEP_ID.value]
    submission_id = submission[SubmissionColumns.ID.value]
    template_issue_report = parse_report(submission[f'{issues_column}_diff'], issues_column)
    template_issues_positions = list(ast.literal_eval(submission[f'{issues_column}_diff_template_positions']))

    template_issues = []
    for issue, position in zip(template_issue_report.get_issues(), template_issues_positions):
        template_issues.append((step_id, submission_id, issue.get_name(), position))

    return pd.DataFrame.from_records(template_issues, columns=[SubmissionColumns.STEP_ID.value,
                                                               SubmissionColumns.ID.value,
                                                               IssuesColumns.NAME.value,
                                                               TemplateColumns.POS_IN_TEMPLATE])


def get_template_issues_stats(df_submissions: pd.DataFrame, df_template_issues: pd.DataFrame) -> pd.DataFrame:
    df_template_issues_stats = df_template_issues.groupby(df_template_issues.columns) \
        .size().reset_index(name=TemplateColumns.COUNT.value)

    df_steps_count = df_submissions.groupby(SubmissionColumns.STEP_ID.value) \
        .size().reset_index(name=TemplateColumns.TOTAL_COUNT.value)

    df_template_issues_stats = merge_dfs(df_template_issues_stats, df_steps_count,
                                         left_on=SubmissionColumns.STEP_ID.value,
                                         right_on=SubmissionColumns.STEP_ID.value)

    df_template_issues_stats[TemplateColumns.FREQUENCY.value] = \
        df_template_issues_stats[TemplateColumns.COUNT.value] / \
        df_template_issues_stats[TemplateColumns.TOTAL_COUNT.value]

    return df_template_issues_stats


def main(filtered_submissions_path: str, template_issues_stats_path: str, issues_column: str):
    df_submissions = read_df(filtered_submissions_path)
    df_template_issues = df_submissions.apply(get_template_issues, issues_column=issues_column, axis=1)
    df_template_issues_stats = get_template_issues_stats(df_submissions, df_template_issues)

    write_df(df_template_issues_stats, template_issues_stats_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('filtered_submissions_path', type=str,
                        help='Path .csv file with submissions with filtered template issues and their positions.')
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
    configure_logger(args.filtered_submissions_path, 'template_issues_postprocess_by_diff', args.log_path)

    main(
        args.filtered_submissions_path,
        args.template_issues_path,
        args.issues_column,
    )
