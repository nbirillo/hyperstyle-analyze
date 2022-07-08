import argparse
from pathlib import Path

from analysis.src.python.evaluation.qodana.utils.models import QodanaColumnName, QodanaIssue
from analysis.src.python.evaluation.qodana.utils.util import (
    configure_model_converter_arguments, get_inspections_dict, replace_inspections_on_its_ids,
)
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import get_parent_folder
from analysis.src.python.utils.extension_utils import AnalysisExtension

INSPECTIONS = QodanaColumnName.INSPECTIONS.value


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_model_converter_arguments(parser)
    args = parser.parse_args()

    solutions_file_path = args.solutions_file_path
    solutions_df = read_df(solutions_file_path)
    inspections_dict = get_inspections_dict(args.inspections_path)

    solutions_df[INSPECTIONS] = solutions_df.apply(
        lambda row: replace_inspections_on_its_ids(QodanaIssue.parse_list_issues_from_json(row[INSPECTIONS]),
                                                   inspections_dict, args.remove_duplicates), axis=1)

    output_path = get_parent_folder(Path(solutions_file_path))
    write_df(solutions_df, output_path / f'numbered_ids{AnalysisExtension.CSV.value}')


if __name__ == '__main__':
    main()
