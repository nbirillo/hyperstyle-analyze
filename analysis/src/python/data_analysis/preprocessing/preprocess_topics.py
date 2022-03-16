import argparse
import ast
import logging
import sys
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import TopicColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger


def build_topics_tree(df_topics: pd.DataFrame) -> Tuple[Dict[int, List[int]], List[int]]:
    """ Build topic thee for given dataset of topics, setting topic as a parent if it is mentioned in prerequisites. """

    logging.info("Building topics tree")

    topics_tree = {topic[TopicColumns.ID.value]: [] for i, topic in df_topics.iterrows()}
    roots = []
    for _, topic in df_topics.iterrows():
        prerequisites = ast.literal_eval((topic[TopicColumns.PREREQUISITES.value]))
        if len(prerequisites) == 0:
            roots.append(topic[TopicColumns.ID.value])
        for prerequisite in prerequisites:
            if prerequisite not in topics_tree:
                print(prerequisite)
            else:
                topics_tree[prerequisite].append(topic[TopicColumns.ID.value])

    topics_tree = {topic: list(set(children)) for topic, children in topics_tree.items()}
    return topics_tree, roots


def get_topics_depth(df_topics: pd.DataFrame) -> Dict[int, int]:
    """ Apply BFS algorithm to order topics and calculate depth. """

    logging.info("Calculating topics depth")
    topics_tree, roots = build_topics_tree(df_topics)
    topics_tree_depth = {}
    queue = []
    for root in roots:
        topics_tree_depth[root] = 0
        queue.append(root)

    while len(queue) != 0:
        topic_id = queue.pop(0)
        for child_topic_id in topics_tree[topic_id]:
            if child_topic_id not in topics_tree_depth:
                topics_tree_depth[child_topic_id] = topics_tree_depth[topic_id] + 1
                queue.append(child_topic_id)
    return topics_tree_depth


def get_topics_prerequisites_tree(df_topics: pd.DataFrame) -> Dict[int, Set[int]]:
    """ Build topic thee for given dataset of topics, setting topic as a parent if it is mentioned in prerequisites. """

    logging.info("Building topics tree")

    prerequisites = {topic[TopicColumns.ID.value]: [] for i, topic in df_topics.iterrows()}

    for _, topic in df_topics.iterrows():
        topic_id = topic[TopicColumns.ID.value]
        prerequisites[topic_id] = set(ast.literal_eval((topic[TopicColumns.PREREQUISITES.value])))

        for prerequisite in prerequisites[topic_id]:
            if prerequisite not in prerequisites:
                logging.info(f'Have no information about topic {prerequisite}')
                exit(0)

    return prerequisites


def get_topics_prerequisites_count_recursive(topic_id: int,
                                             topics_prerequisites_tree: Dict[int, Set[int]],
                                             topics_prerequisites: Dict[int, Set[int]]) -> int:
    """ Lazy recursive algorithm to calculate number of unique prerequisites for each topic. """

    if topic_id not in topics_prerequisites:

        topics_prerequisites[topic_id] = set(topics_prerequisites_tree[topic_id])

        for prerequisite in topics_prerequisites_tree[topic_id]:
            if prerequisite not in topics_prerequisites:
                get_topics_prerequisites_count_recursive(prerequisite, topics_prerequisites_tree, topics_prerequisites)
            topics_prerequisites[topic_id].update(topics_prerequisites[prerequisite])

    return len(topics_prerequisites[topic_id])


def get_topics_prerequisites_count(df_topics: pd.DataFrame) -> Dict[int, int]:
    """ Apply lazy recursive algorithm to calculate number of unique prerequisites for each topic. """

    logging.info("Calculating topics prerequisites count")
    topics_prerequisites_tree = get_topics_prerequisites_tree(df_topics)
    topics_topics_prerequisites_count = {}
    topics_prerequisites = {}

    for topic_id in df_topics[TopicColumns.ID.value]:
        topics_topics_prerequisites_count[topic_id] = \
            get_topics_prerequisites_count_recursive(topic_id, topics_prerequisites_tree, topics_prerequisites)

    return topics_topics_prerequisites_count


def preprocess_topics(topics_path: str, preprocessed_topics_path: Optional[str]):
    """ Build topic tree and calculate depth for each topics in tree. """

    df_topics = read_df(topics_path)
    logging.info(f"Topics initial shape: {df_topics.shape}")

    df_topics = df_topics[
        [TopicColumns.ID.value, TopicColumns.PREREQUISITES.value, TopicColumns.CHILDREN.value,
         TopicColumns.HAS_STEPS.value, TopicColumns.HIERARCHY.value, TopicColumns.TOPOLOGICAL_INDEX.value,
         TopicColumns.TITLE.value, TopicColumns.ROOT_ID.value, TopicColumns.ROOT_TITLE.value, TopicColumns.URL.value,
         ]]

    topics_depth = get_topics_depth(df_topics)
    df_topics[TopicColumns.DEPTH.value] = df_topics[TopicColumns.ID.value] \
        .apply(lambda topic_id: topics_depth.get(topic_id, None))

    logging.info(f"Set topics depth:\n{df_topics[TopicColumns.DEPTH.value].value_counts()}")

    topics_prerequisites_count = get_topics_prerequisites_count(df_topics)
    df_topics[TopicColumns.PREREQUISITES_COUNT.value] = df_topics[TopicColumns.ID.value] \
        .apply(lambda topic_id: topics_prerequisites_count.get(topic_id, None))

    logging.info(f"Set topics prerequisites count:\n{df_topics[TopicColumns.PREREQUISITES_COUNT.value].value_counts()}")

    logging.info(f"Topics final shape: {df_topics.shape}")
    logging.info(f"Saving topics to {preprocessed_topics_path}")
    write_df(df_topics, preprocessed_topics_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics info.')
    parser.add_argument('preprocessed_topics_path', type=str, nargs='?', default=None,
                        help='Path to .csv file where preprocessed users will be saved.')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    if args.preprocessed_topics_path is None:
        args.preprocessed_topics_path = args.topics_path

    configure_logger(args.preprocessed_topics_path, 'preprocess', args.log_path)

    preprocess_topics(args.topics_path, args.preprocessed_topics_path)
