import argparse
import sys

from analysis.src.python.data_collection.hyperskill.hyperskill_client import HyperskillClient, ObjectClass
import pandas as pd


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def extend_hyperskill_dataset(csv_file_path: str, obj_class: str):
    api = HyperskillClient()
    df = pd.read_csv(csv_file_path)

    if obj_class == ObjectClass.STEP:
        ids = list(set(df['step_id'].values))
        for ids_chunk in chunks(ids, 20):
            api.get_steps(ids=ids_chunk, save_to_csv=True)

    if obj_class == ObjectClass.TRACK:
        ids = list(set(df['id'].values))
        for ids_chunk in chunks(ids, 20):
            api.get_tracks(ids=ids_chunk, save_to_csv=True)

    if obj_class == ObjectClass.TOPIC:
        ids = list(set(df['id'].values))
        for ids_chunk in chunks(ids, 20):
            api.get_topics(ids=ids_chunk, save_to_csv=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--csv_file_path', type=str, help='path to csv file with data', required=True)

    parser.add_argument('--platform', type=str, help='educational platform', required=True,
                        choices=['stepik', 'hyperskill'])

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['course', 'project', 'topic', 'step', 'track'])

    args = parser.parse_args(sys.argv[1:])

    if args.platform == 'hyperskill':
        extend_hyperskill_dataset(args.csv_file_path, args.object)
