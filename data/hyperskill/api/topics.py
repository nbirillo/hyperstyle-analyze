from dataclasses import dataclass
from typing import List, Optional

from data.common_api.response import PageRequestParams, PageResponse, Object


@dataclass
class TopicsRequestParams(PageRequestParams):
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
    theory: Optional[int] = None
    root_subgroup_title: Optional[str] = ""
    parent_id: Optional[int] = None
    verification_step: Optional[int] = None

    def __post_init__(self):
        self.url = f'https://hyperskill.org/topics/{self.id}'


@dataclass
class TopicsResponse(PageResponse[Topic]):
    topics: List[Topic]

    def get_objects(self) -> List[Topic]:
        return self.topics
