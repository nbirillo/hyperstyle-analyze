import argparse
import sys

import pandas as pd

from analysis.src.python.data_collection.api.platform_objects import Platform
from analysis.src.python.data_collection.hyperskill.hyperskill_client import HyperskillClient
from analysis.src.python.data_collection.stepik.stepik_client import StepikClient
from analysis.src.python.data_collection.utils.csv_utils import save_objects_to_csv

platform_client = {
    Platform.HYPERSKILL: HyperskillClient,
    Platform.STEPIK: StepikClient,
}


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('--platform', '-p', type=str, help='platform to collect data from',
                        choices=Platform.values(), required=True)

    parser.add_argument('--object', '-o', type=str,
                        help='objects to request from platform (can be defaults like `step`, '
                             '`user` of custom like `java`)', required=True)
    parser.add_argument('--ids', '-i', nargs='*', type=int, default=None, help='ids of requested objects')
    parser.add_argument('--ids_from_file', '-f', type=str, default=None, help='csv file to get ids from')
    parser.add_argument('--ids_from_column', '-c', type=str, default=None, help='column in csv file to get ids from')
    parser.add_argument('--count', '-cnt', type=int, default=None, help='count of requested objects')
    parser.add_argument('--output', '-out', type=str, default='results',
                        help='path to directory where to save the results')
    return parser


if __name__ == '__main__':

    parser = configure_parser()
    args = parser.parse_args(sys.argv[1:])

    platform = Platform(args.platform)
    client = platform_client[platform]()
    if args.ids is not None:
        ids = args.ids
    else:
        ids = list(pd.read_csv(args.ids_from_file)[args.ids_from_column].unique().values)
    objects = client.get_objects(args.object, ids, args.count)
    save_objects_to_csv(args.output, objects, args.object)
