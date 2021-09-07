from dataclasses import dataclass, field
from typing import List, Optional

from data.common_api.response import PageResponse, Object, PageRequestParams


@dataclass
class TracksRequestParams(PageRequestParams):
    pass


@dataclass
class ProjectsByLevel:
    easy: List[int] = field(default_factory=list)
    medium: List[int] = field(default_factory=list)
    hard: List[int] = field(default_factory=list)
    nightmare: List[int] = field(default_factory=list)


@dataclass
class Track(Object):
    id: int
    title: str
    description: str
    projects: List[int]
    projects_by_level: ProjectsByLevel
    best_rated_project: int
    fastest_to_complete_project: int
    progress_id: str
    seconds_to_complete: float
    topics_count: int
    results: str
    is_on_onboarding: bool
    is_beta: bool
    is_free: bool
    careers: str
    root_topic_id: Optional[int] = ""
    type: Optional[str] = ""
    url: str = field(init=False)

    def __post_init__(self):
        self.url = f'https://hyperskill.org/tracks/{self.id}'


@dataclass
class TracksResponse(PageResponse[Track]):
    tracks: List[Track]

    def get_objects(self) -> List[Track]:
        return self.tracks
