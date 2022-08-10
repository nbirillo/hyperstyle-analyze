import ast
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from analysis.src.python.data_analysis.analysis.attrs import AttrType, get_attr
from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.utils.df_utils import merge_dfs


class Stats(Enum):
    COUNT = 'count'
    ISSUE = 'issue'
    RATIO = 'ratio'


def get_top_issues(df: pd.DataFrame, df_issues: pd.DataFrame,
                   n: Optional[int] = None, ignore_issues: List[str] = None) -> pd.DataFrame:
    """
    Gets first `n` issues form `df_issues` (ignoring `ignore_issues`) sorted by count in all submissions from `df`.
    """

    df_top_issues = df_issues.copy()
    if ignore_issues is not None:
        df_top_issues = df_top_issues[~df_top_issues[IssuesColumns.NAME.value].isin(ignore_issues)]

    df_top_issues[Stats.COUNT.value] = \
        [df[issue_class].sum() for issue_class in df_top_issues[IssuesColumns.NAME.value].values]
    df_top_issues = df_top_issues.sort_values(Stats.COUNT.value, ascending=False)

    df_top_issues[Stats.RATIO.value] = df_top_issues[Stats.COUNT.value] / df.shape[0]

    return df_top_issues if n is None else df_top_issues[:n]


def get_top_issues_categories(df: pd.DataFrame, df_issues: pd.DataFrame,
                              n: Optional[int] = None, ignore_issues: List[str] = None) -> pd.DataFrame:
    df_top_issues = get_top_issues(df, df_issues, ignore_issues=ignore_issues)
    df_top_categories = df_top_issues.groupby(IssuesColumns.CATEGORY.value) \
        .sum() \
        .reset_index() \
        .sort_values(by=Stats.COUNT.value, ascending=False)

    df_top_categories[Stats.RATIO.value] = df_top_categories[Stats.COUNT.value] / df.shape[0]

    return df_top_categories if n is None else df_top_categories[:n]


def get_submissions_percent_by_feature(df: pd.DataFrame, feature: str, attr: AttrType, bins: List[int]) -> pd.DataFrame:
    """
    Divides `feature` values to intervals (a, b], (b, c] according to `bins` = [a, b, c] and submissions to groups
    according to `attr` values and then calculates percent of submissions inside submission group with feature values
    inside interval.

    The result dataframe for
        feature=`hyperstyle_issues_count`
        attr=(`difficulty`, [`easy`, `medium`, `hard`], ...)
        bins=[0, 5, 10, 15]:

    | `hyperstyle_issues_count` | `easy` | `medium` | `hard` |
    |      (0, 5]        |  0.5   |    0.2   |   0.3  |
    |      (5, 10]       |  0.3   |    0.7   |   0.6  |
    |      (10, 15]      |  0.2   |    0.1   |   0.1  |

    """

    attr = get_attr(attr)

    result = {}

    for value in attr.values:
        df_value = df[df[attr.name] == value]
        intervals = pd.cut(df_value[feature], bins=bins)
        result[value] = df_value.groupby(intervals).size() / df_value.shape[0]

    df_result = pd.DataFrame.from_dict(result)
    df_result = df_result.reset_index()
    return df_result


