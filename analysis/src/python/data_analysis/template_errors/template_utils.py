import ast
from typing import Dict, List

from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines


def parse_templates_code(template_config: str) -> Dict[str, List[str]]:
    templates_code = ast.literal_eval(template_config)
    for lang, template_code in templates_code.items():
        templates_code[lang] = split_code_to_lines(template_code)
    return templates_code


def parse_template_issue_positions(positions: str) -> List[int]:
    return list(map(int, positions.split(', ')))
