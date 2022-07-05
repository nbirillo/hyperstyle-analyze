import json
import logging
from typing import List, Set

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.quality.penalty import PenaltyIssue
from hyperstyle.src.python.review.reviewers.utils.print_review import convert_json_to_issues

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.utils.df_utils import filter_df_by_iterable_value

logger = logging.getLogger(__name__)


def filter_df_by_language(df: pd.DataFrame, languages: Set[LanguageVersion],
                          column: str = ColumnName.LANG.value) -> pd.DataFrame:
    return filter_df_by_iterable_value(df, column, set(map(lambda l: l.value, languages)))


# Find all rows and columns where two dataframes are inconsistent.
# For example:
#  row  |  column    |
#  -------------------------
#  3    | column_1   | True
#       | column_2   | True
#  -------------------------
#  4    | column_1   | True
#       | column_2   | True
# means first and second dataframes have different values
# in column_1 and in column_2 in 3-th and 4-th rows
def get_inconsistent_positions(first: pd.DataFrame, second: pd.DataFrame) -> pd.DataFrame:
    ne_stacked = (first != second).stack()
    inconsistent_positions = ne_stacked[ne_stacked]
    inconsistent_positions.index.names = [ColumnName.ROW.value, ColumnName.COLUMN.value]
    return inconsistent_positions


# Create a new dataframe with all items that are different.
# For example:
#            |       old   |   new
#  ---------------------------------
# row column |             |
# 3   grade  |  EXCELLENT  | MODERATE
# 4   grade  |  EXCELLENT  |  BAD
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


def get_issues_by_row(df: pd.DataFrame, row: int) -> List[PenaltyIssue]:
    return get_issues_from_json(df.iloc[row][ColumnName.TRACEBACK.value])
