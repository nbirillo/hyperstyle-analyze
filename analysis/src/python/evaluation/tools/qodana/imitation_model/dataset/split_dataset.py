import argparse
import os

from sklearn.model_selection import train_test_split

from analysis.src.python.evaluation.tools.qodana.imitation_model.roberta.util import SeedArgument
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_name_from_path


def split_dataset(code_dataset_path: str, target_dataset_path: str, output_directory_path: str, val_size: float,
                  test_size: float, shuffle: bool):
    """
    Split code and target datasets to train/test/val parts in proportion (1 - test_size - val_size)/test_size/val_size.
    """
    code_df = read_df(code_dataset_path)
    target_df = read_df(target_dataset_path)

    assert target_df.shape[0] == code_df.shape[0], "Code and target datasets must be of same size."

    code_train, code_test, target_train, target_test = train_test_split(code_df, target_df,
                                                                        test_size=test_size,
                                                                        random_state=SeedArgument.SEED.value,
                                                                        shuffle=shuffle)

    code_train, code_val, target_train, target_val = train_test_split(code_train, target_train,
                                                                      test_size=val_size,
                                                                      random_state=SeedArgument.SEED.value,
                                                                      shuffle=shuffle)

    output_directory_path = create_directory(output_directory_path)
    code_dataset_file_name = get_name_from_path(code_dataset_path, with_extension=True)
    target_dataset_file_name = get_name_from_path(target_dataset_path, with_extension=True)

    for holdout in [("train", code_train, target_train),
                    ("val", code_val, target_val),
                    ("test", code_test, target_test)]:
        result_path = output_directory_path / holdout[0]
        os.makedirs(result_path)
        write_df(holdout[1], result_path / code_dataset_file_name)
        write_df(holdout[2], result_path / target_dataset_file_name)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('code_dataset_path',
                        type=str,
                        help=f'Path to the dataset with code features to apply train/test/val split')

    parser.add_argument('target_dataset_path',
                        type=str,
                        help=f'Path to the dataset with target values to apply train/test/val split')

    parser.add_argument('result_path',
                        type=str,
                        help='Path to the directory where folders for train, test and validation datasets will be '
                             'created.')

    parser.add_argument('-ts', '--test_size',
                        type=int,
                        default=0.3,
                        help='Rate of test size from the whole dataset. Default is 0.3')

    parser.add_argument('-vs', '--val_size',
                        type=int,
                        default=0.2,
                        help='Rate of validation dataset from the train dataset. Default is 0.2')

    parser.add_argument('-sh', '--shuffle',
                        type=bool,
                        default=True,
                        help='If true, data will be shuffled before splitting. Default is True.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    split_dataset(args.code_dataset_path, args.target_dataset_path,
                  args.result_path, args.val_size, args.test_size, args.shuffle)
