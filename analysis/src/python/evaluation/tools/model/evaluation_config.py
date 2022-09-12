from pathlib import Path
from typing import List, Union

from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.utils.file_utils import create_directory


class EvaluationConfig:

    def __init__(self, tmp_path: Path, result_path: Path, with_template: bool):
        """
        @param tmp_path: temporary directory path where input/output can be saved
        @param result_path: relative path from output root where results are located
        @param with_template: template should or not be added while evaluation
        """
        self.tmp_path = tmp_path
        self.result_path = result_path
        self.with_template = with_template

        create_directory(self.tmp_path, clear=True)

    def build_command(self,
                      input_path: Union[Path, str],
                      output_path: Union[Path, str],
                      language_version: LanguageVersion) -> List[str]:
        pass
