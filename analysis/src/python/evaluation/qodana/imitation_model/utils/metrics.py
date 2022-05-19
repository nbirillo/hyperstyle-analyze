from enum import Enum, unique


@unique
class EvaluationMetricsColumns(Enum):
    ACCURACY = 'accuracy'
    PRECISION = 'precision'
    RECALL = 'recall'
    F_SCORE = 'f_score'
    F1_SCORE = 'f1_score'

    TRAIN_SIZE = 'train_size'
    TEST_SIZE = 'test_size'
    ISSUES_IN_TRAIN = 'issues_in_train'
    ISSUES_IN_TEST = 'issues_in_test'

    TEST_TARGET = 'test_target'
    TRAIN_TARGET = 'train_target'
