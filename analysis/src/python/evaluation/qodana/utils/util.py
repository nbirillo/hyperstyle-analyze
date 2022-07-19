import argparse
import json
from pathlib import Path
from typing import Dict, List

from analysis.src.python.evaluation.qodana.utils.models import QodanaColumnName, QodanaIssue, QodanaJsonField
from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument
from analysis.src.python.utils.df_utils import read_df


def to_json(issues: List[QodanaIssue]) -> str:
    issues_json = {
        QodanaJsonField.ISSUES.value: list(map(lambda i: i.to_json(), issues)),
    }
    return json.dumps(issues_json)


# Get a dictionary: Qodana inspection_id -> inspection_id from csv file with two columns: id, inspection_id
def get_inspections_dict(inspections_path: str) -> Dict[str, int]:
    inspections_df = read_df(inspections_path)
    inspections_dict = inspections_df.set_index(QodanaColumnName.INSPECTION_ID.value).T.to_dict('list')
    for qodana_id, id_list in inspections_dict.items():
        inspections_dict[qodana_id] = id_list[0]
    return inspections_dict


def replace_inspections_on_its_ids(issues_list: List[QodanaIssue], inspections_dict: Dict[str, int],
                                   to_remove_duplicates: bool) -> str:
    if len(issues_list) == 0:
        inspections = '0'
    else:
        problem_id_list = list(map(lambda i: inspections_dict[i.problem_id], issues_list))
        if to_remove_duplicates:
            problem_id_list = list(set(problem_id_list))
        problem_id_list.sort()
        inspections = ','.join(str(p) for p in problem_id_list)
    return inspections


def configure_model_converter_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument(EvaluationRunToolArgument.INSPECTIONS_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.INSPECTIONS_PATH.value.description)

    parser.add_argument(EvaluationRunToolArgument.DUPLICATES.value.long_name,
                        help=EvaluationRunToolArgument.DUPLICATES.value.description,
                        action='store_true')
