import logging.config
import os
from pathlib import Path
from typing import List, Optional, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.evaluation.utils.evaluation_utils import EvaluationConfig
from analysis.src.python.utils.file_utils import get_tmp_directory

logger = logging.getLogger(__name__)

PROFILE_FOLDER = Path(__file__).parents[3] / 'resources' / 'evaluation' / 'qodana' / 'inspection_profiles'

QODANA_JAVA_DOCKER_PATH = 'jetbrains/qodana'
QODANA_PYTHON_DOCKER_PATH = 'jetbrains/qodana-python:2022.1-eap'

OUTPUT_FILE_PATH = Path('report', 'results', 'result-allProblems.json')


class QodanaEvaluationConfig(EvaluationConfig):

    def __init__(self,
                 with_custom_profile: bool = False,
                 tmp_directory: Optional[Path] = None):
        """
        `with_custom_profile` - run qodana with custom inspection profile (settings)
        `tmp_directory` - directory where to place evaluation temporary files
        """

        tmp_directory = get_tmp_directory() if tmp_directory is None else tmp_directory
        super().__init__(tmp_path=tmp_directory / 'qodana',
                         result_path=OUTPUT_FILE_PATH,
                         with_template=True)

        self.with_custom_profile: bool = with_custom_profile

    def build_command(self,
                      input_path: Union[Path, str],
                      output_path: Union[Path, str],
                      language_version: LanguageVersion) -> List[str]:

        if language_version.is_java():
            docker_path = QODANA_JAVA_DOCKER_PATH
            profile_path = PROFILE_FOLDER / 'java_profile.xml'
        elif language_version == LanguageVersion.PYTHON_3:
            docker_path = QODANA_PYTHON_DOCKER_PATH
            profile_path = PROFILE_FOLDER / 'python_profile.xml'
        else:
            raise NotImplementedError(f'Language {language_version.value} is not supported now')

        command = [
            'docker', 'run',
            '-u', str(os.getuid()),
            '--rm',
            '-v', f'{input_path}/:/data/project/',
            '-v', f'{output_path}/:/data/results/',
        ]

        if self.with_custom_profile:
            command += ['-v', f'{profile_path}:/data/profile.xml']

        command.append(docker_path)
        command.append('--save-report')

        return command
