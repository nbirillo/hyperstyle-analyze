from dataclasses import dataclass
from typing import List

from data.hyperskill.api.meta import Meta


@dataclass
class SearchResultsRequestParams:
    query: str
    include_groups: bool = True
    include_projects: bool = True
    page: int = 1


@dataclass
class SearchResult:
    target_id: int
    target_type: str
    position: int
    score: float


@dataclass
class SearchResultsResponse:
    search_results: List[SearchResult]
    meta: Meta
