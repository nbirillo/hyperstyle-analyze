import argparse
import sys
from enum import Enum

from data.common_api.platform_api import PlatformApi
from data.common_api.response import PageRequestParams
from data.common_api.utils import save_objects_to_csv
from data.hyperskill.api.projects import Project, ProjectsRequestParams, ProjectsResponse
from data.hyperskill.api.search_results import SearchResult, SearchResultsRequestParams, SearchResultsResponse
from data.hyperskill.api.steps import Step, StepsRequestParams, StepsResponse
from data.hyperskill.api.topics import TopicsResponse, TopicsRequestParams, Topic
from data.hyperskill.api.tracks import TracksRequestParams, TracksResponse, Track

API_HOST = 'https://hyperskill.org/'


class ObjectClass(str, Enum):
    STEP = 'step'
    SEARCH_RESULT = 'search-result'
    TRACK = 'track'
    PROJECT = 'project'
    TOPIC = 'topic'


def get_and_save_object(obj_class: ObjectClass,
                        obj_response_type,
                        obj_type,
                        params: PageRequestParams):
    api = PlatformApi(API_HOST)
    objects = api.get_objects_from_pages(obj_class, obj_response_type, params)
    save_objects_to_csv(objects, obj_class, obj_type)


def get_search_results(query: str):
    get_and_save_object(ObjectClass.SEARCH_RESULT, SearchResultsResponse, SearchResult,
                        SearchResultsRequestParams(query=query))


def get_steps(topic_id: int):
    get_and_save_object(ObjectClass.STEP, StepsResponse, Step, StepsRequestParams(topic=topic_id))


def get_tracks():
    get_and_save_object(ObjectClass.TRACK, TracksResponse, Track, TracksRequestParams())


def get_projects():
    get_and_save_object(ObjectClass.PROJECT, ProjectsResponse, Project, ProjectsRequestParams())


def get_topics():
    get_and_save_object(ObjectClass.TOPIC, TopicsResponse, Topic, TopicsRequestParams())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['project', 'topic', 'step', 'search-result', 'track'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')
    parser.add_argument('--topic-id', type=str, default=None, help='topic id for steps request')

    args = parser.parse_args(sys.argv[1:])

    if args.object == ObjectClass.TOPIC:
        get_topics()
    elif args.object == ObjectClass.TRACK:
        get_tracks()
    elif args.object == ObjectClass.STEP:
        get_steps(args.topic_id)
    elif args.object == ObjectClass.PROJECT:
        get_projects()
    elif args.object == ObjectClass.SEARCH_RESULT:
        get_search_results(args.query)
