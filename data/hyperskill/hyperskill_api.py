import urllib
from dataclasses import asdict
from typing import List, Dict

import pandas as pd
import requests
from dacite import from_dict

from data.hyperskill.api.projects import Project, ProjectsRequestParams, ProjectsResponse
from data.hyperskill.api.search_results_java import SearchResult, SearchResultsRequestParams, SearchResultsResponse
from data.hyperskill.api.steps import Step, StepsRequestParams, StepsResponse
from data.hyperskill.api.topics import TopicsResponse, TopicsRequestParams, Topic
from data.hyperskill.api.tracks import TracksRequestParams, TracksResponse, Track
from data.utils.csv import CsvWriter
from data.utils.json import kebab_to_snake_case

API_HOST = 'https://hyperskill.org/'

SEARCH_RESULTS_DOMAIN = 'search-results'

COURSES_DOMAIN = 'courses'


def fetch_object(obj_class: str, obj_id: int = None, params: Dict = None) -> Dict:
    api_url = '{}/api/{}s'.format(API_HOST, obj_class)
    if obj_id:
        api_url = '{}/{}'.format(api_url, obj_id)
    if params:
        api_url = '{}?{}'.format(api_url, urllib.parse.urlencode(params))
    response = requests.get(api_url).json()
    return response


def get_search_results(query: str, pages_count: int = 10) -> List[SearchResult]:
    search_results = []
    for p in range(1, pages_count):
        print(f'Getting search_results page: {p}')
        try:
            params = SearchResultsRequestParams(query, page=p)
            response = fetch_object('search-result', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=SearchResultsResponse, data=response_json)
            search_results += response.search_results
        except Exception as e:
            print(f'Unable to get search results: {e}')
    return search_results


def get_steps(search_results: List[SearchResult]) -> List[Step]:
    steps = []
    for search_result in search_results:
        try:
            params = StepsRequestParams(topic=search_result.target_id)
            response = fetch_object('step', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=StepsResponse, data=response_json)
            steps += response.steps
        except Exception as e:
            print(f'Unable to get step: {e}')
    return steps


def get_tracks(pages_count: int = 5) -> List[Track]:
    tracks = []

    for p in range(1, pages_count):
        print(f'Getting tracks page: {p}')
        try:
            params = TracksRequestParams(page=p)
            response = fetch_object('track', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=TracksResponse, data=response_json)
            tracks += response.tracks
        except Exception as e:
            print(f'Unable to get tracks: {e}')
    return tracks


def get_projects(pages_count: int = 20) -> List[Project]:
    projects = []
    for p in range(1, pages_count):
        print(f'Getting projects page: {p}')
        try:
            params = ProjectsRequestParams(page=p)
            response = fetch_object('project', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=ProjectsResponse, data=response_json)
            projects += response.projects
        except Exception as e:
            print(f'Unable to get projects: {e}')
    return projects


def get_topics(pages_count: int = 150) -> List[Topic]:
    topics = []
    for p in range(0, pages_count):
        print(f'Getting topics page: {p}')
        try:
            params = TopicsRequestParams(page=p)
            response = fetch_object('topic', params=asdict(params))
            response_json = kebab_to_snake_case(response)
            response = from_dict(data_class=TopicsResponse, data=response_json)
            topics += response.topics
        except Exception as e:
            print(f'Unable to get topics: {e}')
    return topics


def search_results_to_csv(search_results: List[SearchResult]):
    csv_writer = CsvWriter("result", "search_result.csv", list(SearchResult.__annotations__.keys()))
    for search_result in search_results:
        csv_writer.write_csv(asdict(search_result))


def steps_to_csv(steps: List[Step]):
    csv_writer = CsvWriter("result", "steps.csv", list(Step.__annotations__.keys()))
    for step in steps:
        csv_writer.write_csv(asdict(step))


def tracks_to_csv(tracks: List[Track]):
    csv_writer = CsvWriter("result", "tracks.csv", list(Track.__annotations__.keys()))
    for track in tracks:
        csv_writer.write_csv(asdict(track))


def projects_to_csv(projects: List[Project]):
    csv_writer = CsvWriter("result", "projects.csv", list(Project.__annotations__.keys()))
    for project in projects:
        csv_writer.write_csv(asdict(project))


def topics_to_csv(topics: List[Topic]):
    csv_writer = CsvWriter("result", "topics-4.csv", list(Topic.__annotations__.keys()))
    for topic in topics:
        csv_writer.write_csv(asdict(topic))


if __name__ == '__main__':
    # search_results = get_search_results("java", 10)
    # search_results_to_csv(search_results)
    # courses = get_steps(search_results)
    # steps_to_csv(courses)
    # tracks = get_tracks()
    # tracks_to_csv(tracks)
    # projects = get_projects()
    # projects_to_csv(projects)
    topics = get_topics()
    topics_to_csv(topics)
