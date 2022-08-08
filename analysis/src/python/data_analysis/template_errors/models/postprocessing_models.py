from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns
from analysis.src.python.utils.numpy_utils import AggregateFunction


@unique
class TemplateGatheringType(Enum):
    API = 'api'
    DATABASE = 'database'

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in TemplateGatheringType]

    @classmethod
    def define_template_gathering_type(cls, df: pd.DataFrame) -> 'TemplateGatheringType':
        columns = df.columns
        if StepColumns.CODE_TEMPLATE.value in columns:
            return TemplateGatheringType.API
        if StepColumns.CODE_TEMPLATES.value in columns:
            return TemplateGatheringType.DATABASE
        raise ValueError('Can not define template gathering type: API or DATABASE')

    def get_template_column(self):
        if self == TemplateGatheringType.API:
            return StepColumns.CODE_TEMPLATE
        if self == TemplateGatheringType.DATABASE:
            return StepColumns.CODE_TEMPLATES
        raise ValueError(f'Undefined template gathering type: {self}')


@dataclass(frozen=True)
class PostprocessingConfig:
    templates_search_result_path: Path
    result_path: Path
    raw_issues_path: Optional[Path]
    filter_duplicates_type: AggregateFunction
    freq_to_remove: float
    freq_to_keep: float
    freq_to_separate_typical_and_template: float
    number_of_solutions: int
    to_add_description: bool
    base_task_url: str