def get_submissions_percent_by_issues(df: pd.DataFrame, df_issues: pd.DataFrame, attr: Optional[AttrType] = None,
                                      by_type: bool = False, sort: bool = True) -> pd.DataFrame:
    """
    Divides submissions into groups according to `attr` values and for each group calculates percent of submissions
    with each issue (issue class or issue type).

    The result dataframe for
        attr=(`difficulty`, [`easy`, `medium`, `hard`], ...)

    | `issue`                 | `count`| `easy` | `medium` | `hard` |
    | `WhitespaceAroundCheck` | 322885 |  0.5   |   0.2    |   0.3  |
    | `MagicNumberCheck`      | 164371 |  0.1   |   0.2    |   0.3  |
    |           ...           |  ...   |  ...   |   ...    |   ...  |

    """

    issues_stats = {
        Stats.ISSUE.value: df_issues[IssuesColumns.CATEGORY.value if by_type else IssuesColumns.NAME.value].values,
        Stats.COUNT.value: [df[issue_class].sum() for issue_class in df_issues[IssuesColumns.NAME.value].values],
    }

    if attr is None:
        df['submission'] = 'submission'
        attr = get_attr(('submission', ['submission']))
    else:
        attr = get_attr(attr)

    for value in attr.values:
        df_value = df[df[attr.name] == value]
        issues_stats[value] = []

        for issue_class in df_issues[IssuesColumns.NAME.value].values:
            issues_stats[value].append(df_value[issue_class].sum())

    df_stats = pd.DataFrame.from_dict(issues_stats)
    df_stats = df_stats.groupby([Stats.ISSUE.value], as_index=False).sum()
    df_stats = df_stats.sort_values(Stats.COUNT.value, ascending=False)

    for value in attr.values:
        df_stats[value] = df_stats[value] / df[df[attr.name] == value].shape[0]

    if sort:
        return df_stats.sort_values(Stats.COUNT.value, ascending=False)

    return merge_dfs(df_issues[[IssuesColumns.NAME.value]], df_stats,
                     left_on=IssuesColumns.NAME.value,
                     right_on=Stats.ISSUE.value).drop(columns=[IssuesColumns.NAME.value])


def get_client_stats(df: pd.DataFrame) -> pd.DataFrame:
    """ For each client series e.x. [web, idea, web] count number of submissions series. """

    df_client_stats = df[[SubmissionColumns.GROUP.value, SubmissionColumns.TOTAL_ATTEMPTS.value,
                          SubmissionColumns.CLIENT_SERIES.value]] \
        .groupby([SubmissionColumns.CLIENT_SERIES.value, SubmissionColumns.TOTAL_ATTEMPTS.value]) \
        .count().reset_index()
    df_client_stats.columns = \
        [SubmissionColumns.CLIENT_SERIES.value, SubmissionColumns.TOTAL_ATTEMPTS.value, Stats.COUNT.value]
    df_client_stats.sort_values(Stats.COUNT.value, ascending=False, inplace=True)

    return df_client_stats


def filter_by_attempts(df: pd.DataFrame, max_attempts: int, exact_attempts: bool) -> pd.DataFrame:
    if exact_attempts:
        return df[df[SubmissionColumns.TOTAL_ATTEMPTS.value] == max_attempts]
    else:
        return df[df[SubmissionColumns.TOTAL_ATTEMPTS.value] <= max_attempts]


def get_statistics_by_attempts(df: pd.DataFrame, statistics_function: Callable[[pd.DataFrame, Dict[str, Any]], None]) \
        -> Dict[str, Any]:
    series_stats_dict = {
        SubmissionColumns.ATTEMPT.value: [],
        Stats.COUNT.value: [],
    }

    for attempt in sorted(df[SubmissionColumns.ATTEMPT.value].unique()):
        df_attempt = df[df[SubmissionColumns.ATTEMPT.value] == attempt]
        series_stats_dict[SubmissionColumns.ATTEMPT.value].append(attempt)
        series_stats_dict[Stats.COUNT.value].append(df_attempt.shape[0])

        statistics_function(df_attempt, series_stats_dict)

    return series_stats_dict


def get_submissions_series_dynamic_by_feature(df: pd.DataFrame, feature: str, attr: AttrType,
                                              max_attempts: int = 3, exact_attempts: bool = True, is_mean=True):
    """
    For attempt count feature value change is submissions which divided by attribute values.
    Submissions can be filtered to analyze submissions with less then `max_attempts` total attempts or
    exact `max_attempts` if exact_attempts=True.
    """

    attr = get_attr(attr)
    df = filter_by_attempts(df, max_attempts, exact_attempts)

    def get_feature_change(df_attempt: pd.DataFrame, stats_dict: Dict[str, List]):
        for value in attr.values:

            if value not in stats_dict:
                stats_dict[value] = []

            df_value = df_attempt[df_attempt[attr.name] == value]
            feature_value = df_value[feature].mean() if is_mean else df_value[feature].median()
            stats_dict[value].append(feature_value)

    series_stats_dict = get_statistics_by_attempts(df, get_feature_change)

    return pd.DataFrame.from_dict(series_stats_dict)


