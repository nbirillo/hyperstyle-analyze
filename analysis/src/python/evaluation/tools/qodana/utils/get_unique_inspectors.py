import argparse
import itertools
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import get_parent_folder
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.evaluation.tools.qodana.utils.models import QodanaColumnName, QodanaIssue

INSPECTION_ID = QodanaColumnName.INSPECTION_ID.value
INSPECTIONS = QodanaColumnName.INSPECTIONS.value
COUNT_ALL = QodanaColumnName.COUNT_ALL.value
COUNT_UNIQUE = QodanaColumnName.COUNT_UNIQUE.value
ID = QodanaColumnName.ID.value


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('--uniq',
                        help='If True, count fragments for eash inspection in which this inspection was.',
                        action='store_true')


def __get_inspections_ids(json_issues: str) -> List[str]:
    issues_list = QodanaIssue.parse_list_issues_from_json(json_issues)
    return list(map(lambda i: i.problem_id, issues_list))


def __get_inspections_from_df(solutions_df: pd.DataFrame) -> List[str]:
    inspections = solutions_df.apply(lambda row: __get_inspections_ids(row[INSPECTIONS]), axis=1)
    return list(itertools.chain.from_iterable(inspections.values))


def __count_uniq_inspections_in_fragment(json_issues: str, inspection_id_to_fragments: Dict[str, int]) -> None:
    issues_list = set(__get_inspections_ids(json_issues))
    for issue in issues_list:
        inspection_id_to_fragments[issue] += 1


def __get_uniq_inspections_in_all_fragments(solutions_df: pd.DataFrame) -> Dict[str, int]:
    inspection_id_to_fragments: Dict[str, int] = defaultdict(int)
    solutions_df.apply(lambda row: __count_uniq_inspections_in_fragment(row[INSPECTIONS], inspection_id_to_fragments),
                       axis=1)

    return inspection_id_to_fragments


def __get_all_inspections_by_inspection_id(inspection_id: str, all_inspections: List[str]) -> List[str]:
    return list(filter(lambda i: i == inspection_id, all_inspections))


def __create_unique_inspections_df(inspections: List[str],
                                   inspection_id_to_fragments: Optional[Dict[str, int]]) -> pd.DataFrame:
    id_to_inspection = {}
    for index, inspection in enumerate(set(inspections)):
        id_to_inspection[index + 1] = inspection
    inspections_df = pd.DataFrame(id_to_inspection.items(), columns=[ID, INSPECTION_ID])
    inspections_df[COUNT_ALL] = inspections_df.apply(lambda row: len(__get_all_inspections_by_inspection_id(
        row[INSPECTION_ID], inspections)), axis=1)
    if inspection_id_to_fragments is None:
        inspections_df[COUNT_UNIQUE] = 0
    else:
        inspections_df[COUNT_UNIQUE] = inspections_df.apply(lambda row: inspection_id_to_fragments.get(
            row[INSPECTION_ID], 0), axis=1)
    return inspections_df


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    solutions_file_path = args.solutions_file_path
    solutions_df = read_df(solutions_file_path)
    if args.uniq:
        inspection_id_to_fragments = __get_uniq_inspections_in_all_fragments(solutions_df)
    else:
        inspection_id_to_fragments = None
    inspections_df = __create_unique_inspections_df(__get_inspections_from_df(solutions_df), inspection_id_to_fragments)

    output_path = get_parent_folder(Path(solutions_file_path))
    write_df(inspections_df, output_path / f'inspections{AnalysisExtension.CSV.value}')


if __name__ == '__main__':
    main()
