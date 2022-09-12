import argparse
import logging
import sys
from typing import List

from analysis.src.python.data_collection.api.platform_objects import Platform
from analysis.src.python.data_collection.hyperskill.hyperskill_client import HyperskillClient
from analysis.src.python.data_collection.stepik.stepik_client import StepikClient
from analysis.src.python.data_collection.utils.csv_utils import save_objects_to_csv
from analysis.src.python.utils.df_utils import read_df

platform_client = {
    Platform.HYPERSKILL: HyperskillClient,
    Platform.STEPIK: StepikClient,
}


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('platform', type=str, help='platform to collect data from', choices=Platform.values())

    parser.add_argument('object', type=str,
                        help='objects to request from platform (can be defaults like `step` or custom like `java`')
    parser.add_argument('--ids', '-i', nargs='*', type=int, default=None, help='ids of requested objects')
    parser.add_argument('--ids_from_file', '-f', type=str, default=None, help='csv file to get ids from')
    parser.add_argument('--ids_from_column', '-c', type=str, default=None, help='column in csv file to get ids from')
    parser.add_argument('--count', '-cnt', type=int, default=None, help='count of requested objects')
    parser.add_argument('--output', '-out', type=str, default='results',
                        help='path to directory where to save the results')
    parser.add_argument('--port', '-p', type=int, default=8000, help='port to run authorization server at')
    return parser


def get_object_ids_from_file(csv_file_path: str, column_name: str) -> List[int]:
    """
    Get ids from scv file column. Method is useful when extra information is required for some subset of objects,
    which are already used in existing dataset (e.x. dataset of solutions).
    """
    return list(read_df(csv_file_path)[column_name].unique().values)


logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':

    parser = configure_parser()
    args = parser.parse_args(sys.argv[1:])

    platform = Platform(args.platform)
    client = platform_client[platform]()

    if args.ids is not None:
        ids = args.ids
    elif args.ids_from_file is not None and args.ids_from_column is not None:
        ids = get_object_ids_from_file(args.ids_from_file, args.ids_from_column)
    else:
        ids = None

    objects = client.get_objects(args.object, ids, args.count)
    save_objects_to_csv(args.output, objects, args.object)
