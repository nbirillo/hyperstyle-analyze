from enum import Enum, unique

DEFAULT_NUMBER_OF_SAMPLES = 100
DEFAULT_RANDOM_STATE = None
DEFAULT_INCLUDE_BOUNDARIES = False


@unique
class ConfigArguments(Enum):
    NUMBER_OF_SAMPLES = 'number_of_samples'
    RANDOM_STATE = 'random_state'
    #
    BINS = 'bins'
    COUNT = 'count'
    INCLUDE_BOUNDARIES = 'include_boundaries'
    #
    IDS = 'ids'
