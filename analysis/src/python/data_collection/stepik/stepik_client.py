import os
from typing import List, Dict, Callable, Optional, Type, TypeVar

from analysis.src.python.data_collection.api.platform_client import PlatformClient
from analysis.src.python.data_collection.api.platform_objects import Object, ObjectResponse, BaseRequestParams
from analysis.src.python.data_collection.stepik.api.courses import CoursesResponse, Course
from analysis.src.python.data_collection.stepik.api.lessons import LessonsResponse, Lesson
from analysis.src.python.data_collection.stepik.api.search_results import SearchResult, SearchResultsRequestParams, \
    SearchResultsResponse
from analysis.src.python.data_collection.stepik.api.steps import StepsResponse, Step
from analysis.src.python.data_collection.stepik.api.submissions import SubmissionsResponse, Submission
from analysis.src.python.data_collection.stepik.api.users import UsersResponse, User
from analysis.src.python.data_collection.stepik.stepik_objects import StepikPlatform, ObjectClass

T = TypeVar('T', bound=Object)


class StepikClient(PlatformClient):

    def __init__(self):
        client_id = os.environ.get('STEPIK_CLIENT_ID')
        client_secret = os.environ.get('STEPIK_CLIENT_SECRET')
        super().__init__(StepikPlatform.BASE_URL, client_id, client_secret)

        self._get_objects_by_class: Dict[
            ObjectClass, Callable[[Optional[List[int]], Optional[int]], List[Object]]] = {
            ObjectClass.COURSE: self.get_courses,
            ObjectClass.LESSON: self.get_lessons,
            ObjectClass.STEP: self.get_steps,
            ObjectClass.USER: self.get_users,
            ObjectClass.SUBMISSION: self.get_submissions
        }

    def get_objects(self, object: str, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Object]:
        if object not in ObjectClass.values():
            return self.get_search_result(object, count)
        else:
            return self._get_objects_by_class[ObjectClass(object)](ids, count)

    def get_search_result(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        return self._get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                 SearchResultsRequestParams(query=query), count=count)

    def get_courses(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Course]:
        return self._get_objects_default(ids, count, ObjectClass.COURSE, CoursesResponse)

    def get_lessons(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Lesson]:
        return self._get_objects_default(ids, count, ObjectClass.LESSON, LessonsResponse)

    def get_steps(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Step]:
        return self._get_objects_default(ids, count, ObjectClass.STEP, StepsResponse)

    def get_users(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[User]:
        return self._get_objects_default(ids, count, ObjectClass.USER, UsersResponse)

    def get_submissions(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Submission]:
        return self._get_objects_default(ids, count, ObjectClass.SUBMISSION, SubmissionsResponse)

    def _get_objects_default(self,
                             ids: Optional[List[int]],
                             count: Optional[int],
                             obj_class: ObjectClass,
                             obj_response_type: Type[ObjectResponse[T]],
                             params: BaseRequestParams = BaseRequestParams()) -> List[T]:
        return self._get_objects_by_ids(obj_class, ids, obj_response_type, params, count=count) if ids is not None \
            else self._get_objects(obj_class, obj_response_type, params, count=count)
