import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe user entity from Hyperskill platform.
Users information is available by API requests, described at
    https://hyperskill.org/api/docs/#users-list
    https://hyperskill.org/api/docs/#users-read
"""


@dataclass
class UserRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Gamification:
    active_days: int
    daily_step_completed_count: int
    passed_problems: int
    passed_projects: int
    passed_topics: int
    progress_updated_at: Optional[datetime.datetime]


@dataclass(frozen=True)
class CommentsPosted:
    comment: Optional[int]
    hint: Optional[int]
    useful_link: Optional[int]
    solutions: Optional[int]


@dataclass(frozen=True)
class User(Object):
    id: int
    avatar: str
    badge_title: str
    bio: str
    fullname: str
    gamification: Gamification
    invitation_code: str
    comments_posted: CommentsPosted
    username: str
    selected_tracks: List[int]
    completed_tracks: List[int]
    country: Optional[str]
    languages: List[str]
    experience: Optional[str]
    github_username: Optional[str]
    linkedin_username: Optional[str]
    twitter_username: Optional[str]
    reddit_username: Optional[str]
    facebook_username: Optional[str]
    discord_id: Optional[str]

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{HyperskillPlatform.BASE_URL}/profile/{self.id}')


@dataclass(frozen=True)
class UserResponse(ObjectResponse[User]):
    users: List[User]

    def get_objects(self) -> List[User]:
        return self.users
