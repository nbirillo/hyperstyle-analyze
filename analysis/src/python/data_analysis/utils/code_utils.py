import os
from typing import List

WINDOWS_LINE_ENDING = '\r\n'
LINUX_LINE_ENDING = '\n'


def split_code_to_lines(code: str) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without \r). """
    code = code.replace(WINDOWS_LINE_ENDING, os.linesep)
    code = code.replace(LINUX_LINE_ENDING, os.linesep)

    return code.split(os.linesep)


def merge_lines_to_code(code_lines: List[str]) -> str:
    """ Merge lines to code. """

    return os.linesep.join(code_lines)
