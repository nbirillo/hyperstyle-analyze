import argparse

from analysis.src.python.evaluation.tools.qodana.imitation_model.roberta.util import SeedArgument
from analysis.src.python.utils.df_utils import read_df, write_df


def get_sample_dataset(submissions_path: str, submissions_sample_path: str, n_sample: int):
    """ Select random samples of `n_sample` size from dataset with submissions. """
    df_submissions = read_df(submissions_path)
    df_submissions_sample = df_submissions.sample(n=n_sample, random_state=SeedArgument.SEED.value)
    write_df(df_submissions_sample, submissions_sample_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path',
                        type=str,
                        help=f'Path to the dataset with submissions.')

    parser.add_argument('submissions_sample_path',
                        type=str,
                        help=f'Path to the dataset to same submissions sample dataset.')

    parser.add_argument('-n', '--n-sample',
                        type=int,
                        default=10000,
                        help='Number of submissions to select from initial dataset.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    get_sample_dataset(args.submissions_path, args.submissions_sample_path, args.n_sample)
