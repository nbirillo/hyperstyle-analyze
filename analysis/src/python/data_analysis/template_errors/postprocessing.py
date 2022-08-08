import argparse
import json
import random
import sys
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from hyperstyle.src.python.review.common.file_system import Extension

from data_analysis.model.column_name import StepColumns, SubmissionColumns
from data_analysis.template_errors.models.postprocessing_models import PostprocessingConfig
from evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder
from utils.df_utils import read_df, write_df
from utils.extension_utils import AnalysisExtension
from utils.file_utils import create_directory, create_file

from analysis.src.python.utils.numpy_utils import AggregateFunction


def filter_duplicates_function(filter_duplicates_type: AggregateFunction):
    if filter_duplicates_type == AggregateFunction.MAX:
        return lambda row: row.loc[row[SubmissionColumns.FREQUENCY.value].idxmax()]
    if filter_duplicates_type == AggregateFunction.MIN:
        return lambda row: row.loc[row[SubmissionColumns.FREQUENCY.value].idxmax()]
    raise AttributeError(f'The --filter-duplicates arg {filter_duplicates_type.value} is unknown!')


def get_none_and_not_none_freq(templates_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    templates_with_none_position = templates_df[templates_df[SubmissionColumns.POS_IN_TEMPLATE.value].isnull()]
    templates_with_not_none_position = templates_df[templates_df[SubmissionColumns.POS_IN_TEMPLATE.value].notnull()]
    return templates_with_none_position, templates_with_not_none_position


def group_by_and_filter_by_freq(templates_df: pd.DataFrame, lambda_function) -> pd.DataFrame:
    return templates_df.groupby([SubmissionColumns.STEP_ID.value, SubmissionColumns.RAW_ISSUE_CLASS.value],
                                group_keys=False).apply(lambda_function)


def filter_duplicates(templates_df: pd.DataFrame, config: PostprocessingConfig) -> pd.DataFrame:
    templates_with_none_position, templates_with_not_none_position = get_none_and_not_none_freq(templates_df)
    filtered_with_none_position = group_by_and_filter_by_freq(templates_with_none_position,
                                                              filter_duplicates_function(
                                                                  config.filter_duplicates_type,
                                                              ))
    templates_with_not_none_position[SubmissionColumns.POS_IN_TEMPLATE.value] = templates_with_not_none_position[
        SubmissionColumns.POS_IN_TEMPLATE.value].apply(lambda x: str(int(x)))
    templates_with_not_none_position = templates_with_not_none_position \
        .sort_values([SubmissionColumns.STEP_ID.value,
                      SubmissionColumns.RAW_ISSUE_CLASS.value,
                      SubmissionColumns.POS_IN_TEMPLATE.value],
                     ascending=[True, True, True])
    merged_pos = templates_with_not_none_position.groupby(
        [SubmissionColumns.STEP_ID.value, SubmissionColumns.RAW_ISSUE_CLASS.value], group_keys=False).agg(
        {SubmissionColumns.STEP_ID.value: 'first', SubmissionColumns.RAW_ISSUE_CLASS.value: 'first',
         SubmissionColumns.FREQUENCY.value: 'first', SubmissionColumns.POS_IN_TEMPLATE.value: ', '.join})
    return merged_pos.append(filtered_with_none_position).reset_index(drop=True)


def filter_by_freq(
        templates_df: pd.DataFrame,
        config: PostprocessingConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Filter issues with frequency les than freq_to_remove
    filtered = templates_df.loc[templates_df[SubmissionColumns.FREQUENCY.value] > config.freq_to_remove]
    template_issues = filtered[filtered[SubmissionColumns.FREQUENCY.value] > config.freq_to_keep]
    rare_typical_issues = filtered[(filtered[SubmissionColumns.FREQUENCY.value] > config.freq_to_remove) & (
            filtered[SubmissionColumns.FREQUENCY.value] <= config.freq_to_separate_typical_and_template)]
    common_typical_issues = filtered[
        (filtered[SubmissionColumns.FREQUENCY.value] > config.freq_to_separate_typical_and_template) & (
                filtered[SubmissionColumns.FREQUENCY.value] <= config.freq_to_keep)]
    return template_issues, rare_typical_issues, common_typical_issues


def generate_index(length: int) -> int:
    return random.randint(0, length - 1)


def find_user_solutions(
        template_issues_df: pd.DataFrame,
        raw_issues_df: pd.DataFrame,
        config: PostprocessingConfig,
) -> pd.DataFrame:
    base_path = f'{config.result_path}/solutions'
    description = 'description'
    final_descriptions = []
    for _, row in template_issues_df.iterrows():
        step_rows = raw_issues_df.loc[
            raw_issues_df[SubmissionColumns.STEP_ID.value] == row[SubmissionColumns.STEP_ID.value]]
        current_attempt = 0
        visited_rows = []
        wrong_rows = []
        descriptions = []
        cur_path = f'{base_path}/{row[SubmissionColumns.STEP_ID.value]}/{row[SubmissionColumns.RAW_ISSUE_CLASS.value]}'
        create_directory(cur_path)
        while current_attempt < config.number_of_solutions:
            row_number = generate_index(step_rows.shape[0])
            if row_number in visited_rows or row_number in wrong_rows:
                continue
            issues = json.loads(step_rows[SubmissionColumns.RAW_ISSUES.value].iloc[row_number], cls=RawIssueDecoder)
            current_issues = list(
                filter(lambda i: i.origin_class == row[SubmissionColumns.RAW_ISSUE_CLASS.value], issues))
            if len(current_issues) == 0:
                wrong_rows.append(row_number)
                continue
            file_path = Path(f"{cur_path}/solution_{current_attempt}{Extension.JAVA.value}")
            next(create_file(file_path, step_rows["code"].iloc[row_number]))
            visited_rows.append(row_number)
            descriptions.append(current_issues[generate_index(len(current_issues))].description)
            current_attempt += 1
        if config.to_add_description:
            final_descriptions.append(descriptions[generate_index(len(descriptions))])
    template_issues_df[description] = final_descriptions
    return template_issues_df


def add_additional_info(
        template_issues_df: pd.DataFrame,
        config: PostprocessingConfig,
        raw_issues_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    template_issues_df[StepColumns.URL.value] = template_issues_df.apply(
        lambda row: f'{config.base_task_url}/{row[SubmissionColumns.STEP_ID.value]}', axis=1)
    if raw_issues_df is not None:
        template_issues_df = find_user_solutions(template_issues_df, raw_issues_df, config)
    template_issues_df[SubmissionColumns.STEP_ID.value] = pd.to_numeric(
        template_issues_df[SubmissionColumns.STEP_ID.value])
    template_issues_df.sort_values(SubmissionColumns.STEP_ID.value, inplace=True)
    return template_issues_df


def get_raw_issue_df(raw_issues_path: Optional[str]) -> Optional[pd.DataFrame]:
    if raw_issues_path is None:
        return None
    return read_df(raw_issues_path)


def save_results(
        output_path: Path,
        template_issues: pd.DataFrame,
        rare_typical_issues: pd.DataFrame,
        common_typical_issues: pd.DataFrame,
):
    base_path = output_path / 'issues'
    create_directory(base_path)
    write_df(template_issues, base_path / f'template_issues{AnalysisExtension.CSV.value}')
    write_df(rare_typical_issues, base_path / f'rare_typical_issues{AnalysisExtension.CSV.value}')
    write_df(common_typical_issues, base_path / f'common_typical_issues{AnalysisExtension.CSV.value}')


def parse_args(args) -> PostprocessingConfig:
    return PostprocessingConfig(
        templates_search_result_path=args.templates_search_result,
        result_path=args.result_path,
        raw_issues_path=args.raw_issues_path,
        filter_duplicates_type=args.filter_duplicates_type,
        freq_to_remove=args.freq_to_remove / 100,
        freq_to_keep=args.freq_to_keep / 100,
        freq_to_separate_typical_and_template=args.freq_to_separate_typical_and_template / 100,
        number_of_solutions=args.number_of_solutions,
        to_add_description=args.add_description,
        base_task_url=args.base_task_url.rstrip('/'),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('templates_search_result', type=str, help='Path to .csv file with issues in templates.')
    parser.add_argument('result_path', type=str, help='Path to resulting folder with processed issues.')
    parser.add_argument('raw_issues_path', type=str, help='Path to .csv file with raw issues.', default=None)
    parser.add_argument('-fd', '--filter-duplicates-type', type=str, default=AggregateFunction.MAX.value,
                        choices=[AggregateFunction.MIN.value, AggregateFunction.MAX.value],
                        help=f'Function for union the same issues. '
                             f'Possible functions: {[AggregateFunction.MIN.value, AggregateFunction.MAX.value]}.')
    parser.add_argument('-fk', '--freq-to-keep', type=int, default=51,
                        help='The threshold of frequency to keep issues in the final table.')
    parser.add_argument('-fr', '--freq-to-remove', type=int, default=10,
                        help='The threshold of frequency to remove issues in the final table.')
    parser.add_argument('-fs', '--freq-to-separate', type=int, default=25,
                        help='The threshold of frequency to separate issues into typical and template in the table.')
    parser.add_argument('-n', '--number-of-solutions', type=int, default=5,
                        help='Tne number of random students solutions that should be gathered for each task.')
    parser.add_argument('--add-description',
                        action='store_false',
                        help='The argument determines whether the description of each issue should be added')
    parser.add_argument('-url', '--base-task-url', type=str, default='https://hyperskill.org/learn/step',
                        help='Base url to the tasks on an education platform.')

    args = parser.parse_args(sys.argv[1:])
    conf = parse_args(args)

    templates_df = read_df(conf.templates_search_result_path)
    raw_issues_df = get_raw_issue_df(conf.raw_issues_path)

    templates_df = filter_duplicates(templates_df, conf)
    templates_df = add_additional_info(templates_df, raw_issues_df=raw_issues_df, config=conf)
    template_issues, rare_typical_issues, common_typical_issues = filter_by_freq(templates_df, conf)
    save_results(conf.result_path, template_issues, rare_typical_issues, common_typical_issues)
