import argparse
import ast
import json
import os
import sys
from typing import Callable, List, Tuple

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns
from analysis.src.python.data_analysis.template_errors.template_matching import EQUAL, match
from analysis.src.python.data_analysis.utils.df_utils import drop_columns, read_df, write_df
from analysis.src.python.evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder


def submission_to_issue_code_pos(submission: pd.DataFrame) -> List[Tuple[str, str, int]]:
    """
    Represent issue as a tuple <origin_class, line, pos_in_template>.
    """
    issues = submission[SubmissionColumns.RAW_ISSUES.value]
    return [(issue.origin_class,
             submission[SubmissionColumns.CODE.value][issue.line_no - 1],
             submission['pos_in_template'][issue.line_no - 1])
            for issue in issues]


def equal_issues(issue: Tuple[str, str, int], other_issue: Tuple[str, str, int],
                 equal: Callable[[str, str], bool]) -> bool:
    return issue[0] == other_issue[0] and (issue[2] == -1 and other_issue[2] == -1 and equal(issue[1], other_issue[1])
                                           or issue[2] == other_issue[2])


def get_repetitive_issues(issues_by_attempt: List[List[Tuple[str, str, int]]],
                          equal: Callable[[str, str], bool]) -> List[Tuple[str, str, int]]:
    """
    Find issues that occur in every attempt of the series issues_by_attempt.
    """

    def is_in_previous_issues(issue_line: Tuple[str, str, int],
                              previous_issues_lines: List[Tuple[str, str, int]]) -> bool:
        return any(map(lambda x: equal_issues(issue_line, x, equal), previous_issues_lines))

    prev_issues = issues_by_attempt.pop(0) if len(issues_by_attempt) > 0 else []

    for issues in issues_by_attempt:
        prev_issues = list(filter(lambda x: is_in_previous_issues(x, prev_issues), issues))

    return prev_issues


def get_candidate_issues(df_submissions: pd.DataFrame, equal: Callable[[str, str], bool]) -> pd.Series:
    """
    Rank issues by frequency of occurrence in all attempts of the series.
    """
    candidate_issues = []
    groups = df_submissions[SubmissionColumns.GROUP.value].unique()

    for group_no in groups:
        df_issues = df_submissions[df_submissions[SubmissionColumns.GROUP.value] == group_no] \
            .sort_values(by=SubmissionColumns.ATTEMPT.value) \
            .apply(lambda x: submission_to_issue_code_pos(x), axis=1)
        candidate_issues += get_repetitive_issues(df_issues.to_list(), equal)

    ranking = pd.DataFrame(candidate_issues).value_counts()
    ranking /= len(groups)
    return ranking


def merge_template_errors(df_ranking: pd.DataFrame) -> pd.DataFrame:
    """
    Merge same template issues in ranking for single step.
    """

    def get_unique_pairs(df: pd.DataFrame, first_col: str, second_col: str):
        return df.loc[:, [first_col, second_col]].drop_duplicates().values

    df_template_errors = df_ranking[df_ranking['pos_in_template'] != -1]
    df_other_errors = df_ranking[df_ranking['pos_in_template'] == -1]
    step_id = df_ranking.iloc[0][SubmissionColumns.STEP_ID.value]

    df_merged = pd.DataFrame()
    for issue, pos in get_unique_pairs(df_template_errors, SubmissionColumns.RAW_ISSUE_CLASS.value, 'pos_in_template'):
        df_cur_error = df_template_errors[(df_template_errors[SubmissionColumns.RAW_ISSUE_CLASS.value] == issue)
                                          & (df_template_errors['pos_in_template'] == pos)]
        if df_cur_error.shape[0] == 1:
            df_merged = pd.concat([df_merged, df_cur_error], axis=0, ignore_index=True)
        else:
            df_merged = pd.concat([df_merged, pd.DataFrame({SubmissionColumns.STEP_ID.value: [step_id],
                                                            SubmissionColumns.RAW_ISSUE_CLASS.value: [issue],
                                                            'line': ['<multiple lines>'],
                                                            'pos_in_template': [pos],
                                                            'frequency': [df_cur_error['frequency'].sum()]})],
                                  axis=0, ignore_index=True)

    return pd.concat([df_merged, df_other_errors], axis=0, ignore_index=True) \
        .sort_values(by='frequency', ascending=False)


