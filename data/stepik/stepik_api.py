import urllib
from dataclasses import asdict
from typing import List, Dict

import pandas as pd
import requests
from dacite import from_dict

from data.stepik.api.courses import CoursesResponse, Course
from data.stepik.api.search_results import SearchResultsRequestParams, SearchResultsResponse, SearchResult
from data.utils.csv import CsvWriter
from data.utils.json import kebab_to_snake_case

API_HOST = 'https://stepik.org'

SEARCH_RESULTS_DOMAIN = 'search-results'

COURSES_DOMAIN = 'courses'


def get_token() -> str:
    client_id = "7GBIAS0GVQfzezxPpfAQhCb1Pp9qCta8lUII7ocd"
    client_secret = "Z5atw6zBDNuoEDcLVqDU6TAD4r56moGoZYq1NJFecLoD7FlibSyK22J5RnZbOAYggqHIVag4PPXgpVZIln5wAJNQzn7cAUqliBMeCSLMX4VqIFZuwzrTbC76d7Qe3axF"
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    response = requests.post('{}/oauth2/token/'.format(API_HOST),
                             data={'grant_type': 'client_credentials'},
                             auth=auth)
    token = response.json().get('access_token', None)
    if not token:
        print('Unable to authorize with provided credentials')
        exit(1)
    return token


def fetch_object(token: str, obj_class: str, obj_id: int = None, params: Dict[str, str] = None) -> Dict:
    api_url = '{}/api/{}s'.format(API_HOST, obj_class, obj_id)
    if obj_id:
        api_url = '{}/{}'.format(api_url, obj_id)
    if params:
        api_url = '{}?{}'.format(api_url, urllib.parse.urlencode(params))
    response = requests.get(api_url, headers={'Authorization': 'Bearer ' + token}).json()
    return response


def get_search_results(token: str, query: str, pages_count: int = 10) -> List[SearchResult]:
    search_results = []
    for p in range(1, pages_count):
        params = SearchResultsRequestParams(query, page=p)
        try:
            response = fetch_object(token, 'search-result', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=SearchResultsResponse, data=response_json)
            search_results_to_csv(response.search_results)
            search_results += response.search_results
        except Exception as e:
            print(f'Unable to get search results: {e}')
    return search_results


def get_courses(token: str, search_results: List[SearchResult]) -> List[Course]:
    courses = []
    for search_result in search_results:
        try:
            response = fetch_object(token, 'course', obj_id=search_result.course)
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=CoursesResponse, data=response_json)
            courses += response.courses
        except Exception as e:
            print(f'Unable to get courses: {e}')
    return courses


def search_results_to_csv(search_results: List[SearchResult]):
    csv_writer = CsvWriter("result", "search_result_python.csv", list(SearchResult.__annotations__.keys()))
    for search_result in search_results:
        csv_writer.write_csv(asdict(search_result))


def courses_to_csv(courses: List[Course]):
    csv_writer = CsvWriter("result", "result/courses.csv", list(Course.__annotations__.keys()))
    for course in courses:
        csv_writer.write_csv(asdict(course))


def get_unique():
    df1 = pd.read_csv("result/courses.csv")
    df2 = pd.read_csv("result/courses_python.csv")
    df = df2[df2["id"].isin(df1["id"].values).__invert__()]
    df.to_csv("result/courses_python_filtered.csv", index=False)


if __name__ == '__main__':
    # token = get_token()
    # search_results = get_search_results(token, "python", 10)
    # search_results_to_csv(search_results)
    # courses = get_courses(token, search_results)
    # courses_to_csv(courses)
    get_unique()
