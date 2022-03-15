import argparse
from pathlib import Path

from pandas import read_csv

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import write_df
from analysis.src.python.data_analysis.utils.parsing_utils import qet_qodana_issues
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, get_parent_folder
from analysis.src.python.evaluation.qodana.util.models import QodanaColumnName
from analysis.src.python.evaluation.qodana.util.util import (
    configure_model_converter_arguments, replace_inspections_on_its_ids,
)

INSPECTIONS = QodanaColumnName.INSPECTIONS.value


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_model_converter_arguments(parser)
    args = parser.parse_args()

    output_path = get_parent_folder(Path(args.solutions_file_path))

    df_solutions = read_csv(args.solutions_file_path)
    df_issues = read_csv(args.inspections_path)

    df_issues[IssuesColumns.ID.value] = list(range(0, df_issues.shape[0]))
    write_df(df_issues, output_path / f'qodana_issues_numbered{AnalysisExtension.CSV.value}')

    issues_ids = {issue[IssuesColumns.CLASS.value]: issue[IssuesColumns.ID.value] for _, issue in df_issues.iterrows()}

    df_solutions[SubmissionColumns.QODANA_ISSUES_IDS.value] = df_solutions.apply(
        lambda row: replace_inspections_on_its_ids(
            qet_qodana_issues(row[SubmissionColumns.QODANA_ISSUES.value]),
            issues_ids, args.remove_duplicates), axis=1)

    write_df(df_solutions, output_path / f'numbered_ids{AnalysisExtension.CSV.value}')


if __name__ == '__main__':
    main()
