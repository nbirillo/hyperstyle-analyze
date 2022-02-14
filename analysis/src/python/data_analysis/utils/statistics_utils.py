import logging
from typing import Callable

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import append_df, write_df


def save_chunk(df: pd.DataFrame, df_path: str, chunk_index: int):
    if chunk_index == 0:
        write_df(df, df_path)
    else:
        append_df(df, df_path)


def get_statistics_by_group(df: pd.DataFrame, df_statistics_path: str, chunk_size: int, func: Callable):
    """ Process given dataframe dividing into chunks by group of range `chunk_size`. """

    min_group, max_group = df[SubmissionColumns.GROUP.value].min(), df[SubmissionColumns.GROUP.value].max()

    logging.info(f'Groups range: [{min_group}, {max_group}]')

    for i in range(min_group, max_group + 1, chunk_size):
        min_group_index, max_group_index = i, i + chunk_size - 1
        logging.info(f'Processing {i}-th chunk with groups: [{min_group_index}, {max_group_index})')

        logging.info('Selecting dataframe chunk')
        df_chunk = df[df[SubmissionColumns.GROUP.value].between(min_group_index, max_group_index, inclusive=True)]

        df_grouped_chunk = df_chunk.groupby([SubmissionColumns.GROUP.value], as_index=False)

        logging.info('Applying function')
        df_chunk_statistics = df_grouped_chunk.apply(func)

        logging.info('Saving chunk result')
        save_chunk(df_chunk_statistics, df_statistics_path, i)
