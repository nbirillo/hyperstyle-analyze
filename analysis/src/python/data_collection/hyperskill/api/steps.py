import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe step entity from Hyperskill platform.
Step is a task where user needs to solve a problem or answer a question.
Steps are available by API requests, described at
    https://hyperskill.org/api/docs/#steps-list
    https://hyperskill.org/api/docs/#steps-read
"""


@dataclass
class StepsRequestParams(BaseRequestParams):
    topic: Optional[int] = None


@dataclass(frozen=True)
class Options:
    task_type: Optional[str]
    lesson_type: Optional[str]
    title: Optional[str]
    description_text: Optional[str]
    description_format: Optional[str]
    code_templates_header_lines_count: Optional[int]
    code_templates_footer_lines_count: Optional[int]


@dataclass(frozen=True)
class Block:
    name: str
    text: str
    options: Options


@dataclass(frozen=True)
class CommentStatistics:
    thread: str
    total_count: int


@dataclass(frozen=True)
class LikesStatistics:
    subject: str
    value: int
    total_count: int


@dataclass(frozen=True)
class Step(Object):
    block: Block
    bloom_level: Optional[int]
    can_abandon: bool
    can_skip: bool
    check_profile: str
    comments_statistics: List[CommentStatistics]
    content_created_at: Optional[datetime.datetime]
    id: int
    is_abandoned: bool
    is_completed: bool
    is_cribbed: bool
    is_recommended: bool
    is_next: bool
    is_skipped: bool
    last_completed_at: Optional[datetime.datetime]
    likes_statistics: List[LikesStatistics]
    lesson_stepik_id: int
    position: int
    seconds_to_complete: Optional[float]
    solved_by: int
    stage: Optional[int]
    stepik_id: int
    success_rate: Optional[float]
    title: str
    topic: Optional[int]
    topic_theory: Optional[int]
    type: str
    updated_at: datetime.datetime
    content_updated_at: Optional[datetime.datetime]
    progress_updated_at: Optional[datetime.datetime]
    popular_ide: Optional[str]
    project: Optional[int]
    is_beta: bool
    is_deprecated: bool
    is_ide_compatible: bool
    is_remote_tested: bool
    error_issues_count: Optional[int]
    warning_issues_count: Optional[int]
    can_see_admin_toolbar: bool

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{HyperskillPlatform.BASE_URL}/learn/step/{self.id}')


@dataclass(frozen=True)
class StepsResponse(ObjectResponse[Step]):
    steps: List[Step]

    def get_objects(self) -> List[Step]:
        return self.steps
