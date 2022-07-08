import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import pandas as pd
from pandarallel import pandarallel

from analysis.src.python.utils.extension_utils import AnalysisExtension, get_restricted_extension
from analysis.src.python.utils.xlsx_utils import read_df_from_xlsx, write_df_to_xlsx


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


def filter_df_by_iterable_value(df: pd.DataFrame, column: str, value: Iterable) -> pd.DataFrame:
    return df.loc[df[column].isin(value)]


def filter_df_by_single_value(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    return df.loc[df[column] == value]


def drop_duplicates(df: pd.DataFrame, column: str, keep: str = 'last') -> pd.DataFrame:
    return df.drop_duplicates(column, keep=keep).reset_index(drop=True)


def rename_columns(df: pd.DataFrame, columns: Dict[str, str]) -> pd.DataFrame:
    """ Rename columns of given dataframe `df`. """

    return df.rename(columns=columns)


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """ Drop columns from given dataframe `df`. """

    return df.drop(labels=columns, axis=1)


def equal_df(expected_df: pd.DataFrame, actual_df: pd.DataFrame) -> bool:
    return (expected_df.empty and actual_df.empty) or expected_df.reset_index(drop=True).equals(
        actual_df.reset_index(drop=True))


def merge_dfs(df_left: pd.DataFrame, df_right: pd.DataFrame, left_on: str, right_on: str, how='inner') -> pd.DataFrame:
    """ Merge two given dataframes on `left_on` = `right_on`. Duplicated columns are removed. """

    df_merged = pd.merge(df_left, df_right, how=how, left_on=left_on, right_on=right_on, suffixes=('', '_extra'))
    df_merged.drop(df_merged.filter(regex='_extra$').columns.tolist(), axis=1, inplace=True)
    return df_merged


def read_df(path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """ Read dataframe from given .csv or .xlsx file `Sheet1` sheet. """

    ext = get_restricted_extension(path, [AnalysisExtension.CSV, AnalysisExtension.XLSX])
    if ext == AnalysisExtension.CSV:
        df = pd.read_csv(path)
    else:
        df = read_df_from_xlsx(path)
    return df


def write_df(df: pd.DataFrame, path: Union[str, Path]):
    """ Write dataframe to given .csv or .xlsx file `Sheet1` sheet. """

    ext = get_restricted_extension(path, [AnalysisExtension.CSV, AnalysisExtension.XLSX])
    if ext == AnalysisExtension.CSV:
        df.to_csv(path, index=False)
    else:
        write_df_to_xlsx(df, path, index=False)


def append_df(df: pd.DataFrame, path: Union[str, Path]):
    """ Append dataframe by given .csv file or .xlsx file `Sheet1` sheet. """

    if os.path.exists(path):
        ext = get_restricted_extension(path, [AnalysisExtension.CSV, AnalysisExtension.XLSX])
        if ext == AnalysisExtension.CSV:
            df.to_csv(path, index=False, mode='a', header=False)
        else:
            write_df_to_xlsx(df, path, index=False, mode='a', header=False)
    else:
        write_df(df, path)
