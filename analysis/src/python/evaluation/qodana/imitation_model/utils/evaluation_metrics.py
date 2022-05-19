from typing import Dict, List

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from analysis.src.python.evaluation.qodana.imitation_model.utils.metrics import EvaluationMetricsColumns


def get_evaluation_metrics(test_target: np.array, pred_target: np.array) -> Dict[str, float]:
    precision, recall, f_score, _ = precision_recall_fscore_support(test_target, pred_target, average='binary')
    accuracy = accuracy_score(test_target, pred_target)
    f1 = f1_score(test_target, pred_target, average='macro')

    return {
        EvaluationMetricsColumns.PRECISION.value: precision,
        EvaluationMetricsColumns.RECALL.value: recall,
        EvaluationMetricsColumns.ACCURACY.value: accuracy,
        EvaluationMetricsColumns.F_SCORE.value: f_score,
        EvaluationMetricsColumns.F1_SCORE.value: f1
    }
