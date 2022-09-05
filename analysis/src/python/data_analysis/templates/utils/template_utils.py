import ast
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines


def parse_template_code(df_steps: pd.DataFrame, lang: Optional[str]) -> pd.DataFrame:
    return df_steps.apply(parse_template_code_from_step, lang=lang)


def parse_template_code_from_step(step: pd.Series, lang: Optional[str]) -> List[str]:
    # Steps gathered from Database in format of str
    if StepColumns.CODE_TEMPLATE.value in step:
        return parse_template_code_from_str(step[StepColumns.CODE_TEMPLATE.value])

    # Steps gathered from API in format of dict
    if StepColumns.CODE_TEMPLATES.value in step and lang is not None:
        return parse_template_code_from_dict(step[StepColumns.CODE_TEMPLATES.value], lang=lang)

    raise Exception('Can not parse template code! '
                    'Check the language is specified and dataset has corresponding columns!')


def parse_template_code_from_dict(template_dict: str, lang: Optional[str]) -> List[str]:
    templates_code = ast.literal_eval(template_dict)
    return split_code_to_lines(templates_code[lang])


def parse_template_code_from_str(template_str: str) -> List[str]:
    return split_code_to_lines(template_str)


def parse_template_issue_positions(positions: str) -> List[int]:
    return list(map(int, positions.split(', ')))
