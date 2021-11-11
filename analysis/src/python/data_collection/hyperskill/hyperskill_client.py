import os
from typing import Callable, Dict, List, Optional

from analysis.src.python.data_collection.api.platform_client import PlatformClient
from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object
from analysis.src.python.data_collection.hyperskill.api.projects import Project, ProjectsResponse
from analysis.src.python.data_collection.hyperskill.api.search_results import \
    SearchResult, SearchResultsRequestParams, SearchResultsResponse
from analysis.src.python.data_collection.hyperskill.api.steps import StepsRequestParams, StepsResponse
from analysis.src.python.data_collection.hyperskill.api.submissions import Submission, SubmissionRequestParams, \
    SubmissionResponse
from analysis.src.python.data_collection.hyperskill.api.topics import Topic, TopicsResponse
from analysis.src.python.data_collection.hyperskill.api.tracks import Track, TracksResponse
from analysis.src.python.data_collection.hyperskill.api.users import User, UserResponse
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform, ObjectClass


class HyperskillClient(PlatformClient):

    def __init__(self):
        client_id = os.environ.get('HYPERSKILL_CLIENT_ID')
        client_secret = os.environ.get('HYPERSKILL_CLIENT_SECRET')
        super().__init__(HyperskillPlatform.BASE_URL, client_id, client_secret)

        self._get_objects_by_class: Dict[
            ObjectClass, Callable[[Optional[List[int]], Optional[int]], List[Object]]] = {
            ObjectClass.TOPIC: self.get_topics,
            ObjectClass.TRACK: self.get_tracks,
            ObjectClass.PROJECT: self.get_projects,
            ObjectClass.USER: self.get_users,
            ObjectClass.STEP: self.get_steps,
            ObjectClass.SUBMISSION: self.get_submissions,
        }

    def get_objects(self, object: str, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Object]:
        if object not in ObjectClass.values():
            return self.get_search_result(object, count)
        else:
            return self._get_objects_by_class[ObjectClass(object)](ids, count)

    def get_search_result(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        return self._get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                 SearchResultsRequestParams(query=query), count=count)

    def get_steps(self, ids: Optional[List[int]] = None,
                  count: Optional[int] = None,
                  topic_ids: Optional[List[int]] = None):
        steps = []
        topic_ids = topic_ids if topic_ids is not None else [topic.id for topic in self.get_topics()]
        for topic_id in topic_ids:
            steps += self._get_objects(ObjectClass.STEP, StepsResponse, StepsRequestParams(ids=ids, topic=topic_id))
            if count is not None and len(steps) >= count:
                return steps[:count]
        return steps

    def get_topics(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Topic]:
        return self._get_objects(ObjectClass.TOPIC, TopicsResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_projects(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Project]:
        return self._get_objects(ObjectClass.PROJECT, ProjectsResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_tracks(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Track]:
        return self._get_objects(ObjectClass.TRACK, TracksResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_users(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[User]:
        return self._get_objects(ObjectClass.USER, UserResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_submissions(self, ids: Optional[List[int]] = None, count: Optional[int] = None,
                        step_ids: Optional[List[int]] = None,
                        user_ids: Optional[List[int]] = None) -> List[Submission]:
        if user_ids is None:
            return self._get_objects(ObjectClass.SUBMISSION, SubmissionResponse,
                                     SubmissionRequestParams(ids=ids), count=count)

        submissions = []
        for user_id in user_ids:
            submissions += self._get_objects(ObjectClass.SUBMISSION, SubmissionResponse,
                                             SubmissionRequestParams(ids=ids, step=step_ids, user=user_id))
            if count is not None and len(submissions) >= count:
                return submissions[:count]
        return submissions
