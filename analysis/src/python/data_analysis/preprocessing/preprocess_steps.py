import argparse
import ast
import logging
import sys
from typing import Dict, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from analysis.src.python.data_analysis.model.column_name import CommentsColumns, Complexity, Difficulty, LikesColumns, \
    StepColumns, TopicColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utlis import configure_logger
from analysis.src.python.data_analysis.utils.stats_utils import calculate_code_lines_count


def get_steps_complexity_tag(depth: int, complexity_borders: Tuple[int, int]) -> Complexity:
    """ Defines step's complexity.
    If < complexity_borders[0] -- shallow, > complexity_borders[1] -- deep, otherwise middle. """

    if depth < complexity_borders[0]:
        return Complexity.SHALLOW
    if depth > complexity_borders[1]:
        return Complexity.DEEP
    return Complexity.MIDDLE


def get_steps_difficulty_tag(success_rate: int, difficulty_borders: Tuple[int, int]) -> Difficulty:
    """ Defines step's difficulty.
    If < difficulty_borders[0] -- easy, > difficulty_borders[1] -- hard, otherwise medium. """

    if success_rate < difficulty_borders[0]:
        return Difficulty.EASY
    if success_rate > difficulty_borders[1]:
        return Difficulty.HARD
    return Difficulty.MEDIUM


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
            like_statistics_dict[like_tag] = like_statistics[StepColumns.TOTAL_COUNT.value]

    return pd.Series(like_statistics_dict, dtype='int32')


def get_comments_statistics(comments_statistics: str) -> pd.Series:
    """ Defines step's comments statistics. For each comment tag return its count. """

    comments_statistics = ast.literal_eval(comments_statistics)

    comment_statistics_dict = {}
    for comment_statistics in comments_statistics:
        comment_tag = CommentsColumns(comment_statistics[StepColumns.THREAD])
        comment_statistics_dict[comment_tag] = comment_statistics[StepColumns.TOTAL_COUNT.value]

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
        StepColumns.HAS_HEADER_FOOTER: check_header_footer(block[StepColumns.OPTIONS.value]),
        StepColumns.HAS_TEMPLATE: check_template(block[StepColumns.OPTIONS.value]),
        StepColumns.HAS_CONSTANT: check_constant_in_assignment(block[StepColumns.TEXT.value]),
    }

    return pd.Series(blocks_info, dtype='bool')


def preprocess_steps(steps_path: str, topics_path: str, preprocessed_steps_path: str,
                     complexity_borders: Tuple[int, int],
                     difficulty_borders: Tuple[int, int],
                     filter_with_header_footer: bool):
    """ Add steps complexity, difficulty tags, related to topic depth, set has_template and has_constant parameters. """

    df_steps = read_df(steps_path)
    logging.info(f"Steps initial shape: {df_steps.shape}")

    df_steps = df_steps[[StepColumns.ID, StepColumns.LIKES, StepColumns.COMMENTS, StepColumns.BLOCK,
                         StepColumns.TOPIC, StepColumns.SECONDS_TO_COMPLETE, StepColumns.SOLVED_BY,
                         StepColumns.SUCCESS_RATE, StepColumns.POPULAR_IDE, StepColumns.IS_IDE_COMPATIBLE,
                         StepColumns.TITLE, StepColumns.URL]]
    logging.info(f"Select steps columns subset. Steps shape: {df_steps.shape}")

    df_topics = read_df(topics_path)

    df_steps = df_steps[df_steps[StepColumns.TOPIC].notnull()]
    logging.info(f"Filter steps without topics. Steps shape: {df_steps.shape}")

    df_steps[StepColumns.DEPTH] = merge_dfs(df_steps, df_topics, StepColumns.TOPIC, TopicColumns.ID)[TopicColumns.DEPTH]
    df_steps[StepColumns.DEPTH] = df_steps[StepColumns.DEPTH].fillna(0).astype('int32')
    logging.info(f"Set submissions depth:\n{df_steps[StepColumns.DEPTH].value_counts()}")

    df_steps[StepColumns.COMPLEXITY] = df_steps[StepColumns.DEPTH] \
        .apply(get_steps_complexity_tag, complexity_borders=complexity_borders)
    logging.info(f"Set submissions complexity:\n{df_steps[StepColumns.COMPLEXITY].value_counts()}")
    df_steps[StepColumns.DIFFICULTY] = df_steps[StepColumns.SUCCESS_RATE] \
        .apply(get_steps_difficulty_tag, difficulty_borders=difficulty_borders)
    logging.info(f"Set submissions difficulty:\n{df_steps[StepColumns.DIFFICULTY].value_counts()}")

    df_block_info = df_steps[StepColumns.BLOCK].apply(get_block_info)
    df_comments_info = df_steps[StepColumns.COMMENTS].apply(get_comments_statistics).fillna(0).astype('int32')
    df_likes_info = df_steps[StepColumns.LIKES].apply(get_likes_statistics).fillna(0).astype('int32')

    df_steps = pd.concat([df_steps, df_block_info, df_comments_info, df_likes_info], axis=1)
    logging.info(f"Add block, comments and likes info to steps. Steps shape: {df_steps.shape}")
    logging.info(f"Set submissions header/footer:\n{df_steps[StepColumns.HAS_HEADER_FOOTER].value_counts()}")
    logging.info(f"Set submissions template:\n{df_steps[StepColumns.HAS_TEMPLATE].value_counts()}")
    logging.info(f"Set submissions constant:\n{df_steps[StepColumns.HAS_CONSTANT].value_counts()}")

    if filter_with_header_footer:
        df_steps = df_steps[~df_steps[StepColumns.HAS_HEADER_FOOTER]]
        logging.info(f"Filter steps with header footer. Steps shape: {df_steps.shape}")

    logging.info(f"Steps final shape: {df_steps.shape}")
    logging.info(f"Saving steps to {preprocessed_steps_path}")
    write_df(df_steps, preprocessed_steps_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('preprocessed_steps_path', type=str, nargs='?', default=None,
                        help='Path to .csv file where preprocessed steps will be saved .')

    parser.add_argument('--complexity-borders', type=Tuple[int, int], default=(3, 7),
                        help='Topic depth to consider steps as shallow, middle or deep.')
    parser.add_argument('--difficulty-borders', type=Tuple[int, int], default=(1 / 3, 2 / 3),
                        help='Steps success rate to consider steps as easy, medium or hard.')
    parser.add_argument('--filter-with-header-footer', type=bool, default=True,
                        help='Filter steps with header or footer.')

    args = parser.parse_args(sys.argv[1:])
    if args.preprocessed_steps_path is None:
        args.preprocessed_steps_path = args.steps_path

    configure_logger(args.preprocessed_steps_path, 'preprocess')

    preprocess_steps(args.steps_path, args.topics_path, args.preprocessed_steps_path,
                     args.complexity_borders, args.difficulty_borders,
                     args.filter_with_header_footer)
