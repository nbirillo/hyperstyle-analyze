from enum import Enum, unique

DEFAULT_NUMBER_OF_SAMPLES = 1000


@unique
class ConfigArguments(Enum):
    NUMBER_OF_SAMPLES = 'number_of_samples'
    RANDOM_STATE = 'random_state'
    #
    BINS = 'bins'
    LENGTH = 'length'
    #
    IDS = 'ids'
