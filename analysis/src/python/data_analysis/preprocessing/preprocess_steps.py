import argparse
import ast
import sys
from typing import Dict, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from analysis.src.python.data_analysis.model.column_name import CommentsColumns, Complexity, Difficulty, LikesColumns, \
    StepColumns, TopicColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.data_analysis.utils.stats_utils import calculate_code_lines_count


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


def get_step_likes_tag(likes_value: int) -> Optional[LikesColumns]:
    """ Defines step's likes tag according to mapping rule. """

    value_to_tag = {
        -2: LikesColumns.ANGRY,
        -1: LikesColumns.SAD,
        0: LikesColumns.NEUTRAL,
        1: LikesColumns.HAPPY,
        2: LikesColumns.LOVE,
    }

    return value_to_tag.get(likes_value, None)


def get_likes_statistics(likes_statistics: str) -> pd.Series:
    """ Defines step's likes statistics. For each like tag return its count. """

    likes_statistics = ast.literal_eval(likes_statistics)

    like_statistics_dict = {}
    for like_statistics in likes_statistics:
        like_tag = get_step_likes_tag(like_statistics[StepColumns.VALUE.value])
        if like_tag is not None:
            like_statistics_dict[like_tag.value] = like_statistics[StepColumns.TOTAL_COUNT.value]

    return pd.Series(like_statistics_dict, dtype='int32')


def get_comments_statistics(comments_statistics: str) -> pd.Series:
    """ Defines step's comments statistics. For each comment tag return its count. """

    comments_statistics = ast.literal_eval(comments_statistics)

    comment_statistics_dict = {}
    for comment_statistics in comments_statistics:
        comment_tag = CommentsColumns(comment_statistics[StepColumns.THREAD])
        comment_statistics_dict[comment_tag.value] = comment_statistics[StepColumns.TOTAL_COUNT.value]

    return pd.Series(comment_statistics_dict, dtype='int32')


def check_header_footer(options: str) -> bool:
    """ Check if there is header or footer in steps assignment template. """

    header_footer_lines_count = 0

    if options[StepColumns.HEADER_LINES_COUNT.value] is not None:
        header_footer_lines_count += sum(dict(options[StepColumns.HEADER_LINES_COUNT.value]).values())
    if options[StepColumns.FOOTER_LINES_COUNT.value] is not None:
        header_footer_lines_count += sum(dict(options[StepColumns.FOOTER_LINES_COUNT.value]).values())

    return header_footer_lines_count > 0


def check_template(options: Dict) -> bool:
    """ Check if there is a template code in steps assignment. """

    code_template_lines_count = 0
    if options[StepColumns.CODE_TEMPLATES.value] is not None:
        code_template_lines_count += sum(map(calculate_code_lines_count,
                                             dict(options[StepColumns.CODE_TEMPLATES.value]).values()))
    return code_template_lines_count > 0


def check_constant_in_assignment(assignment: str) -> bool:
    """ Check step's assignment contains constants [used to test hypothesis about MagicNumber issue]. """

    parsed_html = BeautifulSoup(assignment)
    return any(char.isdigit() for char in parsed_html.text)


def get_block_info(step_block: str) -> pd.Series:
    """ Get information from step's block about templates and constants in assignment. """

    block = ast.literal_eval(step_block)

    blocks_info = {
        StepColumns.HAS_HEADER_FOOTER.value: check_header_footer(block[StepColumns.OPTIONS.value]),
        StepColumns.HAS_TEMPLATE.value: check_template(block[StepColumns.OPTIONS.value]),
        StepColumns.HAS_CONSTANT.value: check_constant_in_assignment(block[StepColumns.TEXT.value])
    }

    return pd.Series(blocks_info, dtype='bool')


def preprocess_steps(steps_path: str, topics_path: str,
                     complexity_borders: Tuple[int, int],
                     difficulty_borders: Tuple[int, int]):
    """ Add steps complexity, difficulty tags, related to topic depth, set has_template and has_constant parameters. """

    df_steps = read_df(steps_path)
    df_topics = read_df(topics_path)

    df_steps = df_steps[
        [StepColumns.ID.value, StepColumns.LIKES.value, StepColumns.COMMENTS.value, StepColumns.BLOCK.value,
         StepColumns.TOPIC.value, StepColumns.SECONDS_TO_COMPLETE.value, StepColumns.SOLVED_BY.value,
         StepColumns.SUCCESS_RATE, StepColumns.POPULAR_IDE.value, StepColumns.IS_IDE_COMPATIBLE.value,
         StepColumns.TITLE.value, StepColumns.URL.value
         ]]

    df_steps = df_steps[df_steps[StepColumns.TOPIC.value].notnull()]
    df_steps[StepColumns.DEPTH.value] = \
        merge_dfs(df_steps, df_topics, StepColumns.TOPIC, TopicColumns.ID)[TopicColumns.DEPTH].fillna(0).astype('int32')

    df_steps[StepColumns.COMPLEXITY.value] = df_steps[StepColumns.DEPTH.value] \
        .apply(get_steps_complexity_tag, complexity_borders=complexity_borders)
    df_steps[StepColumns.DIFFICULTY.value] = df_steps[StepColumns.SUCCESS_RATE.value] \
        .apply(get_steps_difficulty_tag, difficulty_borders=difficulty_borders)

    df_block_info = df_steps[StepColumns.BLOCK.value].apply(get_block_info)
    df_comments_info = df_steps[StepColumns.COMMENTS.value].apply(get_comments_statistics).fillna(0).astype('int32')
    df_likes_info = df_steps[StepColumns.LIKES.value].apply(get_likes_statistics).fillna(0).astype('int32')

    df_steps = pd.concat([df_steps, df_block_info, df_comments_info, df_likes_info], axis=1)

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
