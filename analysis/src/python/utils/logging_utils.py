import logging
import os
from typing import Optional

from analysis.src.python.utils.file_utils import clean_file, create_directory, create_file, get_name_from_path, \
    get_parent_folder


def configure_logger(processing_file_path: str, prefix: str, log_directory_path: Optional[str] = None):
    """ Create or clear logging to file to write information while processing csv files. """

    log_filename = f'{prefix}_{get_name_from_path(processing_file_path, with_extension=False)}.log'
    if log_directory_path is None:
        log_directory_path = get_parent_folder(processing_file_path)

    create_directory(log_directory_path)
    log_file_path = os.path.join(log_directory_path, log_filename)
    create_file(log_file_path, '')
    clean_file(log_file_path)

    logging.basicConfig(filename=os.path.join(log_directory_path, log_filename), level=logging.DEBUG)
