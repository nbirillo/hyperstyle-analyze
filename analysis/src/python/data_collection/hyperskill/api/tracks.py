from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe track entity from Hyperskill platform.
Track is a series of steps to get knowledge on some specific theme (programming language, data analysis, ect.).
Tracks are available by API requests, described at
    https://hyperskill.org/api/docs/#tracks-list
    https://hyperskill.org/api/docs/#tracks-read
"""


@dataclass
class TracksRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class ProjectsByLevel:
    easy: List[int] = field(default_factory=list)
    medium: List[int] = field(default_factory=list)
    hard: List[int] = field(default_factory=list)
    nightmare: List[int] = field(default_factory=list)


@dataclass(frozen=True)
class Track(Object):
    id: int
    title: str
    description: str
    projects: List[int]
    projects_by_level: ProjectsByLevel
    best_rated_project: Optional[int]
    fastest_to_complete_project: Optional[int]
    progress_id: Optional[str]
    seconds_to_complete: float
    topics_count: int
    results: str
    is_on_onboarding: Optional[bool]
    is_beta: bool
    is_free: bool
    careers: str
    root_topic_id: Optional[int]
    type: Optional[str]

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{HyperskillPlatform.BASE_URL}/tracks/{self.id}')


@dataclass(frozen=True)
class TracksResponse(ObjectResponse[Track]):
    tracks: List[Track]

    def get_objects(self) -> List[Track]:
        return self.tracks
