from dataclasses import dataclass
from enum import Enum
from typing import Generic, List, Optional, TypeVar


class Platform(str, Enum):
    HYPERSKILL = 'hyperskill'
    STEPIK = 'stepik'

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


@dataclass
class Object:
    pass


@dataclass
class BaseRequestParams:
    page: int = 1
    page_size: int = 100
    ids: Optional[List[int]] = None


@dataclass
class Meta:
    page: int
    has_next: bool
    has_previous: bool


T = TypeVar('T', bound='Object')


@dataclass
class ObjectResponse(Generic[T]):
    meta: Meta

    def get_objects(self) -> List[T]:
        pass
