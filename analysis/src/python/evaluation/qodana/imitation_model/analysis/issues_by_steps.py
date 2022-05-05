import argparse
import os

import pandas as pd
from pandas import read_csv

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, write_df
from analysis.src.python.evaluation.common.file_util import AnalysisExtension
from analysis.src.python.evaluation.qodana.imitation_model.utils.evaluation_metrics import get_evaluation_metrics


def get_evaluation_metrics_by_steps(df_test_pred_step: pd.DataFrame) -> pd.Series:
    test_target = df_test_pred_step['test_target']
    pred_target = df_test_pred_step['pred_target']
    evaluation_metrics = get_evaluation_metrics(test_target, pred_target)
    step_info = df_test_pred_step.iloc[0]
    evaluation_metrics[SubmissionColumns.STEP_ID.value] = step_info[SubmissionColumns.STEP_ID.value]
    evaluation_metrics[SubmissionColumns.CODE.value] = step_info[SubmissionColumns.CODE.value]
    evaluation_metrics['count'] = test_target.shape[0]
    evaluation_metrics['ones'] = test_target.sum()
    evaluation_metrics['zeros'] = test_target.shape[0] - test_target.sum()
    return pd.Series(evaluation_metrics)


def get_scores_by_steps(solutions_path: str, issues_path: str, test_pred_dir: str, test_pred_metrics_dir: str):
    df_solutions = read_csv(solutions_path)
    df_issues = read_csv(issues_path)
    df_test_pred = merge_dfs(df_test_pred,
                             df_solutions[[SubmissionColumns.ID.value,
                                           SubmissionColumns.STEP_ID.value,
                                           SubmissionColumns.CODE.value]],
                             left_on='submissions',
                             right_on=SubmissionColumns.ID.value)

    for _, issue in df_issues.iterrows():
        file = f'{issue[IssuesColumns.CLASS.value]}{AnalysisExtension.CSV.value}'
        test_pred_path = os.path.join(test_pred_dir, file)
        if os.path.exists(test_pred_path):
            df_test_pred = read_csv(test_pred_path)
            df_test_pred = merge_dfs(df_test_pred,
                                     df_solutions[[SubmissionColumns.ID.value,
                                                   SubmissionColumns.STEP_ID.value,
                                                   SubmissionColumns.CODE.value]],
                                     left_on='submissions',
                                     right_on=SubmissionColumns.ID.value)
            evaluation_metrics_by_steps = df_test_pred. \
                groupby(SubmissionColumns.STEP_ID.value). \
                apply(get_evaluation_metrics_by_steps)

            test_pred_metrics_path = os.path.join(test_pred_metrics_dir, file)
            write_df(evaluation_metrics_by_steps, test_pred_metrics_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('solutions_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues')
    parser.add_argument('test_pred_dir', type=str, help='Path to directory with test/pred values')
    parser.add_argument('test_pred_metrics_dir', type=str, help='Path to directory with test/pred values')

    args = parser.parse_args()
    get_scores_by_steps(args.solutions_path,
                        args.issues_path,
                        args.test_pred_dir,
                        args.test_pred_metrics_dir)
