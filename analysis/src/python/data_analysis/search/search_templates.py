import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepColumns, SubmissionColumns, \
    TemplateColumns
from analysis.src.python.data_analysis.template_errors.template_matching import parse_template_issue_positions, \
    parse_templates_code
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.file_utils import create_directory, create_file
from analysis.src.python.utils.logging_utils import configure_logger


def save_template(step: pd.Series, output_dir: Path):
    """ Save submission to file with extension. Easy to compare diffs. """

    output_dir = create_directory(output_dir / f'step_{step[StepColumns.ID.value]}')
    for lang, template_lines in step[StepColumns.CODE_TEMPLATES.value].items():
        try:
            extension = get_language_version(lang).extension_by_language()
        except Exception:
            continue

        code = merge_lines_to_code(template_lines)
        next(create_file(output_dir / f'template_{lang}{extension.value}', content=code))


def get_comment_to_code_line(issue_name: str, line_number: int) -> str:
    """ Add comment to given code line. """

    return f' // {issue_name} line={line_number}'


def add_issue_info_comment_to_template(step: pd.Series, df_templates_issues: pd.DataFrame) -> pd.Series:
    """ Add comment to row where specific issue appears in solution. """

    df_step_templates_issues = df_templates_issues[
        df_templates_issues[SubmissionColumns.STEP_ID.value] == step[StepColumns.ID.value]]

    templates_code = step[StepColumns.CODE_TEMPLATES.value]

    for _, template_issues in df_step_templates_issues.iterrows():

        template_issue_positions = parse_template_issue_positions(
            template_issues[TemplateColumns.POS_IN_TEMPLATE.value])

        template_issue_name = template_issues[IssuesColumns.NAME.value]

        for template_code in templates_code.values():
            for template_issue_position in template_issue_positions:
                if template_issue_position < len(template_code):
                    comment = get_comment_to_code_line(template_issue_name, template_issue_position)
                    template_code[template_issue_position] += comment

    return step


def search_templates(df_steps: pd.DataFrame,
                     df_templates_issues: pd.DataFrame,
                     output_dir: Path):
    """
    Search and save to `output_dir` examples of submissions for given `step`
    with and without given `issue_name`.
    """

    df_templates_issues = df_templates_issues.dropna(subset=[TemplateColumns.POS_IN_TEMPLATE.value])
    df_steps[StepColumns.CODE_TEMPLATES.value] = df_steps[StepColumns.CODE_TEMPLATES.value].apply(parse_templates_code)
    df_steps.apply(add_issue_info_comment_to_template, df_templates_issues=df_templates_issues, axis=1)
    df_steps.apply(save_template, output_dir=output_dir, axis=1)


def main(steps_path: str, template_issues_path: str, step: Optional[int], issue_name: Optional[str], output_dir: str):
    """
    Search and save to `output_dir` examples of steps submissions with and without issue.
    Pairs of step and issue can be provided directly or listed in `steps_issues_path` csv file.
    """

    output_dir = create_directory(output_dir)
    df_steps = read_df(steps_path)
    df_template_issues = read_df(template_issues_path)

    if step is not None:
        df_steps = df_steps[df_steps[StepColumns.ID] == step]

    if issue_name is not None:
        df_template_issues = df_template_issues[df_template_issues[IssuesColumns.NAME] == issue_name]

    search_templates(df_steps, df_template_issues, output_dir)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('template_issues_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('--issue-name', type=str, default=None, help='Issue example to search for')
    parser.add_argument('--step', type=int, default=None, help='Step to search templates for')
    parser.add_argument('output_dir', type=str, help='Path to directory with output')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.output_dir, 'search', args.log_path)

    main(args.steps_path,
         args.template_issues_path,
         args.issue_name,
         args.step,
         args.output_dir)
