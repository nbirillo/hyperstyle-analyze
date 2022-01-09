import argparse
import logging
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from analysis.src.python.evaluation.batching.batch_config import BatchConfig
from analysis.src.python.evaluation.common.csv_util import append_dataframe_to_csv, write_dataframe_to_csv
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, create_directory, get_name_from_path
from analysis.src.python.evaluation.common.parallel_util import run_and_wait

logger = logging.getLogger(__name__)


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input_path", help="Path to the csv file with data to process",
                        type=lambda value: Path(value).absolute())
    parser.add_argument("output_path", help="Path to the output directory",
                        type=lambda value: Path(value).absolute())
    parser.add_argument("config_path", help="Path to the script config to run under batching",
                        type=lambda value: Path(value).absolute())
    parser.add_argument("--batch-size", help="Batch size for data", nargs='?', default=1000, type=int)
    parser.add_argument("--start-from", help="Index of batch to start processing from", nargs='?', default=0, type=int)


def run_batching():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    args = parser.parse_args()
    batch_paths = split_to_batches(args.input_path, args.output_path, args.batch_size)
    config = BatchConfig.from_yaml(args.config_path)

    for index, input_file_path, logs_path, output_path in batch_paths[args.start_from:]:
        logs_file_path = os.path.join(logs_path, f"log{AnalysisExtension.TXT.value}")

        with open(logs_file_path, 'w+') as logs_file:
            # create run script with python3
            command = ['python3', config.script_path, input_file_path]
            # add script args and flags
            command += config.script_args + config.script_flags
            # add script output flag
            command += [f'-o={output_path}']

            logging.info(f"Command to execute batch {index}: {command}")

            logging.info(f'Start batch {index} processing')
            start_time = time.time()
            run_and_wait(command, stdout=logs_file, stderr=logs_file, cwd=config.project_path)
            end_time = time.time()
            logging.info(f'Finish batch {index} processing in {end_time - start_time}')

    merge_batch_results(batch_paths, args.output)


def create_sub_directory(base_path: str, directory_name: str) -> str:
    directory_path = os.path.join(base_path, directory_name)
    create_directory(directory_path)
    return directory_path


def split_to_batches(dataset_path: str, output_dir_path: str, batch_size: int) -> List[Tuple[int, str, str, str]]:
    input_path = create_sub_directory(output_dir_path, 'input')
    logs_path = create_sub_directory(output_dir_path, 'logs')
    output_path = create_sub_directory(output_dir_path, 'output')

    df_name = get_name_from_path(dataset_path)

    batch_paths = []
    index = 0
    for batch in pd.read_csv(input, chunksize=batch_size):
        batch_name = f'batch_{index}'

        logging.info(f"Creating batch {index}")
        batch_input_path = create_sub_directory(input_path, batch_name)
        batch_logs_path = create_sub_directory(logs_path, batch_name)
        batch_output_path = create_sub_directory(output_path, batch_name)

        batch_input_file = os.path.join(batch_input_path, df_name)
        write_dataframe_to_csv(batch_input_file, batch)

        batch_paths.append((index, batch_input_file, batch_logs_path, batch_output_path))
        index += 1

    return batch_paths


def merge_batch_results(batch_paths: List[Tuple[int, str, str, str]], output: str):
    output_files_by_name = defaultdict(list)

    for _, _, _, output_path in batch_paths:
        output_files = os.listdir(output_path)
        for output_file in output_files:
            if AnalysisExtension.get_extension_from_file(output_file) == AnalysisExtension.CSV:
                output_file_id = re.sub(r'\.*batch_[0-9]+\.*', '', get_name_from_path(output_file))
                output_files_by_name[output_file_id].append(os.path.join(output_path, output_file))
    for output_file_name, output_files in output_files_by_name.items():
        for i, output_file in enumerate(output_files):
            output_df = pd.read_csv(output_file)
            if i == 0:
                write_dataframe_to_csv(os.path.join(output, output_file_name), output_df)
            else:
                append_dataframe_to_csv(os.path.join(output, output_file_name), output_df)


if __name__ == "__main__":
    run_batching()
