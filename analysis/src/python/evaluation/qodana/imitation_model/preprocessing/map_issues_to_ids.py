import argparse
from typing import Dict, List

import pandas as pd
from pandas import read_csv

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.df_utils import flat_apply, write_df
from analysis.src.python.data_analysis.utils.parsing_utils import dump_qodana_issues_to_str, list_to_str, \
    parse_qodana_issues_to_objects
from analysis.src.python.evaluation.qodana.util.models import QodanaIssue


def get_issues_to_ids_dict(df_issues: pd.DataFrame) -> Dict[str, int]:
    """ Creates dict with each issue class is connected with unique id. """

    df_issues[IssuesColumns.ID.value] = list(range(1, df_issues.shape[0] + 1))
    return {issue[IssuesColumns.CLASS.value]: issue[IssuesColumns.ID.value] for _, issue in df_issues.iterrows()}


def map_issue_to_ids(issues: List[QodanaIssue], issues_dict: Dict[str, int]) -> str:
    """ Map list of issues to list of their ids according to map `issues_dict`. """

    if len(issues) == 0:
        issue_ids = [0]
    else:
        issue_ids = list(map(lambda issue: issues_dict[issue.problem_id], issues))
        issue_ids.sort()
    return list_to_str(issue_ids)


def preprocess_qodana_issues(submission: pd.Series) -> pd.Series:
    """ Parses list of issues to list of qodana issues objects. """

    issues = parse_qodana_issues_to_objects(submission[SubmissionColumns.QODANA_ISSUES.value])

    submission_by_lines_dict = {
        SubmissionColumns.ID.value: submission[SubmissionColumns.ID.value],
        SubmissionColumns.CODE.value: submission[SubmissionColumns.CODE.value],
        SubmissionColumns.QODANA_ISSUES.value: issues
    }

    return pd.Series(submission_by_lines_dict)


def get_code_lines_to_issues(submission: pd.DataFrame) -> pd.DataFrame:
    """ Split submission to lines and divide issues to related line. """

    issues = parse_qodana_issues_to_objects(submission[SubmissionColumns.QODANA_ISSUES.value])
    code_lines = split_code_to_lines(submission)
    n_code_lines = len(code_lines)

    submission_by_lines_dict = {
        SubmissionColumns.ID.value: [submission[SubmissionColumns.ID.value]] * n_code_lines,
        SubmissionColumns.CODE.value: code_lines,
        SubmissionColumns.QODANA_ISSUES.value: [[] for _ in range(n_code_lines)]
    }

    for issue in issues:
        submission_by_lines_dict[SubmissionColumns.QODANA_ISSUES.value][issue.line - 1].append(issue)

    df = pd.DataFrame.from_dict(submission_by_lines_dict)

    return df


def map_submissions_issues_to_ids(submissions_path: str,
                                  issues_path: str,
                                  mapped_solutions_path: str,
                                  mapped_issues_path: str,
                                  by_line: bool = False,
                                  unique: bool = True):
    """
    Map list of issues in issues column to list of their ids.
    If `by_line` is True also split submission code to lines and distribute issues ids to lines.
    """

    df_submissions = read_csv(submissions_path)
    df_issues = read_csv(issues_path)

    issues_dict = get_issues_to_ids_dict(df_issues)
    write_df(df_issues, mapped_issues_path)

    if by_line:
        df_submissions = flat_apply(df_submissions, get_code_lines_to_issues)
    else:
        df_submissions = df_submissions.apply(preprocess_qodana_issues, axis=1)

    df_submissions[SubmissionColumns.QODANA_ISSUES_IDS.value] = \
        df_submissions[SubmissionColumns.QODANA_ISSUES.value].apply(map_issue_to_ids, issues_dict=issues_dict)

    df_submissions[SubmissionColumns.QODANA_ISSUES.value] = \
        df_submissions[SubmissionColumns.QODANA_ISSUES.value].apply(dump_qodana_issues_to_str)

    df_submissions[SubmissionColumns.CODE.value].fillna('\n', inplace=True)

    if unique:
        df_submissions = df_submissions.drop_duplicates()

    write_df(df_submissions, mapped_solutions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('mapped_submissions_path', type=str,
                        help='Path to .csv file with submissions with mapped issues')
    parser.add_argument('mapped_issues_path', type=str, help='Path to .csv file with issues mapped to ids')
    parser.add_argument('--by-line', action=argparse.BooleanOptionalAction,
                        help='Map issues by code line or whole code')
    parser.add_argument('--unique', action=argparse.BooleanOptionalAction,
                        help='Leave only unique pieces of code/lines')

    args = parser.parse_args()

    map_submissions_issues_to_ids(args.submissions_path,
                                  args.issues_path,
                                  args.mapped_submissions_path,
                                  args.mapped_issues_path,
                                  args.by_line,
                                  args.unique)
