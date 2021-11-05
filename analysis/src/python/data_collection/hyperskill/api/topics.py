from dataclasses import dataclass
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_platform import HyperskillPlatform


@dataclass
class TopicsRequestParams(BaseRequestParams):
    pass


@dataclass
class Topic(Object):
    id: int
    children: List[int]
    depth: int
    followers: list[int]
    has_steps: bool
    hierarchy: List[int]
    prerequisites: List[int]
    progress_id: str
    depth: int
    root_id: int
    root_title: str
    title: str
    topological_index: int
    is_deprecated: bool
    theory: Optional[int]
    root_subgroup_title: Optional[str]
    parent_id: Optional[int]
    verification_step: Optional[int]

    def __post_init__(self):
        self.url = f'{HyperskillPlatform.BASE_URL}/topics/{self.id}'


@dataclass
class TopicsResponse(ObjectResponse[Topic]):
    topics: List[Topic]

    def get_objects(self) -> List[Topic]:
        return self.topics
