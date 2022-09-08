import argparse
import logging
import sys

from analysis.src.python.utils.df_utils import filter_df_by_iterable_value, merge_dfs, read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_output_filename
from analysis.src.python.utils.logging_utils import configure_logger


def filer_datasets(first_dataset_path: str, second_dataset_path: str, first_column: str, second_column: str,
                   result_path: str):
    df_first = read_df(first_dataset_path)
    logging.info(f'First dataset {first_dataset_path} initial count: {df_first.shape[0]}')
    df_second = read_df(second_dataset_path)
    logging.info(f'First dataset {second_dataset_path} initial count: {df_second.shape[0]}')

    df_compiled = merge_dfs(df_first, df_second, first_column, second_column)

    df_first = filter_df_by_iterable_value(df_first, first_column, df_compiled[first_column])
    logging.info(f'First dataset {first_dataset_path} final count: {df_first.shape[0]}')
    df_second = filter_df_by_iterable_value(df_second, second_column, df_compiled[second_column])
    logging.info(f'First dataset {second_dataset_path} final count: {df_second.shape[0]}')

    result_path = create_directory(result_path)
    write_df(df_first, result_path / get_output_filename(first_dataset_path))
    write_df(df_second, result_path / get_output_filename(second_dataset_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('first_dataset_path', type=str, help='Path to .csv file with first dataset.')
    parser.add_argument('second_dataset_path', type=str, help='Path to .csv file with second dataset.')
    parser.add_argument('first_column', type=str, help='Column in first dataset to filter.')
    parser.add_argument('second_column', type=str, help='Column in second dataset to filter.')
    parser.add_argument('result_path', type=str, help='Path to directory where to save filtered datasets.')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.second_dataset_path, 'filter', args.log_path)

    filer_datasets(args.first_dataset_path, args.second_dataset_path, args.first_column, args.second_column,
                   args.result_path)
