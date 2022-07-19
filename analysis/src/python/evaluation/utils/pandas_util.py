import json
import logging
from typing import List, Set

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.quality.penalty import PenaltyIssue
from hyperstyle.src.python.review.reviewers.utils.print_review import convert_json_to_issues

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.utils.args_util import script_structure_rule
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value

logger = logging.getLogger(__name__)


def get_language_version(lang_key: str) -> LanguageVersion:
    try:
        return LanguageVersion(lang_key)
    except ValueError as e:
        logger.error(script_structure_rule)
        # We should raise KeyError since it is incorrect value for key in a column
        raise KeyError(e)


def filter_df_by_language(df: pd.DataFrame, languages: Set[LanguageVersion],
                          column: str = ColumnName.LANG.value) -> pd.DataFrame:
    return filter_df_by_iterable_value(df, column, set(map(lambda l: l.value, languages)))


# Find all rows and columns where two dataframes are inconsistent.
# For example:
#
#          |   | column_1 | column_2 |           |   | column_1 | column_2 |
#  first = | 0 |    A     |    4     |  second = | 0 |    A     |    8     |
#          | 1 |    B     |    3     |           | 1 |    C     |    3     |
#
# So the inconsistent will be multi index dataframe:
#
#                 |               |   0  |
#  inconsistent = | (0, column_2) | True |
#                 | (1, column_1) | True |
#
# Which means that the first and second dataframes have different values
# in 0-th row of column_2 (4 != 8) and in 1-th row of column_1 (B != C)
def get_inconsistent_positions(first: pd.DataFrame, second: pd.DataFrame) -> pd.DataFrame:
    ne_stacked = (first != second).stack()
    inconsistent_positions = ne_stacked[ne_stacked]
    inconsistent_positions.index.names = [ColumnName.ROW.value, ColumnName.COLUMN.value]
    return inconsistent_positions


# Create a new dataframe with all items that are different.
# For example:
#
#          |   | column_1 | column_2 |           |   | column_1 | column_2 |
#  first = | 0 |    A     |    4     |  second = | 0 |    A     |    8     |
#          | 1 |    B     |    3     |           | 1 |    C     |    3     |
#
# So the diff will be multi index dataframe:
#
#         |               |  old  |  new  |
#  diff = | (0, column_2) |   4   |   8   |
#         | (1, column_1) |   B   |   C   |
#
# Which means that the first and second dataframes have the following changes ([old] -> [new])
# in 0-th row of column_2 (4 -> 8) and in 1-th row of column_1 (B -> C)
def get_diffs(first: pd.DataFrame, second: pd.DataFrame) -> pd.DataFrame:
    changed = get_inconsistent_positions(first, second)

    difference_locations = np.where(first != second)
    changed_from = first.values[difference_locations]
    changed_to = second.values[difference_locations]
    return pd.DataFrame({
        ColumnName.OLD.value: changed_from,
        ColumnName.NEW.value: changed_to},
        index=changed.index)


def get_issues_from_json(str_json: str) -> List[PenaltyIssue]:
    parsed_json = json.loads(str_json)['issues']
    return convert_json_to_issues(parsed_json)


def get_issues_from_json_by_row(df: pd.DataFrame, row: int) -> List[PenaltyIssue]:
    return get_issues_from_json(df.iloc[row][ColumnName.TRACEBACK.value])
