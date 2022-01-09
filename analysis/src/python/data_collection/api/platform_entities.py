from dataclasses import dataclass
from typing import List, TypeVar, Generic


@dataclass
class Object:
    pass


@dataclass
class RequestParams:
    page: int = 1
    page_size: int = 10


@dataclass
class Meta:
    page: int
    has_next: bool
    has_previous: bool


T = TypeVar('T', bound='Object')


@dataclass
class Response(Generic[T]):
    meta: Meta

    def get_objects(self) -> List[T]:
        pass
