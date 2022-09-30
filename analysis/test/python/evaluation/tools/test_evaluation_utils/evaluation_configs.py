from pathlib import Path
from typing import Optional

from analysis.src.python.evaluation.tools.hyperstyle.evaluation_config import HYPERSTYLE_DOCKER_PATH, \
    HYPERSTYLE_TOOL_PATH, HyperstyleEvaluationConfig
from analysis.src.python.evaluation.tools.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.test.python.evaluation.tools import TMP_DIR_PATH


def get_default_hyperstyle_config(docker_path: Optional[str] = HYPERSTYLE_DOCKER_PATH,
                                  tool_path: str = HYPERSTYLE_TOOL_PATH,
                                  allow_duplicates: bool = False,
                                  with_all_categories: bool = False,
                                  new_format: bool = False,
                                  tmp_path: Path = TMP_DIR_PATH) -> HyperstyleEvaluationConfig:
    return HyperstyleEvaluationConfig(docker_path=docker_path,
                                      tool_path=tool_path,
                                      allow_duplicates=allow_duplicates,
                                      with_all_categories=with_all_categories,
                                      new_format=new_format,
                                      tmp_path=tmp_path)


def get_default_qodana_config(tmp_path: Path = TMP_DIR_PATH) -> QodanaEvaluationConfig:
    return QodanaEvaluationConfig(tmp_path=tmp_path,
                                  profile_path=None,
                                  cache_path=None,
                                  profile_name='qodana.recommended')
