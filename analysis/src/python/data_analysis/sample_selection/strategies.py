import logging
from enum import Enum, unique
from typing import Dict, Optional, Set

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.sample_selection.config import ConfigArguments, DEFAULT_INCLUDE_BOUNDARIES

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

    def execute(
        self,
        submissions: pd.DataFrame,
        number_of_samples: int,
        random_state: Optional[int],
        args: Dict,
    ) -> pd.DataFrame:
        function = GROUP_STRATEGY_TO_FUNCTION.get(self)
        if function is None:
            raise NotImplementedError('This strategy has no implementation.')

        return function(submissions, number_of_samples, random_state, args)


def get_samples_by_code_lines_count(
    submissions: pd.DataFrame,
    number_of_samples: int,
    random_state: Optional[int],
    args: Dict,
) -> pd.DataFrame:
    """
    Get samples by code lines count.

    `submissions` must contain the `code_lines_count` column.
    The `args` must contain either the `count` value or the `bins` value.

    `count` may be:
    1) An integer number `step`.
       In this case only those code line counts which are multiples of `step` will be used for grouping.
       Also, if you want to include boundaries, you can do it with the `include_boundaries` flag.
    2) An array of integers.
       In this case only those code line counts which are specified in the array will be used for grouping.

    The `bins` must be an array of integers in which the boundaries of the bins will be specified.

    The `number_of_samples` sets the number of samples to be in the group.
    If the number of elements in the group is less than `number_of_samples`, all elements in their group will be taken.

    The `random_seed` sets a seed for the random generator.
    """

    if ConfigArguments.COUNT.value in args:
        if isinstance(args[ConfigArguments.COUNT.value], list):
            count_range = args[ConfigArguments.COUNT.value]
        else:
            count_range = list(
                range(
                    args[ConfigArguments.COUNT.value],
                    submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max() + 1,
                    args[ConfigArguments.COUNT.value],
                ),
            )

            if args.get(ConfigArguments.INCLUDE_BOUNDARIES.value, DEFAULT_INCLUDE_BOUNDARIES):
                if submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].min() not in count_range:
                    count_range.append(submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].min())

                if submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max() not in count_range:
                    count_range.append(submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].max())

        submissions_samples = (
            submissions[submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value].isin(count_range)]
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
    random_state: Optional[int],
    args: Dict,
) -> pd.DataFrame:
    """
    Get samples by step ID.

    `submissions` must contain the `step_id` column.
    The `args` must contain the `ids` value. The `ids` is an array of integers by which the grouping will be done.

    The `number_of_samples` sets the number of samples to be in the group.
    If the number of elements in the group is less than `number_of_samples`, all elements in their group will be taken.

    The `random_seed` sets a seed for the random generator.
    """

    return (
        submissions[submissions[SubmissionColumns.STEP_ID.value].isin(args[ConfigArguments.IDS.value])]
        .groupby(SubmissionColumns.STEP_ID.value, as_index=False)
        .apply(lambda group: group.sample(min(number_of_samples, len(group)), random_state=random_state))
        .reset_index(drop=True)
    )


GROUP_STRATEGY_TO_FUNCTION = {
    GroupStrategy.BY_CODE_LINES_COUNT: get_samples_by_code_lines_count,
    GroupStrategy.BY_STEP_ID: get_samples_by_step_id,
}
