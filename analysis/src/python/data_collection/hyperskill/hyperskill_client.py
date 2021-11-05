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
from analysis.src.python.data_collection.hyperskill.api.submissions import SubmissionResponse, SubmissionRequestParams
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

        self._get_all_objects_by_class: Dict[ObjectClass, Callable[[], List[Object]]] = {
            ObjectClass.TOPIC: self._get_topics,
            ObjectClass.TRACK: self._get_tracks,
            ObjectClass.PROJECT: self._get_projects,
            ObjectClass.USER: self._get_users,
            ObjectClass.STEP: self._get_steps,
            ObjectClass.SUBMISSION: self._get_submissions
        }

    def get_all_objects_by_class(self, obj_class: ObjectClass) -> List[Object]:
        return self._get_all_objects_by_class[obj_class]()

    def get_all_objects_by_query(self, query: str) -> List[SearchResult]:
        return self.get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                SearchResultsRequestParams(query=query))

    def _get_steps(self, ids: Optional[List[int]] = None,
                   topic_ids: Optional[List[int]] = None):
        steps = self.get_objects(ObjectClass.STEP, StepsResponse, StepsRequestParams(ids=ids))
        topic_ids = topic_ids if topic_ids is not None else [topic.id for topic in self._get_topics()]
        for topic_id in topic_ids:
            steps += self.get_objects(ObjectClass.STEP, StepsResponse, StepsRequestParams(ids=ids, topic=topic_id))

        return steps

    def _get_topics(self, ids: Optional[List[int]] = None) -> List[Topic]:
        return self.get_objects(ObjectClass.TOPIC, TopicsResponse, BaseRequestParams(ids=ids))

    def _get_projects(self, ids: Optional[List[int]] = None) -> List[Project]:
        return self.get_objects(ObjectClass.PROJECT, ProjectsResponse, BaseRequestParams(ids=ids))

    def _get_tracks(self, ids: Optional[List[int]] = None) -> List[Track]:
        return self.get_objects(ObjectClass.TRACK, TracksResponse, BaseRequestParams(ids=ids))

    def _get_users(self, ids: Optional[List[int]] = None) -> List[User]:
        return self.get_objects(ObjectClass.USER, UserResponse, BaseRequestParams(ids=ids))

    def _get_submissions(self, ids: Optional[List[int]] = None,
                         step_id: Optional[int] = None,
                         user_id: Optional[int] = None) -> List[User]:
        return self.get_objects(ObjectClass.SUBMISSION, SubmissionResponse,
                                SubmissionRequestParams(ids=ids, step=step_id, user=user_id, page_size=5), end_page=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['project', 'topic', 'step', 'search-result', 'track', 'user', 'submission'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')
    parser.add_argument('--output', type=str, default='results', help='path to directory where to save the results')

    args = parser.parse_args(sys.argv[1:])

    api = HyperskillClient()

    obj_class = ObjectClass(args.object)

    if obj_class == ObjectClass.SEARCH_RESULT:
        objects = api.get_all_objects_by_query(args.query)
    else:
        objects = api.get_all_objects_by_class(obj_class)

    save_objects_to_csv(args.output, objects, obj_class)
