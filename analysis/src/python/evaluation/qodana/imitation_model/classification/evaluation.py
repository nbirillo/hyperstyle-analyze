import argparse
import logging
import os

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, create_directory
from analysis.src.python.evaluation.qodana.imitation_model.classification.model import get_model, \
    get_model_config
from analysis.src.python.evaluation.qodana.imitation_model.preprocessing.sampling import down_sample
from analysis.src.python.evaluation.qodana.imitation_model.utils.evaluation_metrics import get_evaluation_metrics
from analysis.src.python.evaluation.qodana.imitation_model.utils.metrics import EvaluationMetricsColumns


def evaluate_submissions_classification(issues_path: str,
                                        train_code_path: str,
                                        train_target_path: str,
                                        test_code_path: str,
                                        test_target_path: str,
                                        output_path: str,
                                        model_config_path: str,
                                        down_sampling: bool,
                                        issues_count: int):
    df_issues = read_df(issues_path)

    df_train_code = read_df(train_code_path)
    logging.info(f'Load train code dataset: {df_train_code.shape}')

    df_train_target = read_df(train_target_path)
    logging.info(f'Load train target datasets: {df_train_target.shape}')

    df_test_code = read_df(test_code_path)
    logging.info(f'Load test code dataset: {df_test_code.shape}')

    df_test_target = read_df(test_target_path)
    logging.info(f'Load test target datasets: {df_test_target.shape}')

    model_config = get_model_config(model_config_path)

    create_directory(output_path)
    issues_path = os.path.join(output_path, 'issues')
    create_directory(issues_path)
    results_path = os.path.join(output_path, f'results_{model_config.get_line_name()}{AnalysisExtension.CSV.value}')

    results = []

    for _, issue in df_issues[:issues_count].iterrows():
        issue_id = str(issue[IssuesColumns.ID.value])

        if issue_id not in df_train_target.columns:
            continue

        model = get_model(model_config)

        train_subsample = down_sample(df_train_target[issue_id]) if down_sampling else df_train_target.index.values
        df_train_code_subsample, df_train_target_subsample = \
            df_train_code.iloc[train_subsample], df_train_target.iloc[train_subsample]

        test_subsample = down_sample(df_test_target[issue_id]) if down_sampling else df_test_target.index.values
        df_test_code_subsample, df_test_target_subsample = \
            df_test_code.iloc[test_subsample], df_test_target.iloc[test_subsample]

        logging.info(f'Start fitting model for issue {issue[IssuesColumns.CLASS.value]}')
        train_target = df_train_target_subsample[issue_id].values
        model.fit(df_train_code_subsample, train_target)
        logging.info(f'End fitting')

        pred_target = model.predict(df_test_code_subsample)
        test_target = df_test_target_subsample[issue_id].values
        result = get_evaluation_metrics(test_target, pred_target)

        logging.info(f'precision={result[EvaluationMetricsColumns.PRECISION.value]} '
                     f'recall={result[EvaluationMetricsColumns.RECALL.value]} '
                     f'f_score={result[EvaluationMetricsColumns.F_SCORE.value]} '
                     f'f1_score={result[EvaluationMetricsColumns.F1_SCORE.value]} '
                     f'accuracy={result[EvaluationMetricsColumns.ACCURACY.value]}')

        result[IssuesColumns.CLASS.value] = issue[IssuesColumns.CLASS.value]
        result[IssuesColumns.ID.value] = issue[IssuesColumns.ID.value]
        result[EvaluationMetricsColumns.TRAIN_SIZE.value] = train_target.shape[0]
        result[EvaluationMetricsColumns.TEST_SIZE.value] = test_target.shape[0]
        result[EvaluationMetricsColumns.ISSUES_IN_TEST.value] = train_target.sum()
        result[EvaluationMetricsColumns.ISSUES_IN_TRAIN.value] = test_target.sum()

        write_df(pd.DataFrame.from_dict({
            SubmissionColumns.ID.value: df_test_target_subsample[SubmissionColumns.ID.value].values,
            EvaluationMetricsColumns.TEST_TARGET.value: test_target,
            EvaluationMetricsColumns.TRAIN_TARGET.value: pred_target,
        }), os.path.join(issues_path, f'{issue[IssuesColumns.CLASS.value]}{AnalysisExtension.CSV.value}'))

        results.append(pd.Series(result))

    write_df(pd.DataFrame.from_records(results), results_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues')
    parser.add_argument('train_code_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('train_target_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('test_code_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('test_target_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('classification_results_path', type=str, help='Path to .csv file with classification results')
    parser.add_argument('model_config_path', type=str, help='Path to .yaml file with model parameters')

    parser.add_argument('--down-sampling', type=bool, default=True, help='Apply down sampling for dataset')
    parser.add_argument('--issues-count', type=int, default=50, help='Number of issues to process')
    parser.add_argument('--log-path', type=str, default=None, help='Path to log')

    args = parser.parse_args()

    configure_logger(args.classification_results_path, 'classification', args.log_path)

    evaluate_submissions_classification(args.issues_path,
                                        args.train_code_path,
                                        args.train_target_path,
                                        args.test_code_path,
                                        args.test_target_path,
                                        args.classification_results_path,
                                        args.model_config_path,
                                        args.down_sampling,
                                        args.issues_count)
