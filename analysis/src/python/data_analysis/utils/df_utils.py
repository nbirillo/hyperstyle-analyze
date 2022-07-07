import os
from typing import Callable, Dict, List

import pandas as pd
from pandarallel import pandarallel


def _apply_to_row(row: pd.Series, column: str, func: Callable) -> pd.Series:
    """ Apply `func` to data in `column` of dataframe's `raw`. """

    copy_row = row.copy()
    copy_row[column] = func(copy_row[column])
    return copy_row


def apply(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """ Apply `func` to  data in `column` of dataframe `df`. """

    return df.apply(lambda row: _apply_to_row(row, column, func), axis=1)


def parallel_apply(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """ Parallel apply `func` to  data in `column` of dataframe `df`. """

    pandarallel.initialize(nb_workers=4)
    return df.parallel_apply(lambda raw: _apply_to_row(raw, column, func), axis=1)


def rename_columns(df: pd.DataFrame, columns: Dict[str, str]) -> pd.DataFrame:
    """ Rename columns of given dataframe `df`. """

    return df.rename(columns=columns)


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """ Drop columns from given dataframe `df`. """

    return df.drop(labels=columns, axis=1)


def merge_dfs(df_left: pd.DataFrame, df_right: pd.DataFrame, left_on: str, right_on: str, how='inner') -> pd.DataFrame:
    """ Merge two given dataframes on `left_on` = `right_on`. Duplicated columns are removed. """

    df_merged = pd.merge(df_left, df_right, how=how, left_on=left_on, right_on=right_on, suffixes=('', '_extra'))
    df_merged.drop(df_merged.filter(regex='_extra$').columns.tolist(), axis=1, inplace=True)
    return df_merged


def read_df(path: str) -> pd.DataFrame:
    """ Read dataframe from given .csv file. """

    return pd.read_csv(path)


def write_df(df: pd.DataFrame, path: str):
    """ Write dataframe to given .csv file. """

    df.to_csv(path, index=False)


def append_df(df: pd.DataFrame, path: str):
    """ Append data to dataframe by given .csv file. """

    if not os.path.exists(path):
        write_df(df, path)
    else:
        df.to_csv(path, index=False, mode='a', header=False)
