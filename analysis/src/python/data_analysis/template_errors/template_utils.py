import ast
from typing import Dict, List

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version


def get_template_language_version(lang: str) -> LanguageVersion:
    # TODO: Remove when java17 language version will be added to hyperstyle.
    if lang == 'java17':
        return LanguageVersion.JAVA_15
    return get_language_version(lang)


def parse_templates_code(template_config: str) -> Dict[str, List[str]]:
    templates_code = ast.literal_eval(template_config)
    for lang, template_code in templates_code.items():
        templates_code[lang] = split_code_to_lines(template_code)
    return templates_code


def parse_template_issue_positions(positions: str) -> List[int]:
    return list(map(int, positions.split(', ')))
