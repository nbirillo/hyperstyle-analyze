import argparse
import json
import sys
from typing import List, Callable, Tuple

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df, rename_columns
from analysis.src.python.evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder


def submission_to_issue_code_pairs(submission: pd.DataFrame) -> List[Tuple[str, str]]:
    """
    Represent issue as a pair <origin_class, line>.
    """
    issues = submission[SubmissionColumns.RAW_ISSUES.value]
    return [(issue.origin_class, submission[SubmissionColumns.CODE.value][issue.line_no - 1]) for issue in issues]


equal_lines: Callable[[str, str], bool] = lambda x, y: x == y


def equal_issues(issue: Tuple[str, str], other_issue: Tuple[str, str]) -> bool:
    return issue[0] == other_issue[0] and equal_lines(issue[1], other_issue[1])


def get_repetitive_issues(issues_by_attempt: List[List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    """
    Find issues that occur in every attempt of the series issues_by_attempt.
    """

    def is_in_previous_issues(issue_line: Tuple[str, str],
                              previous_issues_lines: List[Tuple[str, str]]) -> bool:
        for pr_issue_line in previous_issues_lines:
            if equal_issues(issue_line, pr_issue_line):
                return True
        return False

    prev_issues = issues_by_attempt[0]

    for attempt in range(1, len(issues_by_attempt)):
        issues = issues_by_attempt[attempt]
        prev_issues = [issue for issue in issues if is_in_previous_issues(issue, prev_issues)]

    return prev_issues


def get_candidate_issues(df_submissions: pd.DataFrame) -> pd.Series:
    """
    Rank issues by frequency of occurrence in all attempts of the series.
    """
    candidate_issues = []
    n = df_submissions[SubmissionColumns.GROUP.value].nunique()

    for group_no in df_submissions[SubmissionColumns.GROUP.value].unique():
        df_issues = df_submissions[df_submissions[SubmissionColumns.GROUP.value] == group_no] \
            .sort_values(by=SubmissionColumns.ATTEMPT.value) \
            .agg(lambda x: submission_to_issue_code_pairs(x), axis=1)
        candidate_issues += get_repetitive_issues(df_issues.to_list())

    ranking = pd.DataFrame(candidate_issues).value_counts()
    ranking /= n
    return ranking


def search(submissions_path: str, result_path: str, n: int):
    """
    Get n most frequently uncorrected issues for every step_id in submissions_path and write them to result_path.
    """
    df_submissions = read_df(submissions_path)

    df_submissions = df_submissions[[SubmissionColumns.ID.value,
                                     SubmissionColumns.STEP_ID.value,
                                     SubmissionColumns.CODE.value,
                                     SubmissionColumns.GROUP.value,
                                     SubmissionColumns.ATTEMPT.value,
                                     SubmissionColumns.RAW_ISSUES.value]]

    # Parsing raw issues
    df_submissions[SubmissionColumns.RAW_ISSUES.value] = \
        df_submissions[SubmissionColumns.RAW_ISSUES.value].map(lambda x: json.loads(x, cls=RawIssueDecoder))
    # Splitting code to lines
    df_submissions[SubmissionColumns.CODE.value] = \
        df_submissions[SubmissionColumns.CODE.value].map(lambda x: x.split('\n'))

    df_issues_ranking = pd.DataFrame()

    for step_id in df_submissions[SubmissionColumns.STEP_ID.value].unique():
        m = df_submissions[SubmissionColumns.STEP_ID.value] == step_id
        df_candidate_issues = get_candidate_issues(df_submissions[m]).head(n).reset_index(name='frequency')

        df_candidate_issues = pd.DataFrame({SubmissionColumns.STEP_ID.value: [step_id] * df_candidate_issues.shape[0],
                                            SubmissionColumns.RAW_ISSUE_CLASS.value: df_candidate_issues[0],
                                            'line': df_candidate_issues[1],
                                            'frequency': df_candidate_issues['frequency']})
        df_candidate_issues['line'] = df_candidate_issues['line'].map(lambda x: x.strip())
        df_issues_ranking = pd.concat([df_issues_ranking, df_candidate_issues], axis=0, ignore_index=True)

    df_issues_ranking.to_csv(result_path, sep='`', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('result_path', type=str, help='Path to resulting .csv file with issues ranking.')
    parser.add_argument('--N', type=int, default=5,
                        help='Number of top issues for every step.')

    args = parser.parse_args(sys.argv[1:])

    search(args.submissions_path, args.result_path, args.N)
