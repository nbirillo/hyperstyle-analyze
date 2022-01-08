import datetime
from dataclasses import dataclass
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse

"""
This file contains classes, which describe submission entity from Stepik platform. 
Submission is a user's attempt to solve the step's task and platform's feedback on this solution.

Steps are available by API requests, described at  
    https://stepic.org/api/docs/#!/submissions
"""


@dataclass
class SubmissionRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Submission(Object):
    id: int
    status: str
    score: float
    hint: str
    feedback: str
    time: Optional[datetime.datetime]
    reply: str
    reply_url: str
    attempt: int
    session: int
    eta: int


@dataclass(frozen=True)
class SubmissionsResponse(ObjectResponse[Submission]):
    submissions: List[Submission]

    def get_objects(self) -> List[Submission]:
        return self.submissions
