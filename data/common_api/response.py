from dataclasses import dataclass
from typing import List, TypeVar, Generic

from data.common_api.meta import Meta


@dataclass
class RequestParams:
    pass


@dataclass
class PageRequestParams(RequestParams):
    page: int = 1
    page_size: int = 10


@dataclass
class Object:
    pass


T = TypeVar('T', bound='Object')


@dataclass
class PageResponse(Generic[T]):
    meta: Meta

    def get_objects(self) -> List[T]:
        pass
