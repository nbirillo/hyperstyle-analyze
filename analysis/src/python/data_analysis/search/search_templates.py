import argparse
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.search.utils.comment_utils import get_issue_comment
from analysis.src.python.data_analysis.template_errors.template_utils import get_template_language_version, \
    parse_template_issue_positions, parse_templates_code
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import filter_df_by_single_value, read_df
from analysis.src.python.utils.file_utils import create_directory, create_file
from analysis.src.python.utils.logging_utils import configure_logger


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('template_issues_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('output_path', type=str, help='Path to directory with output')
    parser.add_argument('--step', type=int, default=None, help='Step to search templates for')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


def save_template(step: pd.Series, output_path: Path):
    """ Save templates with issue comments to file. """

    output_path = create_directory(output_path / f'step_{step[StepColumns.ID.value]}')
    for lang, template_code_lines in step[StepColumns.CODE_TEMPLATES.value].items():
        extension = get_template_language_version(lang).extension_by_language()
        code = merge_lines_to_code(template_code_lines)
        next(create_file(output_path / f'template_{lang}{extension.value}', content=code))


def add_issue_comment_to_template(step: pd.Series, df_templates_issues: pd.DataFrame) -> pd.Series:
    """ Add comment to row where specific issue appears in template. """

    templates_code = step[StepColumns.CODE_TEMPLATES.value]

    df_step_templates_issues = \
        filter_df_by_single_value(df_templates_issues, SubmissionColumns.STEP_ID.value, step[StepColumns.ID.value])

    for _, template_issues in df_step_templates_issues.iterrows():

        template_issue_positions = parse_template_issue_positions(
            template_issues[TemplateColumns.POS_IN_TEMPLATE.value])

        template_issue_name = template_issues[IssuesColumns.NAME.value]

        for lang, template_code_lines in templates_code.items():
            for template_issue_position in template_issue_positions:
                if template_issue_position < len(template_code_lines):
                    language_version = get_language_version(lang)
                    comment = get_issue_comment(language_version, template_issue_name, template_issue_position)
                    template_code_lines[template_issue_position] += comment

    return step


def search_templates(df_steps: pd.DataFrame,
                     df_templates_issues: pd.DataFrame,
                     output_path: Path):
    """ Search and save to `output_dir` all templates with issues comments. """

    df_templates_issues = df_templates_issues.dropna(subset=[TemplateColumns.POS_IN_TEMPLATE.value])
    df_steps[StepColumns.CODE_TEMPLATES.value] = df_steps[StepColumns.CODE_TEMPLATES.value].apply(parse_templates_code)
    df_steps.apply(add_issue_comment_to_template, df_templates_issues=df_templates_issues, axis=1)
    df_steps.apply(save_template, output_path=output_path, axis=1)


def main(steps_path: str, template_issues_path: str, step: Optional[int], issue_name: Optional[str],
         output_path: str):
    """
    Search and save to `output_dir` examples of steps submissions with and without issue.
    Pairs of step and issue can be provided directly or listed in `steps_issues_path` csv file.
    """

    output_path = create_directory(output_path)
    df_steps = read_df(steps_path)
    df_template_issues = read_df(template_issues_path)

    if step is not None:
        df_steps = filter_df_by_single_value(df_steps, StepColumns.ID.value, step)
        df_template_issues = filter_df_by_single_value(df_template_issues, SubmissionColumns.STEP_ID.value, step)

    if issue_name is not None:
        df_template_issues = filter_df_by_single_value(df_template_issues, IssuesColumns.NAME.value, issue_name)

    search_templates(df_steps, df_template_issues, output_path)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    configure_logger(args.output_dir, 'search', args.log_path)

    main(args.steps_path,
         args.template_issues_path,
         args.issue_name,
         args.step,
         args.output_dir)
