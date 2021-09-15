from dataclasses import dataclass
from typing import List

from analysis.src.python.data_mining.api.platform_entities import RequestParams, Object, Response, Meta


@dataclass
class SearchResultsRequestParams(RequestParams):
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
class SearchResultsResponse(Response[SearchResult]):
    search_results: List[SearchResult]
    meta: Meta

    def get_objects(self) -> List[SearchResult]:
        return self.search_results
