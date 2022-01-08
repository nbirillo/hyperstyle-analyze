from enum import Enum, unique


@unique
class ObjectClass(str, Enum):
    STEP = 'step'
    SEARCH_RESULT = 'search-result'
    TRACK = 'track'
    PROJECT = 'project'
    TOPIC = 'topic'
    USER = 'user'
    SUBMISSION = 'submission'

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class HyperskillPlatform:
    BASE_URL = 'https://hyperskill.org'
    CLIENT_ID = 'HYPERSKILL_CLIENT_ID'
    CLIENT_SECRET = 'HYPERSKILL_CLIENT_SECRET'
