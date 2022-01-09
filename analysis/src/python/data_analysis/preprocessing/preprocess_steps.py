import argparse
import ast
import sys
from typing import Tuple

import pandas as pd
from bs4 import BeautifulSoup

from analysis.src.python.data_analysis.model.column_name import Complexity, Difficulty, StepColumns, TopicColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, write_df


def get_steps_complexity_tag(depth: int, complexity_borders: Tuple[int, int]) -> str:
    """ Defines step's complexity.
    If < complexity_borders[0] -- shallow, > complexity_borders[1] -- deep, otherwise middle. """

    if depth < complexity_borders[0]:
        return Complexity.SHALLOW.value
    if depth > complexity_borders[1]:
        return Complexity.DEEP.value
    return Complexity.MIDDLE.value


def get_steps_difficulty_tag(success_rate: int, difficulty_borders: Tuple[int, int]) -> str:
    """ Defines step's difficulty.
    If < difficulty_borders[0] -- easy, > difficulty_borders[1] -- hard, otherwise medium. """

    if success_rate < difficulty_borders[0]:
        return Difficulty.EASY.value
    if success_rate > difficulty_borders[1]:
        return Difficulty.HARD.value
    return Difficulty.MEDIUM.value


def count_template(step_block: str, position: str) -> int:
    """ Count number of code lines in footer or header template. """

    block = ast.literal_eval(step_block)
    options = block[StepColumns.OPTIONS.value]
    if options[position] is None:
        return 0
    return sum(dict(options[position]).values())


def check_template(step: pd.Series) -> pd.Series:
    """ Check if there is header or footer in steps template. """

    return pd.Series(step[StepColumns.HEADER_LINES_COUNT.value] > 0 or
                     step[StepColumns.FOOTER_LINES_COUNT.value] > 0)


def contains_constant_in_assignment(step_block: str) -> bool:
    """ Check step's assignment contains constants [used to test hypothesis about MagicNumber issue]. """

    block = ast.literal_eval(step_block)
    html = block[StepColumns.TEXT.value]
    parsed_html = BeautifulSoup(html)

    return any(char.isdigit() for char in parsed_html.text)


def preprocess_steps(steps_path: str, topics_path: str,
                     complexity_borders: Tuple[int, int],
                     difficulty_borders: Tuple[int, int]):
    """ Add steps complexity, difficulty tags, related to topic depth, set has_template and has_constant parameters. """

    df_steps = read_df(steps_path)
    df_topics = read_df(topics_path)

    df_steps[StepColumns.DEPTH.value] = \
        merge_dfs(df_steps, df_topics, StepColumns.TOPIC, TopicColumns.ID)[TopicColumns.DEPTH]

    df_steps[StepColumns.COMPLEXITY.value] = df_steps[StepColumns.DEPTH.value] \
        .apply(get_steps_complexity_tag, complexity_borders=complexity_borders)
    df_steps[StepColumns.DIFFICULTY.value] = df_steps[StepColumns.SUCCESS_RATE.value] \
        .apply(get_steps_difficulty_tag, difficulty_borders=difficulty_borders)

    df_steps[StepColumns.HEADER_LINES_COUNT.value] = df_steps[StepColumns.BLOCK.value] \
        .apply(count_template, position=StepColumns.HEADER_LINES_COUNT.value)
    df_steps[StepColumns.FOOTER_LINES_COUNT.value] = df_steps[StepColumns.BLOCK.value] \
        .apply(count_template, position=StepColumns.FOOTER_LINES_COUNT.value)

    df_steps[StepColumns.HAS_TEMPLATE.value] = df_steps[[StepColumns.HEADER_LINES_COUNT.value,
                                                         StepColumns.FOOTER_LINES_COUNT.value]] \
        .apply(check_template, axis=1)
    df_steps[StepColumns.HAS_CONSTANT.value] = df_steps[StepColumns.BLOCK.value] \
        .apply(contains_constant_in_assignment)
    write_df(df_steps, steps_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('--complexity-borders', '-sb', type=Tuple[int, int], default=(3, 7),
                        help='Topic depth to consider steps as shallow, middle or deep.')
    parser.add_argument('--difficulty-borders', '-db', type=Tuple[int, int], default=(1 / 3, 2 / 3),
                        help='Steps success rate to consider steps as easy, medium or hard.')

    args = parser.parse_args(sys.argv[1:])
    preprocess_steps(args.steps_path, args.topics_path,
                     args.complexity_borders, args.difficulty_borders)
