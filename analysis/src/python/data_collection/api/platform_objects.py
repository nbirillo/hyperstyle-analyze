from dataclasses import dataclass
from enum import Enum, unique
from typing import Generic, List, Optional, TypeVar


@unique
class Platform(str, Enum):
    HYPERSKILL = 'hyperskill'
    STEPIK = 'stepik'

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


@dataclass(frozen=True)
class Object:
    pass


@dataclass
class BaseRequestParams:
    page: int = 1
    page_size: int = 1000
    ids: Optional[List[int]] = None


@dataclass(frozen=True)
class Meta:
    page: int
    has_next: bool
    has_previous: bool


T = TypeVar('T', bound='Object')


@dataclass(frozen=True)
class ObjectResponse(Generic[T]):
    meta: Meta

    def get_objects(self) -> List[T]:
        raise NotImplementedError
