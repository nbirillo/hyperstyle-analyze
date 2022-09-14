import argparse
import logging
import sys

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns, TopicColumns
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_output_filename
from analysis.src.python.utils.logging_utils import configure_logger


def compile_dataset(submissions_path: str, steps_path: str, topics_path: str, result_path: str):
    """ Create directory with result dataset to analyse: select data which present in all datasets. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial count: {df_submissions.shape[0]}')
    df_steps = read_df(steps_path)
    logging.info(f'Steps initial count: {df_steps.shape[0]}')
    df_topics = read_df(topics_path)
    logging.info(f'Topics initial size: {df_topics.shape[0]}')

    df_compile = merge_dfs(df_submissions, df_steps, SubmissionColumns.STEP_ID.value, StepColumns.ID.value)
    df_compile = merge_dfs(df_compile, df_topics, StepColumns.TOPIC_ID.value, TopicColumns.ID.value)

    logging.info(f'Compiled dataset shape: {df_compile.shape}')

    df_submissions = df_submissions[
        df_submissions[SubmissionColumns.ID.value].isin(df_compile[SubmissionColumns.ID.value])]
    logging.info(f'Select {df_submissions.shape[0]} submissions which presented in compile dataset')

    df_steps = df_steps[df_steps[StepColumns.ID.value].isin(df_compile[SubmissionColumns.STEP_ID.value])]
    logging.info(f'Select {df_steps.shape[0]} steps which presented in compile dataset')

    df_topics = df_topics[df_topics[TopicColumns.ID.value].isin(df_compile[StepColumns.TOPIC_ID.value])]
    logging.info(f'Select {df_topics.shape[0]} topics which presented in compile dataset')

    result_path = create_directory(result_path)
    write_df(df_submissions, result_path / get_output_filename(submissions_path))
    logging.info(f'Submissions final count: {df_submissions.shape[0]}')
    write_df(df_steps, result_path / get_output_filename(steps_path))
    logging.info(f'Steps final count: {df_steps.shape[0]}')
    write_df(df_topics, result_path / get_output_filename(topics_path))
    logging.info(f'Topics final count: {df_topics.shape[0]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('result_path', type=str, help='Path to directory to save compiled datasets.')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.submissions_path, 'compile', args.log_path)

    compile_dataset(args.submissions_path, args.steps_path, args.topics_path, args.result_path)
