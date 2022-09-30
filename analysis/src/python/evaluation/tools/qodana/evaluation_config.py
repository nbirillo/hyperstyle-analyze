import logging.config
import os
from pathlib import Path
from typing import List, Optional, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.evaluation.tools.model.evaluation_config import EvaluationConfig
from analysis.src.python.evaluation.tools.utils.saving_utils import get_template_config
from analysis.src.python.utils.file_utils import create_directory

logger = logging.getLogger(__name__)

QODANA_PATH = 'jetbrains/qodana'

OUTPUT_FILE_PATH = Path('report', 'results', 'result-allProblems.json')


class QodanaEvaluationConfig(EvaluationConfig):

    def __init__(self,
                 tmp_path: Path,
                 cache_path: Optional[Path],
                 profile_path: Optional[Path],
                 profile_name: Optional[str]):
        """
        `tmp_path` - directory where to place evaluation temporary files
        `with_custom_profile` - run qodana with custom inspection profile (settings)
        """

        super().__init__(tmp_path=tmp_path / 'qodana',
                         result_path=OUTPUT_FILE_PATH,
                         with_template=True)

        if cache_path is not None:
            self.cache_path = cache_path
            create_directory(self.cache_path, clear=False)
        else:
            self.cache_path = None

        self.profile_path: Optional[Path] = profile_path
        self.profile_name: Optional[str] = profile_name

    def build_command(self,
                      input_path: Union[Path, str],
                      output_path: Union[Path, str],
                      language_version: LanguageVersion) -> List[str]:

        if language_version.is_java():
            docker_path = f'{QODANA_PATH}-jvm'
        elif language_version == LanguageVersion.PYTHON_3:
            docker_path = f'{QODANA_PATH}-python'
        else:
            raise NotImplementedError(f'Language {language_version.value} is not supported now')

        command = [
            'docker', 'run',
            '-u', str(os.getuid()),
            '--rm',
            '-v', f'{input_path}/:/data/project/',
            '-v', f'{output_path}/:/data/results/',
        ]

        if self.cache_path is not None:
            command += ['-v', f'{self.cache_path}/:/data/cache/']

        if self.profile_path is not None:
            command += ['-v', f'{self.profile_path}:/data/profile.xml']

        command.append(docker_path)

        template_config = get_template_config(language_version)
        command += ['--source-directory', str(template_config.template_root)]

        if self.profile_name is not None:
            command += ['--profile-name', self.profile_name]

        command.append('--save-report')

        return command
