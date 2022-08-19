import ast
from typing import Dict, List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines


def parse_template_code(df_steps: pd.DataFrame) -> pd.DataFrame:
    # Steps gathered from Database in format of str
    if StepColumns.CODE_TEMPLATE.value in df_steps.columns:
        return df_steps[StepColumns.CODE_TEMPLATE.value].apply(parse_template_code_from_str)

    # Steps gathered from API in format of dict
    if StepColumns.CODE_TEMPLATES.value in df_steps:
        return df_steps[StepColumns.CODE_TEMPLATES.value].apply(parse_template_code_from_dict)

    raise NotImplementedError('Can not find a function to parse templates!')


def parse_template_code_from_dict(template_dict: str) -> Dict[str, List[str]]:
    templates_code = ast.literal_eval(template_dict)
    for lang, template_code in templates_code.items():
        templates_code[lang] = parse_template_code_from_str(template_code)
    return templates_code


def parse_template_code_from_str(template_str: str) -> List[str]:
    return split_code_to_lines(template_str)


def parse_template_issue_positions(positions: str) -> List[int]:
    return list(map(int, positions.split(', ')))
