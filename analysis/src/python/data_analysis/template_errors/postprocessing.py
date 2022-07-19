import argparse
import json
import random
import sys
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from data_analysis.model.column_name import SubmissionColumns
from evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder
from utils.df_utils import read_df, write_df
from utils.file_utils import create_directory, create_file


def filter_duplicates_function(filter_duplicates_type: str):
    if filter_duplicates_type == 'max':
        return lambda row: row.loc[row[SubmissionColumns.FREQUENCY.value].idxmax()]
    if filter_duplicates_type == 'min':
        return lambda row: row.loc[row[SubmissionColumns.FREQUENCY.value].idxmax()]
    raise AttributeError(f'The --filter-duplicates arg {filter_duplicates_type} is unknown!')


def get_none_and_not_none_freq(templates_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    templates_with_none_position = templates_df[templates_df[SubmissionColumns.POS_IN_TEMPLATE.value].isnull()]
    templates_with_not_none_position = templates_df[templates_df[SubmissionColumns.POS_IN_TEMPLATE.value].notnull()]
    return templates_with_none_position, templates_with_not_none_position


def group_by_and_filter_by_freq(templates_df: pd.DataFrame, lambda_function) -> pd.DataFrame:
    return templates_df.groupby([SubmissionColumns.STEP_ID.value, SubmissionColumns.RAW_ISSUE_CLASS.value],
                                group_keys=False).apply(lambda_function)


def filter_duplicates(templates_df: pd.DataFrame, filter_duplicates_type: str) -> pd.DataFrame:
    templates_with_none_position, templates_with_not_none_position = get_none_and_not_none_freq(templates_df)
    filtered_with_none_position = group_by_and_filter_by_freq(templates_with_none_position,
                                                              filter_duplicates_function(filter_duplicates_type))
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
        max_template_freq: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lowest_threshold = 0.1
    middle_threshold = 0.25
    biggest_threshold = max_template_freq / 100
    # Filter issues with frequency les than 10%
    filtered = templates_df.loc[templates_df[SubmissionColumns.FREQUENCY.value] > lowest_threshold]
    template_issues = filtered[filtered[SubmissionColumns.FREQUENCY.value] > biggest_threshold]
    rare_typical_issues = filtered[(filtered[SubmissionColumns.FREQUENCY.value] > lowest_threshold) & (
            filtered[SubmissionColumns.FREQUENCY.value] <= middle_threshold)]
    common_typical_issues = filtered[(filtered[SubmissionColumns.FREQUENCY.value] > middle_threshold) & (
            filtered[SubmissionColumns.FREQUENCY.value] <= biggest_threshold)]
    return template_issues, rare_typical_issues, common_typical_issues


def find_user_solutions(
        template_issues_df: pd.DataFrame,
        raw_issues_df: pd.DataFrame,
        output_path: str,
        n: int = 5,
        to_add_description: bool = True,
) -> pd.DataFrame:
    base_path = f'{output_path}/solutions'
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
        while current_attempt < n:
            row_number = random.randint(0, step_rows.shape[0] - 1)
            if row_number in visited_rows or row_number in wrong_rows:
                continue
            issues = json.loads(step_rows[SubmissionColumns.RAW_ISSUES.value].iloc[row_number], cls=RawIssueDecoder)
            current_issues = list(
                filter(lambda i: i.origin_class == row[SubmissionColumns.RAW_ISSUE_CLASS.value], issues))
            if len(current_issues) == 0:
                wrong_rows.append(row_number)
                continue
            file_path = Path(f"{cur_path}/solution_{current_attempt}.java")
            create_file(file_path, step_rows["code"].iloc[row_number])
            visited_rows.append(row_number)
            descriptions.append(current_issues[random.randint(0, len(current_issues) - 1)].description)
            current_attempt += 1
        if to_add_description:
            final_descriptions.append(descriptions[random.randint(0, len(descriptions) - 1)])
    template_issues_df[description] = final_descriptions
    return template_issues_df


def add_additional_info(
        template_issues_df: pd.DataFrame,
        output_path: str,
        raw_issues_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    template_issues_df['task_link'] = template_issues_df.apply(
        lambda row: f'https://hyperskill.org/learn/step/{row[SubmissionColumns.STEP_ID.value]}', axis=1)
    if raw_issues_df is not None:
        template_issues_df = find_user_solutions(template_issues_df, raw_issues_df, output_path)
    template_issues_df[SubmissionColumns.STEP_ID.value] = pd.to_numeric(
        template_issues_df[SubmissionColumns.STEP_ID.value])
    template_issues_df.sort_values(SubmissionColumns.STEP_ID.value, inplace=True)
    return template_issues_df


def get_raw_issue_df(raw_issues_path: Optional[str]) -> Optional[pd.DataFrame]:
    if raw_issues_path is None:
        return None
    return read_df(raw_issues_path)


def save_results(
        output_path: str,
        template_issues: pd.DataFrame,
        rare_typical_issues: pd.DataFrame,
        common_typical_issues: pd.DataFrame,
):
    base_path = f'{output_path}/issues'
    create_directory(base_path)
    write_df(template_issues, f'{base_path}/template_issues.csv')
    write_df(rare_typical_issues, f'{base_path}/rare_typical_issues.csv')
    write_df(common_typical_issues, f'{base_path}/common_typical_issues.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('templates_search_result', type=str, help='Path to .csv file with issues in templates.')
    parser.add_argument('result_path', type=str, help='Path to resulting folder with processed issues.')
    parser.add_argument('raw_issues_path', type=str, help='Path to .csv file with raw issues.', default=None)
    parser.add_argument('-fd', '--filter-duplicates', type=str, default='max',
                        help='Function for union the same issues. Possible functions: "max", "min".')
    parser.add_argument('-fk', '--freq-to-keep', type=int, default=51,
                        help='The threshold of frequency to keep issues in the final table.')

    args = parser.parse_args(sys.argv[1:])
    templates_df = read_df(args.templates_search_result)
    raw_issues_df = get_raw_issue_df(args.raw_issues_path)

    templates_df = filter_duplicates(templates_df, args.filter_duplicates)
    templates_df = add_additional_info(templates_df, args.result_path, raw_issues_df)
    template_issues, rare_typical_issues, common_typical_issues = filter_by_freq(templates_df, args.freq_to_keep)
    save_results(args.result_path, template_issues, rare_typical_issues, common_typical_issues)
