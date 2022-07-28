"""
This script will allow you to select several submission samples from certain groups.

There are several strategies for grouping data:
- 'by_code_lines_count' -- grouping is done by the 'code_lines_count' column, where the code lines count is specified.
- 'by_step_id' -- grouping is done by the 'step_id' column, where the step ID is specified.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.sample_selection.config import (
    ConfigArguments,
    DEFAULT_NUMBER_OF_SAMPLES,
    DEFAULT_RANDOM_STATE,
)
from analysis.src.python.data_analysis.sample_selection.config_validation import validate_config
from analysis.src.python.data_analysis.sample_selection.strategies import GroupStrategy
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.yaml_utils import parse_yaml

logger = logging.getLogger(__name__)


def get_submissions_samples(submissions: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Get samples from submissions using the group strategy specified in `config`.

    The number of samples in a group is specified with the `number_of_samples` argument in `config`.
    It is also possible to set a seed for the random generator using the `random_seed` argument in `config`.
    """

    number_of_samples = config.get(ConfigArguments.NUMBER_OF_SAMPLES.value, DEFAULT_NUMBER_OF_SAMPLES)
    random_state = config.get(ConfigArguments.RANDOM_STATE.value, DEFAULT_RANDOM_STATE)

    strategy = GroupStrategy.from_config(config)
    args = config[strategy.value]

    return strategy.execute(submissions, number_of_samples, random_state, args)


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        'output_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file where to save the samples.',
    )

    parser.add_argument(
        '--stats-path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with additional columns to be added.',
    )

    parser.add_argument(
        '--config',
        type=lambda value: Path(value).absolute(),
        required=True,
        help='Path to a config file. For more information, see README.',
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    config = parse_yaml(args.config)
    if not validate_config(config):
        return 1

    submissions = read_df(args.submissions_path)
    if args.stats_path is not None:
        submissions_stats = read_df(args.stats_path)
        submissions = merge_dfs(
            submissions,
            submissions_stats,
            left_on=SubmissionColumns.ID.value,
            right_on=SubmissionColumns.ID.value,
        )

    selected_submissions = get_submissions_samples(submissions, config)
    write_df(selected_submissions, args.output_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
