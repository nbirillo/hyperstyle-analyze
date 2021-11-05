import argparse
import logging
import os
import sys
from typing import List, Dict, Callable, Optional

from analysis.src.python.data_collection.api.platform_client import PlatformClient
from analysis.src.python.data_collection.api.platform_objects import Object
from analysis.src.python.data_collection.stepik.api.courses import CoursesResponse, Course
from analysis.src.python.data_collection.stepik.api.lessons import LessonsResponse
from analysis.src.python.data_collection.stepik.api.search_results import SearchResult, SearchResultsRequestParams, \
    SearchResultsResponse
from analysis.src.python.data_collection.stepik.api.steps import StepsResponse
from analysis.src.python.data_collection.stepik.api.submissions import SubmissionsResponse
from analysis.src.python.data_collection.stepik.api.users import UsersResponse
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform, ObjectClass

log = logging.getLogger()
log.setLevel(logging.DEBUG)


class StepicClient(PlatformClient):

    def __init__(self):
        client_id = os.environ.get('STEPIK_CLIENT_ID')
        client_secret = os.environ.get('STEPIK_CLIENT_SECRET')
        super().__init__(StepikPlatform.BASE_URL, client_id, client_secret)

        self._get_all_objects_by_class: Dict[ObjectClass, Callable[[], List[Object]]] = {
            ObjectClass.COURSE: self._get_courses,
            ObjectClass.LESSON: self._get_lessons,
            ObjectClass.STEP: self._get_steps,
            ObjectClass.USER: self._get_users,
            ObjectClass.SUBMISSION: self._get_submissions
        }

    def get_all_objects_by_class(self, obj_class: ObjectClass) -> List[Object]:
        return self._get_all_objects_by_class[obj_class]()

    def get_all_objects_by_query(self, query: str) -> List[SearchResult]:
        return self.get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                SearchResultsRequestParams(query=query))

    def _get_courses(self, ids: Optional[List[int]] = None) -> List[Course]:
        return self.get_objects_by_ids(ObjectClass.COURSE, ids, CoursesResponse) if ids is not None \
            else self.get_objects(ObjectClass.COURSE, CoursesResponse)

    def _get_lessons(self, ids: Optional[List[int]] = None) -> List[Course]:
        return self.get_objects_by_ids(ObjectClass.LESSON, ids, LessonsResponse) if ids is not None \
            else self.get_objects(ObjectClass.LESSON, LessonsResponse)

    def _get_steps(self, ids: Optional[List[int]] = None) -> List[Course]:
        return self.get_objects_by_ids(ObjectClass.STEP, ids, StepsResponse) if ids is not None \
            else self.get_objects(ObjectClass.STEP, StepsResponse)

    def _get_users(self, ids: Optional[List[int]] = None) -> List[Course]:
        return self.get_objects_by_ids(ObjectClass.USER, ids, UsersResponse) if ids is not None \
            else self.get_objects(ObjectClass.USER, UsersResponse)

    def _get_submissions(self, ids: Optional[List[int]] = None) -> List[Course]:
        return self.get_objects_by_ids(ObjectClass.SUBMISSION, ids, SubmissionsResponse) if ids is not None \
            else self.get_objects(ObjectClass.SUBMISSION, SubmissionsResponse, end_page=3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['course', 'lesson', 'step', 'search-result', 'user', 'submission'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')

    args = parser.parse_args(sys.argv[1:])

    client = StepicClient()

    object_class = ObjectClass(args.object)

    if object_class == ObjectClass.SEARCH_RESULT:
        client.get_all_objects_by_query(args.query)
    else:
        client.get_all_objects_by_class(object_class)
