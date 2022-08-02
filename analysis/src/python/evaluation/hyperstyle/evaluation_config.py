import logging.config
from pathlib import Path
from typing import List, Optional, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.evaluation.utils.evaluation_utils import EvaluationConfig

logger = logging.getLogger(__name__)

HYPERSTYLE_TOOL_PATH = 'review/hyperstyle/src/python/review/run_tool.py'
HYPERSTYLE_DOCKER_PATH = 'stepik/hyperstyle:1.2.2'

OUTPUT_FILE_PATH = Path('result.json')


class HyperstyleEvaluationConfig(EvaluationConfig):
    def __init__(self, docker_path: Optional[str],
                 tool_path: str,
                 allow_duplicates: bool,
                 with_all_categories: bool,
                 new_format: bool,
                 tmp_path: Path,
                 n_cpu: Optional[int] = None):
        """
        `docker_path` - docker image name to run hyperstyle in (custom or default HYPERSTYLE_DOCKER_PATH)
        `tool_path` - path to hyperstyle tool running script (custom or HYPERSTYLE_TOOL_PATH)
        `tmp_path` - path where to place evaluation temporary files
        Number of hyperstyle tool running script parameters (`allow_duplicates`, `with_all_categories` etc.)
        """

        super().__init__(tmp_path=tmp_path / 'hyperstyle',
                         result_path=OUTPUT_FILE_PATH,
                         with_template=False)

        self.docker_path: str = docker_path
        self.tool_path: str = tool_path

        self.allow_duplicates: bool = allow_duplicates
        self.with_all_categories: bool = with_all_categories
        self.new_format = new_format
        self.n_cpu = n_cpu

    def build_command(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      language_version: LanguageVersion) -> List[str]:

        python_command = ['python3', f'{self.tool_path}']

        if self.allow_duplicates:
            python_command += ['--allow-duplicates']

        if self.with_all_categories:
            python_command += ['--with‑all‑categories']

        if self.new_format:
            python_command += ['--new-format']

        if self.n_cpu:
            python_command += ['--n-cpu', self.n_cpu]

        if language_version.is_java():
            python_command += ['--language_version', language_version.value]

        # If docker path specified, hyperstyle will run inside docker
        if self.docker_path is not None:
            python_command += ['/input', '>', f'/output/{OUTPUT_FILE_PATH}']
            command = ['docker', 'run',
                       '-v', f'{input_path}/:/input/',
                       '-v', f'{output_path}/:/output/',
                       f'{self.docker_path}',
                       '/bin/bash', '-c', ' '.join(python_command),
                       ]
        else:
            python_command += [str(input_path), '>', str(output_path / OUTPUT_FILE_PATH)]
            command = ['/bin/bash', '-c', ' '.join(python_command)]

        return command
