import logging
from enum import Enum, unique
from typing import Dict, Optional, Set

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.sample_selection.config import ConfigArguments

logger = logging.getLogger(__name__)


@unique
class GroupStrategy(Enum):
    BY_CODE_LINES_COUNT = 'by_code_lines_count'
    BY_STEP_ID = 'by_step_id'

    @classmethod
    def strategies(cls) -> Set[str]:
        return {strategy.value for strategy in cls}

    @classmethod
    def from_config(cls, config: Dict) -> Optional['GroupStrategy']:
        strategies = list(filter(lambda strategy: strategy in GroupStrategy.strategies(), list(config.keys())))
        if not strategies:
            return None

        return GroupStrategy(strategies[0])

    def execute(self, submissions: pd.DataFrame, number_of_samples: int, random_state: int, args: Dict) -> pd.DataFrame:
        function = GROUP_STRATEGY_TO_FUNCTION.get(self)
        if function is None:
            raise NotImplementedError('This strategy has no implementation.')

        return function(submissions, number_of_samples, random_state, args)


def get_samples_by_code_lines_count(
    submissions: pd.DataFrame,
    number_of_samples: int,
    random_state: int,
    args: Dict,
) -> pd.DataFrame:
    """
    Get samples by code lines count.

    `submissions` must contain a `code_lines_count` column.
    The `args` must contain either the `length` value or the `bins` value.

    `length` may be:
    1) An integer number `step`.
       In this case only those code line counts which are multiples of `step` will be used for grouping.
       Also, the bounding values of the `code_lines_count` column will be included.
    2) An array of integers.
       In this case only those code line counts which are specified in the array will be used for grouping.

    The `bins` must be an array of integers in which the boundaries of the bins will be specified.

    The `number_of_samples` sets the number of samples to be in the group.
    If the number of elements in the group is less than `number_of_samples`, all elements in their group will be taken.

    The `random_seed` sets a seed for the random generator.
    """

    if ConfigArguments.LENGTH.value in args:
        if isinstance(args[ConfigArguments.LENGTH.value], list):
            lines_range = args[ConfigArguments.LENGTH.value]
        else:
            lines_range = list(
                range(
                    args[ConfigArguments.LENGTH.value],
                    submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max() + 1,
                    args[ConfigArguments.LENGTH.value],
                )
            )

            # Add left boundary
            if 1 not in lines_range:
                lines_range.append(1)

            # Add right boundary
            if submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max() not in lines_range:
                lines_range.append(submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max())

        submissions_samples = (
            submissions[submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].isin(lines_range)]
            .groupby(SubmissionStatsColumns.CODE_LINES_COUNT.value)
            .apply(lambda group: group.sample(min(number_of_samples, len(group)), random_state=random_state))
            .reset_index(drop=True)
        )

    else:  # ConfigArguments.BINS.value in args
        bins = args[ConfigArguments.BINS.value]
        submissions_samples = (
            submissions.groupby(pd.cut(submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value], bins))
            .apply(lambda group: group.sample(min(number_of_samples, len(group)), random_state=random_state))
            .reset_index(drop=True)
        )

    return submissions_samples


def get_samples_by_step_id(
    submissions: pd.DataFrame,
    number_of_samples: int,
    random_state: int,
    args: Dict,
) -> pd.DataFrame:
    """
    Get samples by step ID.

    `submissions` must contain a `step_id` column.
    The `args` must contain the `ids` value. The `ids` is an array of integers by which the grouping will be done.

    The `number_of_samples` sets the number of samples to be in the group.
    If the number of elements in the group is less than `number_of_samples`, all elements in their group will be taken.

    The `random_seed` sets a seed for the random generator.
    """

    return (
        submissions[submissions[SubmissionColumns.STEP_ID.value].isin(args[ConfigArguments.IDS.value])]
        .groupby(SubmissionColumns.STEP_ID.value, as_index=False)
        .apply(lambda group: group.sample(min(number_of_samples, len(group))), random_state=random_state)
        .reset_index(drop=True)
    )


GROUP_STRATEGY_TO_FUNCTION = {
    GroupStrategy.BY_CODE_LINES_COUNT: get_samples_by_code_lines_count,
    GroupStrategy.BY_STEP_ID: get_samples_by_step_id,
}
