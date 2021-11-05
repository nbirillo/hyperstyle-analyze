from enum import Enum


class ObjectClass(str, Enum):
    SEARCH_RESULT = 'search-result'
    LESSON = 'lesson'
    COURSE = 'course'
    STEP = 'step'
    USER = 'user'
    SUBMISSION = 'submission'


class StepikPlatform:
    BASE_URL = 'https://stepik.org'
