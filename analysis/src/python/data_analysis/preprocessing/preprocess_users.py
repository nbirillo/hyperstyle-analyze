import argparse
import logging
import sys
from typing import Optional, Tuple

from analysis.src.python.data_analysis.model.column_name import Level, UserColumns
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_user_level_tag(passed_problems: int, level_borders: Tuple[int, int]) -> str:
    """ Defines user's level. If < level_borders[0] -- low, > level_borders[1] -- high, otherwise average. """

    if passed_problems < level_borders[0]:
        return Level.LOW.value
    if passed_problems > level_borders[1]:
        return Level.HIGH.value
    return Level.AVERAGE.value


def preprocess_users(users_path: str, preprocessed_users_path: Optional[str], level_borders: Tuple[int, int]):
    """ Set level to each user according to `level_borders`. """

    df_users = read_df(users_path)
    logging.info(f"Users initial shape: {df_users.shape}")

    df_users[UserColumns.LEVEL.value] = df_users[UserColumns.PASSED_PROBLEMS.value] \
        .apply(get_user_level_tag, level_borders=level_borders)
    logging.info(f"Set users level with borders {level_borders}:\n"
                 f"{df_users[UserColumns.LEVEL.value].value_counts()}")

    logging.info(f"Users final shape: {df_users.shape}")
    logging.info(f"Saving users to {preprocessed_users_path}")
    write_df(df_users, preprocessed_users_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('users_path', type=str, help='Path to .csv file with users.')
    parser.add_argument('preprocessed_users_path', type=str, nargs='?', default=None,
                        help='Path to .csv file where preprocessed users will be saved.')
    parser.add_argument('--level-borders', '-lb', type=Tuple[int, int], default=(20, 150),
                        help='Passed topics count to consider user level as low, average or high.')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    if args.preprocessed_users_path is None:
        args.preprocessed_users_path = args.users_path

    configure_logger(args.preprocessed_users_path, 'preprocess', args.log_path)

    preprocess_users(args.users_path, args.preprocessed_users_path, args.level_borders)
