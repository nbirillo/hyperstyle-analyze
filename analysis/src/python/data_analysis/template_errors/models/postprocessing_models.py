from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from data_collection.api.platform_objects import Object
from utils.numpy_utils import AggregateFunction


@dataclass(frozen=True)
class PostprocessingConfig(Object):
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
