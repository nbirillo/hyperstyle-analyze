import argparse
import logging
from typing import List, Tuple

import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from analysis.src.python.data_analysis.model.column_name import IssuesColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger
from analysis.src.python.evaluation.qodana.imitation_model.classification.models import get_classification_model
from analysis.src.python.evaluation.qodana.imitation_model.preprocessing.down_sampling import down_sample


def apply_down_sampling(df_code: pd.DataFrame, df_target: pd.Series) -> Tuple[List[int], pd.DataFrame, pd.Series]:
    logging.info(f'Start down sampling with shape {df_target.shape}')
    balanced_sample = down_sample(df_target)
    df_target = df_target.iloc[balanced_sample].values
    df_code = df_code.iloc[balanced_sample]
    logging.info(f'Finish down sampling with shape {df_target.shape}')

    return balanced_sample, df_code, df_target


def evaluate_submissions_classification(issues_path: str,
                                        train_code_path: str,
                                        train_target_path: str,
                                        test_code_path: str,
                                        test_target_path: str,
                                        classification_results_path: str,
                                        model_config_path: str):
    df_issues = read_df(issues_path)

    df_train_code = read_df(train_code_path)
    logging.info(f'Load train code dataset: {df_train_code.shape}')
    df_train_target = read_df(train_target_path)
    logging.info(f'Load train target datasets: {df_train_target.shape}')

    df_test_code = read_df(test_code_path)
    logging.info(f'Load test code dataset: {df_test_code.shape}')
    df_test_target = read_df(test_target_path)
    logging.info(f'Load test target datasets: {df_test_target.shape}')

    results = {
        'class': [],
        'id': [],
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f_score': [],
        'issues_per_test': [],
        'issues_per_traint': [],
        'train_size': [],
        'test_size': []
    }

    for _, issue in df_issues[:50].iterrows():
        issue_index = str(issue[IssuesColumns.ID.value])

        if issue_index not in df_train_target.columns:
            continue

        model = get_classification_model(model_config_path)

        train_sample, train_code, train_target = apply_down_sampling(df_train_code, df_train_target[issue_index])
        test_sample, test_code, test_target = apply_down_sampling(df_test_code, df_test_target[issue_index])

        logging.info(f'Start fitting model for issue {issue[IssuesColumns.CLASS.value]}')
        model.fit(train_code, train_target)
        logging.info(f'End fitting')

        pred_target = model.predict(test_code)

        precision, recall, f_score, _ = precision_recall_fscore_support(test_target, pred_target, average='binary')
        logging.info(f'precision={precision} recall={recall} f_score={f_score}')
        accuracy = accuracy_score(test_target, pred_target)
        logging.info(f'accuracy={accuracy}')

        write_df(pd.DataFrame.from_dict({
            'id': df_test_target.iloc[test_sample]['id'].values,
            'test_target': test_target,
            'pred_target': pred_target,
        }), f'../data/issues/{issue[IssuesColumns.CLASS.value]}.csv')

        results['accuracy'].append(accuracy)
        results['precision'].append(precision)
        results['recall'].append(recall)
        results['f_score'].append(f_score)
        results['class'].append(issue[IssuesColumns.CLASS.value])
        results['id'].append(issue[IssuesColumns.ID.value])
        results['train_size'].append(train_code.shape[0])
        results['test_size'].append(test_code.shape[0])

        results['issues_per_traint'].append(train_target.mean())
        results['issues_per_test'].append(test_target.mean())

    write_df(pd.DataFrame.from_dict(results), classification_results_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues')
    parser.add_argument('train_code_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('train_target_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('test_code_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('test_target_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('classification_results_path', type=str, help='Path to .csv file with classification results')
    parser.add_argument('model_config_path', type=str, help='Path to .yaml file with model parameters')

    parser.add_argument('--log-path', type=str, default=None, help='Path to log')

    args = parser.parse_args()

    configure_logger(args.classification_results_path, 'classification', args.log_path)

    evaluate_submissions_classification(args.issues_path,
                                        args.train_code_path,
                                        args.train_target_path,
                                        args.test_code_path,
                                        args.test_target_path,
                                        args.classification_results_path,
                                        args.model_config_path)
