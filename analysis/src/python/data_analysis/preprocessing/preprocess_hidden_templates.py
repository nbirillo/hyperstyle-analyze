import argparse
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code, split_code_to_lines
from analysis.src.python.utils.df_utils import apply, read_df, write_df


class TemplateBlock(Enum):
    HEADER = '::header'
    CODE = '::code'
    FOOTER = '::footer'

    @staticmethod
    def from_value(value: str) -> Optional['TemplateBlock']:
        try:
            return TemplateBlock(value)
        except ValueError:
            return None


class Template:
    block_to_content: Dict[TemplateBlock, str]

    def __init__(self, template: Optional[str]):
        self.block_to_content = {}

        if template is not None:
            self.block_to_content = self._parse(template)

    @staticmethod
    def _parse(template: str) -> Dict[TemplateBlock, str]:
        lines = split_code_to_lines(template)

        lines_by_block = defaultdict(list)
        current_block = None
        for line in lines:
            if line.startswith('::'):
                current_block = TemplateBlock.from_value(line.strip())
                continue

            if current_block is not None:
                lines_by_block[current_block].append(line)

        return {block: merge_lines_to_code(lines).strip('\n') for block, lines in lines_by_block.items()}

    def compile_template(
        self,
        new_block_content: Optional[Dict[TemplateBlock, str]] = None,
        separate_blocks: bool = True,
    ) -> str:
        if new_block_content is not None:
            for block, content in new_block_content.items():
                self.block_to_content[block] = content

        if separate_blocks:
            for block, content in self.block_to_content.items():
                self.block_to_content[block] = content + '\n'

        header = self.block_to_content.get(TemplateBlock.HEADER)
        code = self.block_to_content.get(TemplateBlock.CODE)
        footer = self.block_to_content.get(TemplateBlock.FOOTER)

        blocks = list(filter(None, [header, code, footer]))

        return merge_lines_to_code(blocks)


def _substitute_code_in_template(row: pd.Series) -> str:
    code = row[SubmissionColumns.CODE.value]
    template_content = row[SubmissionColumns.HIDDEN_CODE_TEMPLATE.value]

    if pd.isna(template_content):
        return code

    return Template(template_content).compile_template({TemplateBlock.CODE: code})


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
