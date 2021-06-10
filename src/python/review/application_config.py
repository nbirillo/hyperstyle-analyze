from dataclasses import dataclass
from enum import Enum, unique
from typing import Dict, List, Optional, Set

from src.python.review.common.file_system import Extension
from src.python.review.inspectors.inspector_type import InspectorType


@dataclass
class ApplicationConfig:
    disabled_inspectors: Set[InspectorType]
    allow_duplicates: bool
    n_cpu: int
    inspectors_config: dict
    start_line: int = 1
    end_line: Optional[int] = None
    new_format: bool = False
    history: Optional[str] = None


@unique
class LanguageVersion(Enum):
    JAVA_7 = 'java7'
    JAVA_8 = 'java8'
    JAVA_9 = 'java9'
    JAVA_11 = 'java11'
    PYTHON_3 = 'python3'
    KOTLIN = 'kotlin'

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls.__members__.values()]

    @classmethod
    def language_to_extension_dict(cls) -> Dict['LanguageVersion', Extension]:
        return {cls.PYTHON_3: Extension.PY,
                cls.JAVA_7: Extension.JAVA,
                cls.JAVA_8: Extension.JAVA,
                cls.JAVA_9: Extension.JAVA,
                cls.JAVA_11: Extension.JAVA,
                cls.KOTLIN: Extension.KT}

    def extension_by_language(self) -> Extension:
        return self.language_to_extension_dict()[self]

    def is_java(self) -> bool:
        return (
            self == LanguageVersion.JAVA_7
            or self == LanguageVersion.JAVA_8
            or self == LanguageVersion.JAVA_9
            or self == LanguageVersion.JAVA_11
        )