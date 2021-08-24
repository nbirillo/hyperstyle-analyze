import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd
from hyperstyle.src.python.review.common.file_system import deserialize_data_from_file, Extension, get_parent_folder
from hyperstyle.src.python.review.quality.penalty import PenaltyIssue
from evaluation.common.csv_util import write_dataframe_to_csv
from evaluation.common.pandas_util import filter_df_by_single_value, get_solutions_df_by_file_path
from evaluation.common.tool_arguments import EvaluationRunToolArgument
from evaluation.common.util import ColumnName


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument(EvaluationRunToolArgument.DIFFS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.DIFFS_FILE_PATH.value.description)

    parser.add_argument('-n', '--n',
                        help='The N worse fragments will be saved',
                        type=int,
                        default=10)


def __get_new_inspections(fragment_id_to_issues: Dict[int, List[PenaltyIssue]], fragment_id: int) -> str:
    return ','.join(set(map(lambda i: i.origin_class, fragment_id_to_issues.get(fragment_id, []))))


def __get_public_fragments(solutions_df: pd.DataFrame, diffs_dict: dict) -> pd.DataFrame:
    # Keep only public solutions
    public_fragments = filter_df_by_single_value(solutions_df, ColumnName.IS_PUBLIC.value, 'YES')
    count_inspections_column = 'count_inspections'
    new_inspections_column = 'new_inspections'

    # Get only new inspections and count them
    fragment_id_to_issues = diffs_dict[ColumnName.TRACEBACK.value]
    public_fragments[new_inspections_column] = public_fragments.apply(
        lambda row: __get_new_inspections(fragment_id_to_issues, row[ColumnName.ID.value]), axis=1)
    public_fragments[count_inspections_column] = public_fragments.apply(
        lambda row: len(row[new_inspections_column].split(',')), axis=1)

    public_fragments = public_fragments.sort_values(count_inspections_column, ascending=False)
    # Keep only public columns
    return public_fragments[[ColumnName.CODE.value, ColumnName.TRACEBACK.value, new_inspections_column]]


# TODO: add readme
def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    solutions_file_path = args.solutions_file_path
    solutions_df = get_solutions_df_by_file_path(solutions_file_path)
    diffs = deserialize_data_from_file(args.diffs_file_path)

    public_fragments = __get_public_fragments(solutions_df, diffs)

    output_path = get_parent_folder(Path(solutions_file_path)) / f'worse_fragments{Extension.CSV.value}'
    write_dataframe_to_csv(output_path, public_fragments.head(args.n))


if __name__ == '__main__':
    main()
