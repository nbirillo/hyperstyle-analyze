from dataclasses import dataclass, field
from typing import Dict, List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe project entity from Hyperskill platform. Project contains of big task with
supportive steps to reach the final result and learn how to implement it.
Projects are available by API requests, described at
    https://hyperskill.org/api/docs/#projects-list
    https://hyperskill.org/api/docs/#projects-read
"""


@dataclass
class ProjectsRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Project(Object):
    id: int
    title: str
    use_ide: bool
    environment: str
    description: str
    is_beta: bool
    is_template_based: bool
    results: str
    stages_count: int
    n_first_prerequisites: int
    n_last_prerequisites: int
    language: str
    is_deprecated: bool
    progress_id: str
    readiness: int
    lesson_stepik_id: Optional[int]
    preview_step: Optional[int] = None
    ide_files: Optional[str] = None
    stages_ids: List[int] = field(default_factory=list)
    url: str = field(init=False)
    tracks: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{HyperskillPlatform.BASE_URL}/projects/{self.id}')


@dataclass(frozen=True)
class ProjectsResponse(ObjectResponse[Project]):
    projects: List[Project]

    def get_objects(self) -> List[Project]:
        return self.projects
