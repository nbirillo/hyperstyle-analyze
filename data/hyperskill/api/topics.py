from dataclasses import dataclass
from typing import List, Optional

from data.hyperskill.api.meta import Meta


@dataclass
class TopicsRequestParams:
    page: int = 1
    page_size: int = 10


@dataclass
class Topic:
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
class TopicsResponse:
    topics: List[Topic]
    meta: Meta
