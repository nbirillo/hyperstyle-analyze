import argparse
from pathlib import Path

import pandas as pd
from hyperstyle.src.python.review.quality.model import QualityType

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument
from analysis.src.python.evaluation.utils.pandas_utils import get_inconsistent_positions, get_issues_from_json_by_row
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.utils.file_utils import get_parent_folder
from analysis.src.python.utils.serialization_utils import serialize_data_and_write_to_file


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name}_old',
                        type=lambda value: Path(value).absolute(),
                        help=f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description}'
                             f'\nAll code fragments from this file must be graded '
                             f'(file contains grade and traceback (optional) columns)')

    parser.add_argument(f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name}_new',
                        type=lambda value: Path(value).absolute(),
                        help=f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description}'
                             f'\nAll code fragments from this file must be graded '
                             f'(file contains grade and traceback (optional) columns)')


# Find difference between two dataframes. Return dict:
# {
#  grade: [list_of_fragment_ids],
#  decreased_grade: [list_of_fragment_ids],
#  user: count_unique_users,
#  traceback: {
#       fragment_id: [list of issues]
#     },
#  penalty: {
#       fragment_id: [list of issues]
#     },
# }
# The key <grade> contains only fragments that increase quality in new df
# The key <decreased_grade> contains only fragments that decrease quality in new df
# The key <user> count number of unique users in the new dataset
# The key <traceback> contains list of new issues for each fragment
# The key <penalty> contains list of issues with not zero influence_on_penalty coefficient
def find_diffs(old_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    if ColumnName.HISTORY.value in new_df.columns:
        del new_df[ColumnName.HISTORY.value]
    new_df = new_df.reindex(columns=old_df.columns)
    inconsistent_positions = get_inconsistent_positions(old_df, new_df)
    diffs = {
        ColumnName.GRADE.value: [],
        ColumnName.DECREASED_GRADE.value: [],
        ColumnName.TRACEBACK.value: {},
        ColumnName.PENALTY.value: {},
    }
    if ColumnName.USER.value in new_df.columns:
        diffs[ColumnName.USER.value] = len(new_df[ColumnName.USER.value].unique())
    else:
        diffs[ColumnName.USER.value] = 0
    # Keep only diffs in the TRACEBACK column
    for row, _ in filter(lambda t: t[1] == ColumnName.TRACEBACK.value, inconsistent_positions.index):
        old_value = old_df.iloc[row][ColumnName.GRADE.value]
        new_value = new_df.iloc[row][ColumnName.GRADE.value]
        old_quality = QualityType(old_value).to_number()
        new_quality = QualityType(new_value).to_number()
        fragment_id = old_df.iloc[row][ColumnName.ID.value]
        if new_quality > old_quality:
            # It is an unexpected keys, we should check the algorithm
            diffs[ColumnName.GRADE.value].append(fragment_id)
        else:
            if new_quality < old_quality:
                diffs[ColumnName.DECREASED_GRADE.value].append(fragment_id)
            old_issues = get_issues_from_json_by_row(old_df, row)
            new_issues = get_issues_from_json_by_row(new_df, row)
            # Find difference between issues
            if len(old_issues) > len(new_issues):
                raise ValueError(f'New dataframe contains less issues than old for fragment {id}')
            difference = set(set(new_issues) - set(old_issues))
            if len(difference) > 0:
                diffs[ColumnName.TRACEBACK.value][fragment_id] = difference

            # Find issues with influence_in_penalty > 0
            penalty = set(filter(lambda i: i.influence_on_penalty > 0, new_issues))
            if len(penalty) > 0:
                diffs[ColumnName.PENALTY.value][fragment_id] = penalty
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    old_solutions_file_path = args.solutions_file_path_old
    old_solutions_df = read_df(old_solutions_file_path)

    new_solutions_file_path = args.solutions_file_path_new
    new_solutions_df = read_df(new_solutions_file_path)

    diffs = find_diffs(old_solutions_df, new_solutions_df)
    output_path = get_parent_folder(Path(old_solutions_file_path)) / f'diffs{AnalysisExtension.PICKLE.value}'
    serialize_data_and_write_to_file(output_path, diffs)


if __name__ == '__main__':
    main()
