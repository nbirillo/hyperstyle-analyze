from enum import Enum, unique


@unique
class EvaluationMetricsColumns(Enum):
    ACCURACY = 'accuracy'
    PRECISION = 'precision'
    RECALL = 'recall'
    F_SCORE = 'f_score'
