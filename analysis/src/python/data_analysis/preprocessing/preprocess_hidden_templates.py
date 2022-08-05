import argparse
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code, split_code_to_lines
from analysis.src.python.utils.df_utils import apply, read_df, write_df


class TemplateField(Enum):
    HEADER = '::header'
    CODE = '::code'
    FOOTER = '::footer'

    @staticmethod
    def from_value(value: str) -> Optional['TemplateField']:
        try:
            return TemplateField(value)
        except ValueError:
            return None


class Template:
    _field_to_content: Dict[TemplateField, str]

    def __init__(self, template: Optional[str]):
        self._field_to_content = {}

        if template is not None:
            self._field_to_content = self._parse_template(template)

    @staticmethod
    def _parse_template(template: str) -> Dict[TemplateField, str]:
        lines = split_code_to_lines(template)

        lines_by_field = defaultdict(list)
        current_field = None
        for line in lines:
            if line.startswith('::'):
                current_field = TemplateField.from_value(line.strip())
                continue

            if current_field is not None:
                lines_by_field[current_field].append(line)

        return {field: merge_lines_to_code(lines).strip('\n') for field, lines in lines_by_field.items()}

    def compile_template(
        self,
        new_field_content: Optional[Dict[TemplateField, str]] = None,
        separate_fields: bool = True,
    ) -> str:
        if new_field_content is not None:
            for field, content in new_field_content.items():
                self._field_to_content[field] = content

        if separate_fields:
            for field, content in self._field_to_content.items():
                self._field_to_content[field] = content + '\n'

        header = self._field_to_content.get(TemplateField.HEADER)
        code = self._field_to_content.get(TemplateField.CODE)
        footer = self._field_to_content.get(TemplateField.FOOTER)

        fields = list(filter(None, [header, code, footer]))

        return merge_lines_to_code(fields)


def _substitute_code_in_template(row: pd.Series) -> str:
    code = row[SubmissionColumns.CODE.value]
    template_content = row[SubmissionColumns.HIDDEN_CODE_TEMPLATE.value]

    if pd.isna(template_content):
        return code

    return Template(template_content).compile_template({TemplateField.CODE: code})


def preprocess_templates(submissions: pd.DataFrame) -> pd.DataFrame:
    return apply(submissions, SubmissionColumns.CODE.value, _substitute_code_in_template, pass_row=True)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        'preprocessed_submissions_path',
        type=lambda value: Path(value).absolute(),
        nargs='?',
        default=None,
        help='Path to .csv file where to save the processed submissions.',
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    submissions = read_df(args.submissions_path)
    submissions = preprocess_templates(submissions)

    if args.output_path is None:
        args.output_path = args.submissions_path

    write_df(submissions, args.output_path)


if __name__ == '__main__':
    main()
