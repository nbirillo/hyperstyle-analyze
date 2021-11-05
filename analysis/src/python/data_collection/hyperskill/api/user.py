import datetime
from dataclasses import dataclass
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_platform import HyperskillPlatform


@dataclass
class UserRequestParams(BaseRequestParams):
    pass


@dataclass
class Gamification:
    active_days: int
    daily_step_completed_count: int
    passed_problems: int
    passed_projects: int
    passed_topics: int
    progress_updated_at: Optional[datetime.datetime]


@dataclass
class CommentsPosted:
    comment: Optional[int]
    hint: Optional[int]
    useful_link: Optional[int]
    solutions: Optional[int]


@dataclass
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

    def __post_init__(self):
        self.url = f'{HyperskillPlatform.BASE_URL}/profile/{self.id}'


@dataclass
class UserResponse(ObjectResponse[User]):
    users: List[User]

    def get_objects(self) -> List[User]:
        return self.users
