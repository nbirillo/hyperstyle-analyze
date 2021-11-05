from enum import Enum


class ObjectClass(str, Enum):
    STEP = 'step'
    SEARCH_RESULT = 'search-result'
    TRACK = 'track'
    PROJECT = 'project'
    TOPIC = 'topic'
    USER = 'user'
    SUBMISSION = 'submission'


class HyperskillPlatform:
    BASE_URL = 'https://hyperskill.org'
