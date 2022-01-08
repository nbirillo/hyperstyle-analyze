import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform

"""
This file contains classes, which describe lesson entity from Stepik platform. Lesson is a group of steps.
Lessons are available by API requests, described at  
    https://stepic.org/api/docs/#!/lessons
"""


@dataclass
class LessonRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Lesson(Object):
    id: int
    steps: List[int]
    actions: str
    progress: str
    subscriptions: str
    viewed_by: int
    passed_by: int
    time_to_complete: Optional[int]
    cover_url: str
    is_comments_enabled: bool
    is_exam_without_progress: bool
    is_blank: bool
    is_draft: bool
    is_orphaned: bool
    courses: List[int]
    units: List[int]
    owner: str
    language: List[str]
    is_featured: bool
    is_public: bool
    title: str
    slug: str
    create_date: datetime.datetime
    update_date: datetime.datetime
    learners_group: str
    testers_group: str
    moderators_group: str
    assistants_group: str
    teachers_group: str
    admins_group: str
    discussions_count: str
    discussion_proxy: str
    discussion_threads: List[str]
    epic_count: int
    abuse_count: int
    vote_delta: int
    vote: str
    lti_consumer_key: str
    lti_secret_key: str
    lti_private_profile: bool

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{StepikPlatform.BASE_URL}/lesson/{self.id}')


@dataclass(frozen=True)
class LessonsResponse(ObjectResponse[Lesson]):
    lessons: List[Lesson]

    def get_objects(self) -> List[Lesson]:
        return self.lessons