def get_issue_key_column(by_type: bool) -> str:
    return IssuesColumns.CATEGORY.value if by_type else IssuesColumns.NAME.value


def get_submissions_series_issues_dynamic(df: pd.DataFrame, df_issues: pd.DataFrame, max_attempts: int = 3,
                                          exact_attempts: bool = True, by_type=False, is_mean=True):
    """
    Form dataframe for issues count change analysis.
    For each attempt and issue class/type count percent os submissions with this issue.
    Submissions can be filtered to analyze submissions with less then `max_attempts` total attempts or
    exact `max_attempts` if exact_attempts=True.

    The result dataframe:

    | attempt |  WhitespaceAroundCheck |  MagicNumberCheck   | ... |
    |    0    |         0.312          |       0.5324        | ... |
    |    1    |         0.12           |       0.324         | ... |
    |    2    |         0.02           |       0.24          | ... |
    """

    df = filter_by_attempts(df, max_attempts, exact_attempts)

    def get_issues_change(df_attempt: pd.DataFrame, stats_dict: Dict[str, List]):
        for _, issue in df_issues.iterrows():
            issue_key = issue[get_issue_key_column(by_type)]
            if issue_key not in stats_dict:
                stats_dict[issue_key] = []

        for issue_key in df_issues[get_issue_key_column(by_type)].unique():
            stats_dict[issue_key].append(np.zeros(df_attempt.shape[0]))

        for _, issue in df_issues.iterrows():
            issue_key = issue[get_issue_key_column(by_type)]
            stats_dict[issue_key][-1] += df_attempt[issue[IssuesColumns.NAME.value]]

    series_stats_dict = get_statistics_by_attempts(df, get_issues_change)

    for issue_key in df_issues[get_issue_key_column(by_type)].unique():
        series_stats_dict[issue_key] = list(map(np.mean if is_mean else np.median, series_stats_dict[issue_key]))

    return pd.DataFrame.from_dict(series_stats_dict)


def get_submissions_series_client_dynamic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Form dataframe for client change analysis.
    For each attempt count number of submissions which change client (web->web, web->idea, idea->web, idea->idea).

    The result dataframe:

    | attempt |  from |  to   | count |
    |    0    |  web  |  web  |  1001 |
    |    0    |  web  |  idea |  202  |
    |    0    |  idea |  web  |  102  |
    |   ...   |  ...  |  ...  |  ...  |
    """
    clients = get_attr('client').values

    attempt = np.max(df[SubmissionColumns.TOTAL_ATTEMPTS.value].unique())

    attempt_clients = [{client_from: {client_to: 0 for client_to in clients} for client_from in clients} for _ in
                       range(attempt)]

    for _, client_series_row in df.iterrows():
        client_series = ast.literal_eval(client_series_row[SubmissionColumns.CLIENT_SERIES.value])
        count = client_series_row[Stats.COUNT.value]
        for i in range(1, len(client_series)):
            attempt_clients[i - 1][client_series[i - 1]][client_series[i]] += count

    attempt_client_dict = {'attempt': [], 'from': [], 'to': [], 'count': []}
    for i in range(attempt):
        for from_client in clients:
            for to_client in clients:
                attempt_client_dict['attempt'].append(i + 1)
                attempt_client_dict['from'].append(from_client)
                attempt_client_dict['to'].append(to_client)
                attempt_client_dict['count'].append(attempt_clients[i][from_client][to_client])

    return pd.DataFrame.from_dict(attempt_client_dict)
