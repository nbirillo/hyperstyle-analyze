import logging.config
import os
from argparse import Namespace
from pathlib import Path
from typing import List, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

logger = logging.getLogger(__name__)


class HyperstyleEvaluationConfig:
    def __init__(self, args: Namespace):

        self.docker_image: str = args.docker_image
        self.tool_path: str = args.tool_path

        self.new_format: bool = args.new_format
        self.allow_duplicates: bool = args.allow_duplicates
        self.with_all_categories: bool = args.with_all_categories

        self.tmp_directory: Path = args.tmp_directory

    def build_command(self,
                      input_path: Union[str, Path],
                      language_version: LanguageVersion) -> List[str]:

        command = ['docker', 'run',
                   '-u', str(os.getuid()),
                   '-v', f'{input_path}/:/input/',
                   f'{self.docker_image}',
                   f'{self.tool_path}', '/input',
                   ]

        if self.new_format:
            command.append(['--new-format'])

        if self.allow_duplicates:
            command.append(['--allow-duplicates'])

        if self.with_all_categories:
            command.append(['--with‑all‑categories'])

        if language_version.is_java():
            command.append(['‑‑language_version', LanguageVersion.value])

        return command
