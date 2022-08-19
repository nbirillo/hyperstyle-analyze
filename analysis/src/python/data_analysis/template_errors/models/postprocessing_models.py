from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns
from analysis.src.python.utils.numpy_utils import AggregateFunction


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
