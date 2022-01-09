import argparse
import sys
from typing import Tuple

from analysis.src.python.data_analysis.model.column_name import Level, UserColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df


def get_user_level_tag(passed_problems: int, level_borders: Tuple[int, int]):
    """ Defines user's level. If < level_borders[0] -- low, > level_borders[1] -- high, otherwise average. """

    if passed_problems < level_borders[0]:
        return Level.LOW.value
    if passed_problems > level_borders[1]:
        return Level.HIGH.value
    return Level.AVERAGE.value


def preprocess_users(users_path: str, level_borders: Tuple[int, int]):
    df_users = read_df(users_path)
    df_users[UserColumns.LEVEL.value] = df_users[UserColumns.PASSED_PROBLEMS.value] \
        .apply(get_user_level_tag, level_borders=level_borders)
    write_df(df_users, users_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('users_path', type=str, help='Path to .csv file with users.')
    parser.add_argument('--level-borders', '-lb', type=Tuple[int, int], default=(20, 150),
                        help='Passed topics count to consider user level as low, average or high.')

    args = parser.parse_args(sys.argv[1:])
    preprocess_users(args.users_path, args.level_borders)
