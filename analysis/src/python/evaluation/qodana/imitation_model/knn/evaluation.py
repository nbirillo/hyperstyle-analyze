import argparse
import logging

import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.neighbors import KNeighborsClassifier

from analysis.src.python.data_analysis.model.column_name import IssuesColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger


def evaluate_submissions_classification(issues_path: str,
                                        train_code_path: str,
                                        train_target_path: str,
                                        test_code_path: str,
                                        test_target_path: str,
                                        classification_results_path: str,
                                        n_neighbors: int = 10):
    df_issues = read_df(issues_path)

    df_train_code = read_df(train_code_path)
    logging.info(f'Load train code dataset: {df_train_code.shape}')
    df_train_target = read_df(train_target_path)
    logging.info(f'Load train target datasets: {df_train_target.shape}')

    df_test_code = read_df(test_code_path)[:1000]
    logging.info(f'Load test code dataset: {df_test_code.shape}')
    df_test_target = read_df(test_target_path)[:1000]
    logging.info(f'Load test target datasets: {df_test_target.shape}')

    results = {
        'class': [],
        'id': [],
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f_score': [],
        'issues_per_test': [],
        'issues_per_traint': []
    }

    for _, issue in df_issues[:10].iterrows():
        issue_index = str(issue[IssuesColumns.ID.value])
        if issue_index not in df_train_target.columns:
            continue

        model = KNeighborsClassifier(n_neighbors=n_neighbors)

        logging.info(f'Start fitting model for issue {issue[IssuesColumns.CLASS.value]}')
        train_target = df_train_target[issue_index].values
        test_target = df_test_target[issue_index].values
        model.fit(df_train_code, train_target)
        logging.info(f'End fitting')

        pred_target = model.predict(df_test_code)

        precision, recall, f_score, _ = precision_recall_fscore_support(test_target, pred_target, average='binary')
        logging.info(f'precision={precision} recall={recall} f_score={f_score}')
        accuracy = accuracy_score(test_target, pred_target)
        logging.info(f'accuracy={accuracy}')

        results['accuracy'].append(accuracy)
        results['precision'].append(precision)
        results['recall'].append(recall)
        results['f_score'].append(f_score)
        results['class'].append(issue[IssuesColumns.CLASS.value])
        results['id'].append(issue[IssuesColumns.ID.value])
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
    parser.add_argument('--log-path', type=str, default=None, help='Path to log')

    args = parser.parse_args()

    configure_logger(args.classification_results_path, 'knn', args.log_path)

    evaluate_submissions_classification(args.issues_path,
                                        args.train_code_path,
                                        args.train_target_path,
                                        args.test_code_path,
                                        args.test_target_path,
                                        args.classification_results_path)
