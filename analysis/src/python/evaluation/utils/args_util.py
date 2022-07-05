import re
from enum import Enum, unique
from pathlib import Path
from typing import List, Set, Tuple, Union

from hyperstyle.src.python.common.tool_arguments import ArgumentsInfo
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.file_system import Extension, get_all_file_system_items

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.utils.file_utils import file_match_condition
from analysis.src.python.utils.extension_utlis import AnalysisExtension


@unique
class EvaluationArgument(Enum):
    TRACEBACK = 'traceback'
    RESULT_FILE_NAME = 'evaluation_results'
    RESULT_FILE_NAME_XLSX = f'{RESULT_FILE_NAME}{AnalysisExtension.XLSX.value}'
    RESULT_FILE_NAME_CSV = f'{RESULT_FILE_NAME}{AnalysisExtension.CSV.value}'


@unique
class EvaluationRunToolArgument(Enum):
    SOLUTIONS_FILE_PATH = ArgumentsInfo(None, 'solutions_file_path',
                                        'Local XLSX-file or CSV-file path. '
                                        'Your file must include column-names: '
                                        f'"{ColumnName.CODE.value}" and '
                                        f'"{ColumnName.LANG.value}". Acceptable values for '
                                        f'"{ColumnName.LANG.value}" column are: '
                                        f'{LanguageVersion.PYTHON_3.value}, {LanguageVersion.JAVA_8.value}, '
                                        f'{LanguageVersion.JAVA_11.value}, {LanguageVersion.KOTLIN.value}.')

    DIFFS_FILE_PATH = ArgumentsInfo(None, 'diffs_file_path',
                                    'Path to a file with serialized diffs that were founded by diffs_between_df.py')

    INSPECTIONS_PATH = ArgumentsInfo(None, 'inspections_path', 'Path to a CSV file with inspections list.')

    DUPLICATES = ArgumentsInfo(None, '--remove-duplicates', 'Remove duplicates around inspections')


script_structure_rule = ('Please, make sure your XLSX-file matches following script standards: \n'
                         '1. Your XLSX-file or CSV-file should have 2 obligatory columns named:'
                         f'"{ColumnName.CODE.value}" & "{ColumnName.LANG.value}". \n'
                         f'"{ColumnName.CODE.value}" column -- relates to the code-sample. \n'
                         f'"{ColumnName.LANG.value}" column -- relates to the language of a '
                         'particular code-sample. \n'
                         '2. Your code samples should belong to the one of the supported languages. \n'
                         'Supported languages are: Java, Kotlin, Python. \n'
                         f'3. Check that "{ColumnName.LANG.value}" column cells are filled with '
                         'acceptable language-names: \n'
                         f'Acceptable language-names are: {LanguageVersion.PYTHON_3.value}, '
                         f'{LanguageVersion.JAVA_8.value} ,'
                         f'{LanguageVersion.JAVA_11.value} and {LanguageVersion.KOTLIN.value}.')


# Split string by separator
def parse_set_arg(str_arg: str, separator: str = ',') -> Set[str]:
    return set(str_arg.split(separator))


def get_in_and_out_list(root: Path,
                        in_ext: Union[Extension, AnalysisExtension] = AnalysisExtension.CSV,
                        out_ext: Union[Extension, AnalysisExtension]
                        = AnalysisExtension.CSV) -> List[Tuple[Path, Path]]:
    in_files = get_all_file_system_items(root, file_match_condition(rf'in_\d+{in_ext.value}'))
    out_files = get_all_file_system_items(root, file_match_condition(rf'out_\d+{out_ext.value}'))
    return pair_in_and_out_files(in_files, out_files)


def pair_in_and_out_files(in_files: List[Path], out_files: List[Path]) -> List[Tuple[Path, Path]]:
    pairs = []
    for in_file in in_files:
        out_file = Path(re.sub(r'in(?=[^in]*$)', 'out', str(in_file)))
        if out_file not in out_files:
            raise ValueError(f'List of out files does not contain a file for {in_file}')
        pairs.append((in_file, out_file))
    return pairs
