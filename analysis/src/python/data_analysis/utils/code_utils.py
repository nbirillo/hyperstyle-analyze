from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns


def split_code_to_lines(submission: pd.DataFrame) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without /r). """

    return submission[SubmissionColumns.CODE.value].replace('\r', '').split('\n')


def merge_lines_to_code(code_lines: List[str]) -> str:
    """ Merge lines to code. """

    return '\n'.join(code_lines)
