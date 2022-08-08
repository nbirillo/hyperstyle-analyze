import argparse
from pathlib import Path
from typing import Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.search.utils.comment_utils import add_issues_comments_to_code
from analysis.src.python.data_analysis.utils.analysis_issue import AnalysisReport
from analysis.src.python.evaluation.utils.solutions_saving_utils import save_solution_to_file
from analysis.src.python.utils.df_utils import filter_df_by_predicate, filter_df_by_single_value, read_df, write_df
from analysis.src.python.utils.file_utils import AnalysisExtension, create_directory
from analysis.src.python.utils.logging_utils import configure_logger


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('output_path', type=str, help='Path to directory with output')
    parser.add_argument('issues_column', type=str, help='Issue column name to add issues comment',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--steps-issues-path', type=str, default=None,
                        help='Path to .csv file with pairs fo steps and issues for examples finding')
    parser.add_argument('--issue-name', type=str, default=None, help='Issue example to search for')
    parser.add_argument('--step', type=int, default=None, help='Step to search submissions for')
    parser.add_argument('--count', type=int, default=5, help='Size of search output')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


def write_submissions_to_files(df_submissions: pd.DataFrame, output_path: Path):
    """ Save submission to file with extension. Easy to compare diffs. """

    output_path = create_directory(output_path)
    output_file = output_path / f'submissions{AnalysisExtension.CSV.value}'
    write_df(df_submissions, output_file)

    df_submissions.apply(save_solution_to_file, input_path=output_path, axis=1)


def search_submissions_by_step_issue(df_submissions: pd.DataFrame, issues_column: str,
                                     step: int, issue_name: str,
                                     count: int, output_path: Path):
    """
    Search and save to `submissions_sample_path` examples of submissions for given `step`
    with and without given `issue_name`.
    """

    df_submissions = filter_df_by_single_value(df_submissions, SubmissionColumns.STEP_ID.value, step)

    def check_contains_issue(issues: str) -> bool:
        report = AnalysisReport.from_json(issues)
        return report.has_issue(issue_name)

    df_submissions_with_issue = filter_df_by_predicate(df_submissions, issues_column, check_contains_issue)
    df_submissions_with_issue = df_submissions_with_issue.head(count)
    df_submissions_with_issue = df_submissions_with_issue.apply(add_issues_comments_to_code,
                                                                issues_column=issues_column,
                                                                issue_name=issue_name,
                                                                axis=1)

    df_submissions_without_issue = filter_df_by_predicate(df_submissions, issues_column, check_contains_issue,
                                                          inverse=True)
    df_submissions_without_issue = df_submissions_without_issue.head(count)

    step_output_path = output_path / f'{issue_name}_{step}_{count}'
    write_submissions_to_files(df_submissions_with_issue, step_output_path / 'with_issue')
    write_submissions_to_files(df_submissions_without_issue, step_output_path / 'without_issue')


def main(submissions_path: str,
         issues_column: str, steps_issues_path: Optional[str],
         step: Optional[int], issue_name: Optional[str],
         count: int, output_path: str):
    """
    Search and save to `submissions_sample_path` examples of steps submissions with and without issue.
    Pairs of step and issue can be provided directly or listed in `steps_issues_path` csv file.
    """

    assert steps_issues_path is not None or (step is not None and issue_name is not None), \
        "if steps_issues_path is not defined provide step and issue_name to search issues"

    output_path = create_directory(output_path)
    df_submissions = read_df(submissions_path)

    if steps_issues_path is None:
        search_submissions_by_step_issue(df_submissions, issues_column, step, issue_name, count, output_path)
    else:
        df_issues_steps = read_df(steps_issues_path)
        df_issues_steps.apply(lambda row: search_submissions_by_step_issue(df_submissions,
                                                                           issues_column,
                                                                           row[SubmissionColumns.STEP_ID.value],
                                                                           row[IssuesColumns.NAME.value],
                                                                           count,
                                                                           output_path), axis=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    configure_logger(args.output_dir, 'search', args.log_path)

    main(args.submissions_path,
         args.issues_column,
         args.steps_issues_path,
         args.step,
         args.issue_name,
         args.count,
         args.output_path)
