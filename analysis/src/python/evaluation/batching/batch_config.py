from dataclasses import dataclass
from enum import Enum, unique
from typing import List

from analysis.src.python.utils.yaml_util import parse_yaml


@unique
class BatchConfigFields(Enum):
    PROJECT_PATH = 'project_path'
    SCRIPT_PATH = 'script_path'
    SCRIPT_ARGS = 'script_args'
    SCRIPT_FLAGS = 'script_flags'


@dataclass(frozen=True)
class BatchConfig:
    project_path: str
    script_path: str
    script_args: List[str]
    script_flags: List[str]

    @classmethod
    def from_yaml(cls, yaml_path) -> 'BatchConfig':
        config = parse_yaml(yaml_path)
        script_args = []
        script_flags = []
        if BatchConfigFields.SCRIPT_ARGS.value in config and config[BatchConfigFields.SCRIPT_ARGS.value] is not None:
            for script_arg in config[BatchConfigFields.SCRIPT_ARGS.value]:
                script_args.append(script_arg)
        if BatchConfigFields.SCRIPT_FLAGS.value in config and config[BatchConfigFields.SCRIPT_FLAGS.value] is not None:
            for flag_key, flag_value in config[BatchConfigFields.SCRIPT_FLAGS.value].items():
                script_flags.append(f"-{flag_key}={flag_value}")

        return BatchConfig(project_path=config[BatchConfigFields.PROJECT_PATH.value],
                           script_path=config[BatchConfigFields.SCRIPT_PATH.value],
                           script_args=script_args,
                           script_flags=script_flags)
