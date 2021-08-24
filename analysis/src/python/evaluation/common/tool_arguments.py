from enum import Enum, unique

from hyperstyle.src.python.common.tool_arguments import ArgumentsInfo
from hyperstyle.src.python.review.application_config import LanguageVersion
from analysis.src.python.evaluation.common.util import ColumnName


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

    QODANA_SOLUTIONS_FILE_PATH = ArgumentsInfo(None, 'solutions_file_path',
                                               'Csv file with solutions. This file must be graded by Qodana.')

    QODANA_INSPECTIONS_PATH = ArgumentsInfo(None, 'inspections_path', 'Path to a CSV file with inspections list.')

    QODANA_DUPLICATES = ArgumentsInfo(None, '--remove-duplicates', 'Remove duplicates around inspections')
