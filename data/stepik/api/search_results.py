from dataclasses import dataclass
from typing import List


@dataclass
class SearchResultsRequestParams:
    query: str
    is_popular: bool = True
    page: int = 1
    type: str = "course"


@dataclass
class SearchResult:
    course: int
    course_title: str
    id: int
    position: int
    score: float
    target_id: int
    target_type: str
    course_owner: int
    course_slug: str
    course_cover: str


@dataclass
class SearchResultsResponse:
    search_results: List[SearchResult]
