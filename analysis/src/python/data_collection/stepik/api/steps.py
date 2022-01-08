import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform

"""
This file contains classes, which describe step entity from Stepik platform.
Step is a task where user needs to solve a problem or answer a question.
Steps are available by API requests, described at
    https://stepic.org/api/docs/#!/steps
"""


@dataclass
class StepRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Block:
    name: Optional[str]
    text: Optional[str]
    video: Optional[str]
    subtitle_files: Optional[List[str]]


@dataclass(frozen=True)
class Step(Object):
    id: int
    lesson: str
    position: int
    status: int
    block: Block
    actions: str
    progress: str
    subscriptions: List[str]
    instruction: str
    session: str
    instruction_type: str
    viewed_by: int
    passed_by: int
    correct_ratio: Optional[int]
    worth: int
    is_solutions_unlocked: bool
    solutions_unlocked_attempts: int
    has_submissions_restrictions: bool
    max_submissions_count: Optional[int]
    variation: int
    variations_count: int
    is_enabled: bool
    needs_plan: Optional[str]
    create_date: datetime.datetime
    update_date: datetime.datetime
    discussions_count: int
    discussion_proxy: str
    discussion_threads: List[str]

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{StepikPlatform.BASE_URL}/lesson/{self.lesson}/step/{self.id}')


@dataclass(frozen=True)
class StepsResponse(ObjectResponse[Step]):
    steps: List[Step]

    def get_objects(self) -> List[Step]:
        return self.steps
