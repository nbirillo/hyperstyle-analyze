import logging.config
import os
from pathlib import Path
from typing import List, Optional, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.utils.file_utils import create_directory, get_tmp_directory, remove_directory

logger = logging.getLogger(__name__)


class HyperstyleEvaluationConfig:
    def __init__(self, docker_path: Optional[str],
                 tool_path: str,
                 allow_duplicates: bool,
                 with_all_categories: bool,
                 new_format: bool,
                 tmp_directory: Optional[Path] = None):
        """
        `docker_path` - docker image name to run hyperstyle in (custom or default HYPERSTYLE_DOCKER_PATH)
        `tool_path` - path to hyperstyle tool running script (custom or HYPERSTYLE_TOOL_PATH)
        `tmp_directory` - directory where to place evaluation temporary files
        Number of hyperstyle tool running script parameters (`allow_duplicates`, `with_all_categories` etc.)
        """
        self.docker_path: str = docker_path
        self.tool_path: str = tool_path

        self.allow_duplicates: bool = allow_duplicates
        self.with_all_categories: bool = with_all_categories
        self.new_format = new_format

        if tmp_directory is None:
            self.tmp_directory: Path = get_tmp_directory() / 'hyperstyle' / str(os.getuid())
        else:
            self.tmp_directory = tmp_directory

        # Create new empty directory
        remove_directory(self.tmp_directory)
        create_directory(self.tmp_directory)

    def build_command(self,
                      input_path: Union[str, Path],
                      language_version: LanguageVersion) -> List[str]:

        command = []

        # If docker path is not specified, hyperstyle will run locally
        if self.docker_path is not None:
            command = ['docker', 'run',
                       '-v', f'{input_path}/:/input/',
                       f'{self.docker_path}',
                       ]

        command += ['python3', f'{self.tool_path}']

        if self.allow_duplicates:
            command += ['--allow-duplicates']

        if self.with_all_categories:
            command += ['--with‑all‑categories']

        if self.new_format:
            command += ['--new-format']

        if language_version.is_java():
            command += ['--language_version', language_version.value]

        if self.docker_path is not None:
            command += ['/input']
        else:
            command += [str(input_path)]

        return command
