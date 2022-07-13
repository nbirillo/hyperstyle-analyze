import logging.config
from argparse import Namespace
from pathlib import Path
from typing import List, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.utils.file_utils import get_tmp_directory

logger = logging.getLogger(__name__)


class HyperstyleEvaluationConfig:
    def __init__(self, args: Namespace):

        self.docker_path: str = args.docker_path
        self.tool_path: str = args.tool_path

        self.allow_duplicates: bool = args.allow_duplicates
        self.with_all_categories: bool = args.with_all_categories

        self.tmp_directory: Path = get_tmp_directory() / 'hyperstyle'

    def build_command(self,
                      input_path: Union[str, Path],
                      language_version: LanguageVersion) -> List[str]:

        command = ['docker', 'run',
                   '-v', f'{input_path}/:/input/',
                   f'{self.docker_path}',
                   'python', f'{self.tool_path}',
                   ]

        if self.allow_duplicates:
            command += ['--allow-duplicates']

        if self.with_all_categories:
            command += ['--with‑all‑categories']

        if language_version.is_java():
            command += ['--language_version', language_version.value]

        command += ['/input']

        return command
