import argparse
import os
import sys
from enum import Enum
from typing import List

import requests

from analysis.src.python.data_mining.api.platform_api import PlatformApi
from analysis.src.python.data_mining.stepik.api.courses import CoursesResponse, CourseRequestParams, Course
from analysis.src.python.data_mining.stepik.api.search_results import SearchResult, SearchResultsRequestParams, \
    SearchResultsResponse


class ObjectClass(str, Enum):
    COURSE = 'course'
    SEARCH_RESULT = 'search-result'


class StepicAPI(PlatformApi):
    API_HOST = 'https://stepik.org'

    def __init__(self):
        token = self._get_token()
        super().__init__(self.API_HOST, token)

    def _get_token(self) -> str:
        client_id = os.environ.get('STEPIK_CLIENT_ID')
        client_secret = os.environ.get('STEPIK_CLIENT_SECRET')

        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        response = requests.post('{}/oauth2/token/'.format(self.API_HOST),
                                 data={'grant_type': 'client_credentials'},
                                 auth=auth)
        token = response.json().get('access_token', None)
        if not token:
            print('Unable to authorize with provided credentials')
            exit(1)
        return token

    def get_courses(self, course_ids: List[int], save_to_csv=False) -> List[Course]:
        return self.get_objects(ObjectClass.COURSE, Course, CoursesResponse, CourseRequestParams(), course_ids,
                                save_to_csv)

    def get_search_results(self, query: str, save_to_csv=False) -> List[SearchResult]:
        return self.get_objects(ObjectClass.SEARCH_RESULT, SearchResult, SearchResultsResponse,
                                SearchResultsRequestParams(query=query), save_to_csv=save_to_csv)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['course', 'search-result'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')
    parser.add_argument('--ids', nargs="+", type=int, default=None, help='id of required object')

    args = parser.parse_args(sys.argv[1:])

    api = StepicAPI()

    if args.object == ObjectClass.COURSE:
        api.get_courses(args.ids, save_to_csv=True)
    elif args.object == ObjectClass.SEARCH_RESULT:
        api.get_search_results(args.query, save_to_csv=True)
