import argparse
from typing import List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df


def extract_code_tfidfs(code: List[str], n_features: int) -> pd.DataFrame:
    """ For given list of code samples builds tf-idf matrix with `n_features` words. """

    vectorizer_tfidf = TfidfVectorizer(max_features=n_features)
    tfidfs = vectorizer_tfidf.fit_transform(code)
    tfidfs = pd.DataFrame(tfidfs.toarray(), columns=vectorizer_tfidf.get_feature_names())

    return tfidfs


def get_submissions_tfidfs(submissions_path: str, submissions_tf_idf_path: str, n_features: int):
    """ Builds tf-idf matrix for all submissions. """

    df_submissions = read_df(submissions_path)
    df_submissions_tf_idf = extract_code_tfidfs(df_submissions[SubmissionColumns.CODE.value], n_features)
    write_df(df_submissions_tf_idf, submissions_tf_idf_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('code_dataset_path', type=str, help='Path to .csv file with submissions tf-idf')
    parser.add_argument('--n-features', type=int, default=100, help='Number of features to take')

    args = parser.parse_args()
    get_submissions_tfidfs(args.submissions_path, args.submissions_tf_idf_path, args.n_features)
