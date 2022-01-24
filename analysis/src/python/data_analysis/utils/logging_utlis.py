import logging
import os

from analysis.src.python.evaluation.common.file_util import clean_file, get_name_from_path, get_parent_folder


def configure_logger(processing_file_path: str, prefix: str):
    """ Create or clear logging to file to write information while processing csv files. """

    log_filename = f'{prefix}_{get_name_from_path(processing_file_path, with_extension=False)}.log'
    log_directory_path = get_parent_folder(processing_file_path)

    log_file_path = os.path.join(log_directory_path, log_filename)
    clean_file(log_file_path)

    logging.basicConfig(filename=os.path.join(log_directory_path, log_filename), level=logging.DEBUG)
