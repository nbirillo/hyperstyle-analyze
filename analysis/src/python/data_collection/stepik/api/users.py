import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform


@dataclass
class UserRequestParams(BaseRequestParams):
    pass


@dataclass
class User(Object):
    id: int
    profile: str
    is_private: bool
    is_active: bool
    is_guest: bool
    is_organization: bool
    short_bio: str
    details: str
    first_name: str
    last_name: str
    full_name: str
    alias: Optional[str]
    avatar: str
    cover: Optional[str]
    city: int
    knowledge: int
    knowledge_rank: int
    reputation: int
    reputation_rank: int
    join_date: Optional[datetime.datetime]
    social_profiles: List[int]
    solved_steps_count: int
    created_courses_count: int
    created_lessons_count: int
    issued_certificates_count: int
    followers_count: int

    url: str = field(init=False)

    def __post_init__(self):
        self.url = f'{StepikPlatform.BASE_URL}/users/{self.id}'


@dataclass
class UsersResponse(ObjectResponse[User]):
    users: List[User]

    def get_objects(self) -> List[User]:
        return self.users
