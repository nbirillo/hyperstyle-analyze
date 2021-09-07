from dataclasses import dataclass
from typing import List

from data.common_api.meta import Meta
from data.common_api.response import PageRequestParams, PageResponse, Object


@dataclass
class SearchResultsRequestParams(PageRequestParams):
    query: str = ""
    include_groups: bool = True
    include_projects: bool = True


@dataclass
class SearchResult(Object):
    target_id: int
    target_type: str
    position: int
    score: float


@dataclass
class SearchResultsResponse(PageResponse[SearchResult]):
    search_results: List[SearchResult]
    meta: Meta

    def get_objects(self) -> List[SearchResult]:
        return self.search_results
