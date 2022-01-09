from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe topic entity from Hyperskill platform.
Topic is a theme of knowledge area of steps. Several steps can be related to one topic. Topics have hierarchy
(every topic have several prerequisite topics) and form the topics tree.
Topics are available by API requests, described at
    https://hyperskill.org/api/docs/#topics-list
    https://hyperskill.org/api/docs/#topics-read
"""


@dataclass
class TopicsRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
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

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{HyperskillPlatform.BASE_URL}/topics/{self.id}')


@dataclass(frozen=True)
class TopicsResponse(ObjectResponse[Topic]):
    topics: List[Topic]

    def get_objects(self) -> List[Topic]:
        return self.topics
