from dataclasses import dataclass, field
from typing import List

from analysis.src.python.data_collection.api.platform_entities import RequestParams, Object, Response


@dataclass
class StepsRequestParams(RequestParams):
    topic: int = 0


@dataclass
class Options:
    task_type: str
    lesson_type: str
    title: str
    description_text: str
    description_format: str


@dataclass
class Block:
    name: str
    text: str
    options: Options


@dataclass
class CommentStatistics:
    thread: str
    total_count: int


@dataclass
class LikesStatistics:
    subject: str
    value: int
    total_count: int


@dataclass
class Step(Object):
    id: int
    title: str
    project: int
    bloom_level: int
    seconds_to_complete: float
    can_abandon: bool
    success_rate: float
    solved_by: int
    topic: str
    can_skip: bool
    check_profile: str
    block: Block
    comments_statistics: List[CommentStatistics]
    content_created_at: str
    last_completed_at: str
    likes_statistics: LikesStatistics
    lesson_stepik_id: int
    stepik_id: int
    position: int
    stage: int
    topic_theory: str
    type: str
    popular_ide: str
    is_abandoned: bool
    is_completed: bool
    is_cribbed: bool
    is_recommended: bool
    is_next: bool
    is_skipped: bool
    url: str = field(init=False)

    def __post_init__(self):
        self.url = f'https://hyperskill.org/learn/step/{self.id}'


@dataclass
class StepsResponse(Response[Step]):
    steps: List[Step]

    def get_objects(self) -> List[Step]:
        return self.steps
