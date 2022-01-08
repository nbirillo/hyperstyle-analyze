import datetime
from dataclasses import dataclass
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform

"""
This file contains classes, which describe submission entity from Hyperskill platform. 
Submission is a user's attempt to solve the step's task and platform's feedback on this solution.

Steps are available by API requests, described at  
    https://hyperskill.org/api/docs/#submissions-list
    https://hyperskill.org/api/docs/#submissions-read
"""


@dataclass
class SubmissionRequestParams(BaseRequestParams):
    step: Optional[List[int]] = None
    user: Optional[int] = None


@dataclass
class Reply:
    language: str
    code: str


@dataclass
class Quality:
    code: str
    text: str


@dataclass
class Error:
    code: str
    text: str
    line: str
    line_number: int
    column_number: int
    category: str
    difficulty: str
    influence_on_penalty: int


@dataclass
class CodeStyle:
    quality: Quality
    errors: List[Error]


@dataclass
class Feedback:
    message: str
    code_style: CodeStyle


@dataclass
class Submission(Object):
    id: int
    attempt: int
    eta: int
    feedback: Optional[Feedback]
    hint: str
    reply: Optional[Reply]
    initial_status: str
    status: str
    client: str
    step: int
    time: datetime.datetime
    can_download_test_set: bool
    is_downloaded_test: bool
    is_free_test: bool
    next_free_test_available_at: Optional[datetime.datetime]
    is_samples_test: bool
    failed_test_number: Optional[int]
    solving_context: str
    is_published: bool

    def __post_init__(self):
        self.url = f'{HyperskillPlatform.BASE_URL}/submissions/{self.id}'


@dataclass
class SubmissionResponse(ObjectResponse[Submission]):
    submissions: List[Submission]

    def get_objects(self) -> List[Submission]:
        return self.submissions
