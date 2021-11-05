import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from analysis.src.python.data_collection.api.platform_objects import ObjectResponse, BaseRequestParams, Object
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform


@dataclass
class SubmissionRequestParams(BaseRequestParams):
    pass


@dataclass
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


@dataclass
class SubmissionsResponse(ObjectResponse[Submission]):
    submissions: List[Submission]

    def get_objects(self) -> List[Submission]:
        return self.submissions
