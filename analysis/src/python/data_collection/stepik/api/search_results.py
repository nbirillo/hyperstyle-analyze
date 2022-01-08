from dataclasses import dataclass
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse

"""
This file contains classes, which describe entities related to search result in Stepik platform. 
In platform there is search system there users can find objects related to their request.
Search can be done using API request, described at  
    https://stepic.org/api/docs/#!/search-results
"""


@dataclass
class SearchResultsRequestParams(BaseRequestParams):
    query: str = ""
    is_popular: bool = True
    type: str = "course"


@dataclass(frozen=True)
class SearchResult(Object):
    course: int
    course_title: str
    id: int
    position: int
    score: float
    target_id: int
    target_type: str
    course_owner: int
    course_slug: str
    course_cover: Optional[str]


@dataclass(frozen=True)
class SearchResultsResponse(ObjectResponse[SearchResult]):
    search_results: List[SearchResult]

    def get_objects(self) -> List[SearchResult]:
        return self.search_results
