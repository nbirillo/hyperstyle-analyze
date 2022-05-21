import argparse
import os
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from analysis.src.python.data_analysis.utils.df_utils import read_df
from analysis.src.python.evaluation.common.csv_util import write_dataframe_to_csv
from analysis.src.python.evaluation.common.file_util import AnalysisExtension
from analysis.src.python.evaluation.qodana.imitation_model.roberta.util import SeedArgument


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('code_dataset_path',
                        type=str,
                        help=f'Path to the file with code representation data')

    parser.add_argument('target_dataset_path',
                        type=str,
                        help=f'Path to the file with targets')

    parser.add_argument('output_directory_path',
                        type=str,
                        default=None,
                        help='Path to the directory where folders for train, test and validation datasets will be '
                             'created. If not set directories will be created in the parent directory of dataset_path')

    parser.add_argument('-ts', '--test_size',
                        type=int,
                        default=0.2,
                        help='Rate of test size from the whole dataset. Default is 0.2')

    parser.add_argument('-vs', '--val_size',
                        type=int,
                        default=0.3,
                        help='Rate of validation dataset from the train dataset. Default is 0.3 ')

    parser.add_argument('-sh', '--shuffle',
                        type=bool,
                        default=True,
                        help='If true, data will be shuffled before splitting. Default is True.')

    return parser


def split_dataset(code_dataset_path: str,
                  target_dataset_path: str,
                  output_directory_path: str,
                  val_size: float, test_size: float, shuffle: bool):
    """ Split dataset to train/test/validate according to `val_size` `test_size`. """

    code_bank = read_df(code_dataset_path)
    target = read_df(target_dataset_path)

    assert target.shape[0] == code_bank.shape[0]

    code_train, code_test, target_train, target_test = train_test_split(code_bank,
                                                                        target,
                                                                        test_size=test_size,
                                                                        random_state=SeedArgument.SEED.value,
                                                                        shuffle=shuffle)

    code_train, code_val, target_train, target_val = train_test_split(code_train,
                                                                      target_train,
                                                                      test_size=val_size,
                                                                      random_state=SeedArgument.SEED.value,
                                                                      shuffle=shuffle)

    for part, code_data, target_data in [("train", code_train, target_train),
                                         ("val", code_val, target_val),
                                         ("test", code_test, target_test)]:
        output_path = Path(output_directory_path) / part
        os.makedirs(output_path, exist_ok=True)
        write_dataframe_to_csv(output_path / f'code{AnalysisExtension.CSV.value}', code_data)
        write_dataframe_to_csv(output_path / f'target{AnalysisExtension.CSV.value}', target_data)


if __name__ == "__main__":
    parser = configure_parser()
    args = parser.parse_args()

    split_dataset(args.code_dataset_path,
                  args.target_dataset_path,
                  args.output_directory_path, args.val_size, args.test_size, args.shuffle)
