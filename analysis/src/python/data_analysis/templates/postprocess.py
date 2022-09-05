import argparse
import ast
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.utils.code_utils import get_code_with_issue_comment
from analysis.src.python.data_collection.api.platform_objects import Object
from analysis.src.python.evaluation.tools.utils.saving_utils import save_solution_to_file
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.utils.file_utils import create_directory


@dataclass(frozen=True)
class ProcessingConfig(Object):
    repetitive_issues_path: str
    result_path: str
    submissions_path: Optional[str]
    issues_column: Optional[str]
    freq_to_remove: float
    freq_to_separate_template_issues: float
    freq_to_separate_rare_and_common_issues: float
    solutions_number: int
    base_task_url: str


def parse_config(args) -> ProcessingConfig:
    return ProcessingConfig(
        repetitive_issues_path=args.repetitive_issues_path,
        submissions_path=args.submissions_path,
        result_path=args.result_path,
        issues_column=args.issues_column,
        freq_to_remove=args.freq_to_remove / 100,
        freq_to_separate_template_issues=args.freq_to_separate_template_issues / 100,
        freq_to_separate_rare_and_common_issues=args.freq_to_separate_rare_and_common_issues / 100,
        solutions_number=args.solutions_number,
        base_task_url=args.base_task_url.rstrip('/'),
    )


def get_with_and_without_pos_in_template(df_repetitive_issues: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_with_pos_in_template = df_repetitive_issues[
        df_repetitive_issues[SubmissionColumns.POS_IN_TEMPLATE.value].notnull()]

    df_without_pos_in_template = df_repetitive_issues[
        df_repetitive_issues[SubmissionColumns.POS_IN_TEMPLATE.value].isnull()]

    return df_with_pos_in_template, df_without_pos_in_template


def split_by_freq(df_repetitive_issues: pd.DataFrame,
                  freq_to_separate_template_issues: float,
                  freq_to_separate_rare_and_common_issues: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ Split issues to group according to their frequency. """

    df_template_issues = df_repetitive_issues.loc[
        df_repetitive_issues[TemplateColumns.FREQUENCY.value] > freq_to_separate_template_issues]
    df_typical_issues = df_repetitive_issues.loc[
        df_repetitive_issues[TemplateColumns.FREQUENCY.value] <= freq_to_separate_template_issues]
    df_rare_typical_issues = df_typical_issues.loc[
        df_typical_issues[TemplateColumns.FREQUENCY.value] <= freq_to_separate_rare_and_common_issues]
    df_common_typical_issues = df_typical_issues.loc[
        (df_typical_issues[TemplateColumns.FREQUENCY.value] > freq_to_separate_rare_and_common_issues)]
    return df_template_issues, df_rare_typical_issues, df_common_typical_issues


def filter_by_freq(df_repetitive_issues: pd.DataFrame, freq_to_remove: float) -> pd.DataFrame:
    """ Filter issues with frequency lower or equal to freq_to_remove. """

    return df_repetitive_issues.loc[df_repetitive_issues[TemplateColumns.FREQUENCY.value] > freq_to_remove]


def save_submission_samples(df_repetitive_issues: pd.DataFrame,
                            df_submissions: pd.DataFrame,
                            config: ProcessingConfig):
    sample_path = Path(config.result_path) / 'samples'
    for _, repetitive_issue in df_repetitive_issues.iterrows():
        issue_name = repetitive_issue[IssuesColumns.NAME.value]
        issue_position = repetitive_issue[TemplateColumns.POS_IN_TEMPLATE.value]
        issue_line_number = None if math.isnan(issue_position) else issue_position + 1

        submission_group_ids = ast.literal_eval(repetitive_issue[TemplateColumns.GROUPS.value])

        for group_id in submission_group_ids[:config.solutions_number]:
            submission_series = df_submissions[df_submissions[SubmissionColumns.GROUP.value] == group_id]
            for _, submission in submission_series.iterrows():
                submission_with_issue = submission.copy()
                submission_with_issue[SubmissionColumns.CODE.value] = get_code_with_issue_comment(
                    submission, config.issues_column,
                    issue_name=issue_name,
                    issue_line_number=issue_line_number)

                step_id = submission[SubmissionColumns.STEP_ID.value]
                attempt = submission[SubmissionColumns.ATTEMPT.value]
                submission_path = sample_path / str(step_id) / issue_name / str(group_id)
                save_solution_to_file(submission_with_issue, submission_path, f'attempt_{attempt}')


def add_additional_info(
        df_repetitive_issues: pd.DataFrame,
        config: ProcessingConfig,
        df_submissions: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    df_repetitive_issues[StepColumns.URL.value] = df_repetitive_issues[SubmissionColumns.STEP_ID.value] \
        .apply(lambda step_id: f'{config.base_task_url}/{step_id}')
    if df_submissions is not None:
        save_submission_samples(df_repetitive_issues, df_submissions, config)
    df_repetitive_issues = df_repetitive_issues.sort_values(SubmissionColumns.STEP_ID.value)
    return df_repetitive_issues


def process_repetitive_issues(df_repetitive_issues: pd.DataFrame,
                              df_submissions: pd.DataFrame,
                              config: ProcessingConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ Postprocess given dataframe with """
    df_repetitive_issues = filter_by_freq(df_repetitive_issues, config.freq_to_remove)
    df_repetitive_issues = add_additional_info(df_repetitive_issues, df_submissions=df_submissions, config=config)
    df_repetitive_issues_split = split_by_freq(df_repetitive_issues,
                                               config.freq_to_separate_template_issues,
                                               config.freq_to_separate_rare_and_common_issues)
    return df_repetitive_issues_split


def main(config: ProcessingConfig):
    df_repetitive_issues = read_df(config.repetitive_issues_path)
    df_submissions = read_df(config.submissions_path)

    df_template_issues, df_rare_typical_issues, df_common_typical_issues = \
        process_repetitive_issues(df_repetitive_issues, df_submissions, config)

    base_path = Path(config.result_path) / 'issues'
    create_directory(base_path)
    write_df(df_template_issues, base_path / f'template_issues{AnalysisExtension.CSV.value}')
    write_df(df_rare_typical_issues, base_path / f'rare_typical_issues{AnalysisExtension.CSV.value}')
    write_df(df_common_typical_issues, base_path / f'common_typical_issues{AnalysisExtension.CSV.value}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('repetitive_issues_path', type=str,
                        help='Path to .csv file with repetitive issues from submissions.')
    parser.add_argument('result_path', type=str, help='Path to resulting folder with processed issues.')
    parser.add_argument('submissions_path', type=str, default=None,
                        help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues_column', type=str, default=None,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('-fr', '--freq-to-remove', type=int, default=10,
                        help='The threshold of frequency to remove issues in the final table.')
    parser.add_argument('-fs', '--freq-to-separate-rare-and-common-issues', type=int, default=25,
                        help='The threshold of frequency to separate typical issues into rare and common.')
    parser.add_argument('-ft', '--freq-to-separate-template-issues', type=int, default=51,
                        help='The threshold of frequency to keep issues in the final table.')
    parser.add_argument('-n', '--solutions-number', type=int, default=5,
                        help='Tne number of random students solutions that should be gathered for each task.')
    parser.add_argument('-url', '--base-task-url', type=str, default='https://hyperskill.org/learn/step',
                        help='Base url to the tasks on an education platform.')

    args = parser.parse_args(sys.argv[1:])
    main(parse_config(args))
