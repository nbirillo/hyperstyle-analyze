import argparse
import os
import sys
from enum import Enum
from typing import List

import requests

from data.common_api.platform_api import PlatformApi
from data.common_api.response import PageRequestParams
from data.common_api.utils import save_objects_to_csv
from data.stepik.api.courses import CoursesResponse, Course, CourseRequestParams
from data.stepik.api.search_results import SearchResultsRequestParams, SearchResultsResponse, SearchResult

API_HOST = 'https://stepik.org'


class ObjectClass(str, Enum):
    COURSE = 'course'
    SEARCH_RESULT = 'search-result'


def get_token() -> str:
    client_id = os.environ.get('STEPIK_CLIENT_ID')
    client_secret = os.environ.get('STEPIK_CLIENT_SECRET')

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    response = requests.post('{}/oauth2/token/'.format(API_HOST),
                             data={'grant_type': 'client_credentials'},
                             auth=auth)
    token = response.json().get('access_token', None)
    if not token:
        print('Unable to authorize with provided credentials')
        exit(1)
    return token


def get_and_save_object(obj_class: ObjectClass,
                        obj_response_type,
                        obj_type,
                        params: PageRequestParams,
                        ids: List[int] = None):
    token = get_token()
    api = PlatformApi(API_HOST, token)
    if ids is None:
        objects = api.get_objects_from_pages(obj_class, obj_response_type, params)
    else:
        objects = api.get_objects_by_ids(obj_class, obj_response_type, params, ids)
    save_objects_to_csv(objects, obj_class, obj_type)


def get_courses(course_ids: List[int]):
    get_and_save_object(ObjectClass.COURSE, CoursesResponse, Course, CourseRequestParams(), course_ids)


def get_search_results(query: str):
    get_and_save_object(ObjectClass.SEARCH_RESULT, SearchResultsResponse, SearchResult,
                        SearchResultsRequestParams(query=query))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['course', 'search-result'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')
    parser.add_argument('--ids', nargs="+", type=int, default=None, help='id of required object')

    args = parser.parse_args(sys.argv[1:])

    if args.object == ObjectClass.COURSE:
        get_courses(args.ids)
    elif args.object == ObjectClass.SEARCH_RESULT:
        get_search_results(args.query)
