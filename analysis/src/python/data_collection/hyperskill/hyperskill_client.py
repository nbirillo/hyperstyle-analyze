import argparse
import logging
import os
import sys
from typing import List, Optional, Callable, Dict

from analysis.src.python.data_collection.api.platform_client import PlatformClient
from analysis.src.python.data_collection.api.platform_objects import Object, BaseRequestParams
from analysis.src.python.data_collection.hyperskill.api.projects import ProjectsResponse, Project
from analysis.src.python.data_collection.hyperskill.api.search_results import \
    SearchResult, SearchResultsRequestParams, SearchResultsResponse
from analysis.src.python.data_collection.hyperskill.api.steps import StepsResponse, StepsRequestParams
from analysis.src.python.data_collection.hyperskill.api.submissions import SubmissionResponse, SubmissionRequestParams, \
    Submission
from analysis.src.python.data_collection.hyperskill.api.topics import TopicsResponse, Topic
from analysis.src.python.data_collection.hyperskill.api.tracks import TracksResponse, Track
from analysis.src.python.data_collection.hyperskill.api.users import UserResponse, User
from analysis.src.python.data_collection.hyperskill.hyperskill_objects import HyperskillPlatform, ObjectClass
from analysis.src.python.data_collection.utils.csv_utils import save_objects_to_csv

log = logging.getLogger()
log.setLevel(logging.DEBUG)


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
            ObjectClass.SUBMISSION: self.get_submissions
        }

    def get_search_result(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        return self._get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                 SearchResultsRequestParams(query=query), count=count)

    def get_objects(self, obj_class: ObjectClass,
                    ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Object]:
        return self._get_objects_by_class[obj_class](ids, count)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='object name or query to get from hyperskill', required=True)
    parser.add_argument('--ids', nargs='*', type=int, default=None, help='ids of requested objects')
    parser.add_argument('--count', type=int, default=None, help='count of requested objects')
    parser.add_argument('--output', type=str, default='results', help='path to directory where to save the results')

    args = parser.parse_args(sys.argv[1:])

    api = HyperskillClient()

    if args.object not in ObjectClass.values():
        obj_class = ObjectClass.SEARCH_RESULT
        objects = api.get_search_result(args.object, args.count)
    else:
        obj_class = ObjectClass(args.object)
        objects = api.get_objects(obj_class, args.ids, args.count)

    save_objects_to_csv(args.output, objects, obj_class)