def count_groups(df_submissions: pd.DataFrame, df_steps: pd.DataFrame):
    """
    Count number of groups in df_submissions for every step_id in df_steps
    """

    def count(step_id: int):
        return len(df_submissions[df_submissions[SubmissionColumns.STEP_ID.value] == step_id][
                       SubmissionColumns.GROUP.value].unique())

    groups_count = df_steps[StepColumns.ID.value].map(count).rename('groups_cnt')
    df_steps = pd.concat([df_steps, groups_count], axis=1)
    return df_steps


def match_with_template(df_submissions: pd.DataFrame, df_steps: pd.DataFrame, equal: Callable[[str, str], bool]) \
        -> pd.DataFrame:
    """
    Match every line from every submission with a corresponding template line and add
    the resulting list of positions to 'pos_in_template' column.
    """

    def match_single_submission(submission: pd.DataFrame, df_steps: pd.DataFrame) -> List[int]:
        step_id = submission[SubmissionColumns.STEP_ID.value]
        template = df_steps[df_steps[StepColumns.ID.value] == step_id].iloc[0][StepColumns.CODE_TEMPLATES.value]
        positions = match(submission[SubmissionColumns.CODE.value], template, equal)
        return positions

    df_submissions['pos_in_template'] = df_submissions.apply(lambda x: match_single_submission(x, df_steps), axis=1)

    return df_submissions


def search(submissions_path: str, steps_path: str, result_path: str, preprocessed_steps_path: str, n: int,
           equal_type: str):
    """
    Get n most frequently uncorrected issues for every step_id in submissions_path and write them to result_path.
    """
    equal = EQUAL[equal_type]

    df_submissions = read_df(submissions_path)

    lang = 'java17'
    df_steps = read_df(steps_path)
    # Parsing code templates
    df_steps[StepColumns.CODE_TEMPLATES.value] = \
        df_steps[StepColumns.CODE_TEMPLATES.value].map(lambda x: ast.literal_eval(x)[lang].split(os.linesep))

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
        df_submissions[SubmissionColumns.CODE.value].map(lambda x: [line.rstrip('\r') for line in x.split(os.linesep)])

    df_steps = count_groups(df_submissions, df_steps)
    write_df(df_steps, preprocessed_steps_path)

    df_submissions = match_with_template(df_submissions, df_steps, equal)

    df_issues_ranking = pd.DataFrame()

    for step_id in df_submissions[SubmissionColumns.STEP_ID.value].unique():
        m = df_submissions[SubmissionColumns.STEP_ID.value] == step_id
        df_candidate_issues = get_candidate_issues(df_submissions[m], equal).head(n).reset_index(name='frequency')
        if df_candidate_issues.shape[0] == 0:
            continue
        df_candidate_issues = pd.DataFrame({SubmissionColumns.STEP_ID.value: [step_id] * df_candidate_issues.shape[0],
                                            SubmissionColumns.RAW_ISSUE_CLASS.value: df_candidate_issues[0],
                                            'line': df_candidate_issues[1],
                                            'pos_in_template': df_candidate_issues[2],
                                            'frequency': df_candidate_issues['frequency']})
        df_candidate_issues = merge_template_errors(df_candidate_issues)
        df_issues_ranking = pd.concat([df_issues_ranking, df_candidate_issues], axis=0, ignore_index=True)

    df_issues_ranking = drop_columns(df_issues_ranking, ['line']).replace({-1: None})
    write_df(df_issues_ranking, result_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('result_path', type=str, help='Path to resulting .csv file with issues ranking.')
    parser.add_argument('preprocessed_steps_path', type=str, nargs='?', default=None,
                        help='Path to new .csv file with steps and counted number of groups.')
    parser.add_argument('--N', type=int, default=5, help='Number of top issues for every step.')
    parser.add_argument('--equal', type=str, default='char_by_char',
                        help='Function for lines comparing. Possible functions: "char_by_char", "edit_distance"')

    args = parser.parse_args(sys.argv[1:])

    if args.preprocessed_steps_path is None:
        args.preprocessed_steps_path = args.steps_path

    search(args.submissions_path, args.steps_path, args.result_path, args.preprocessed_steps_path, args.N, args.equal)
