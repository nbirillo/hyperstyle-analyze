from typing import Dict, List

from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from analysis.src.python.evaluation.qodana.imitation_model.utils.model import EvaluationMetricsColumns


def get_evaluation_metrics(test_target: List[int], pred_target: List[int]) -> Dict[str, float]:
    precision, recall, f_score, _ = precision_recall_fscore_support(test_target, pred_target, average='binary')
    accuracy = accuracy_score(test_target, pred_target)
    return {
        EvaluationMetricsColumns.PRECISION.value: precision,
        EvaluationMetricsColumns.RECALL.value: recall,
        EvaluationMetricsColumns.ACCURACY.value: accuracy,
        EvaluationMetricsColumns.F_SCORE.value: f_score,
    }
