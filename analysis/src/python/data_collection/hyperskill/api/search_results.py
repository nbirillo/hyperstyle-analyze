from dataclasses import dataclass
from typing import List

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse


@dataclass
class SearchResultsRequestParams(BaseRequestParams):
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
class SearchResultsResponse(ObjectResponse[SearchResult]):
    search_results: List[SearchResult]

    def get_objects(self) -> List[SearchResult]:
        return self.search_results
