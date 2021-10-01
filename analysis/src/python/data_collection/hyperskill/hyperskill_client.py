import argparse
import sys
from enum import Enum
from typing import List

from analysis.src.python.data_collection.api.platform_api import PlatformClient
from analysis.src.python.data_collection.hyperskill.api.projects import ProjectsResponse, ProjectsRequestParams, Project
from analysis.src.python.data_collection.hyperskill.api.search_results import SearchResult, SearchResultsRequestParams, \
    SearchResultsResponse
from analysis.src.python.data_collection.hyperskill.api.steps import StepsRequestParams, StepsResponse, Step
from analysis.src.python.data_collection.hyperskill.api.topics import TopicsResponse, TopicsRequestParams, Topic
from analysis.src.python.data_collection.hyperskill.api.tracks import TracksResponse, TracksRequestParams, Track


class ObjectClass(str, Enum):
    STEP = 'step'
    SEARCH_RESULT = 'search-result'
    TRACK = 'track'
    PROJECT = 'project'
    TOPIC = 'topic'


class HyperskillClient(PlatformClient):
    API_HOST = 'https://hyperskill.org/'

    def __init__(self):
        super().__init__(self.API_HOST)

    def get_steps(self, topic_id: int = None, save_to_csv: bool = False, ids: List[int] = None) -> List[Step]:
        return self.get_objects(ObjectClass.STEP, Step, StepsResponse, StepsRequestParams(topic=topic_id), ids,
                                save_to_csv)

    def get_tracks(self, save_to_csv: bool = False, ids: List[int] = None) -> List[Track]:
        return self.get_objects(ObjectClass.TRACK, Track, TracksResponse, TracksRequestParams(), ids,
                                save_to_csv)

    def get_projects(self, save_to_csv: bool = False, ids: List[int] = None) -> List[Project]:
        return self.get_objects(ObjectClass.PROJECT, Project, ProjectsResponse, ProjectsRequestParams(), ids,
                                save_to_csv)

    def get_topics(self, save_to_csv: bool = False, ids: List[int] = None) -> List[Topic]:
        return self.get_objects(ObjectClass.TOPIC, Topic, TopicsResponse, TopicsRequestParams(), ids,
                                save_to_csv)

    def get_search_results(self, query: str, save_to_csv: bool = False) -> List[SearchResult]:
        return self.get_objects(ObjectClass.SEARCH_RESULT, SearchResult, SearchResultsResponse,
                                SearchResultsRequestParams(query=query), save_to_csv=save_to_csv)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--object', type=str, help='path to output dir with result', required=True,
                        choices=['project', 'topic', 'step', 'search-result', 'track'])
    parser.add_argument('--query', type=str, default=None, help='query for search_results request')
    parser.add_argument('--topic-id', type=str, default=None, help='topic id for steps request')
    parser.add_argument('--ids', nargs='*', type=int, default=None, help='topic id for steps request')

    args = parser.parse_args(sys.argv[1:])

    api = HyperskillClient()
    if args.object == ObjectClass.TOPIC:
        api.get_topics(save_to_csv=True)
    elif args.object == ObjectClass.TRACK:
        api.get_tracks(save_to_csv=True)
    elif args.object == ObjectClass.STEP:
        api.get_steps(args.topic_id, save_to_csv=True)
    elif args.object == ObjectClass.PROJECT:
        api.get_projects(save_to_csv=True)
    elif args.object == ObjectClass.SEARCH_RESULT:
        api.get_search_results(args.query, save_to_csv=True)
