import xgboost as xgb
from sklearn.neighbors import KNeighborsClassifier

from analysis.src.python.evaluation.common.yaml_util import parse_yaml

model_to_class = {
    'knn': KNeighborsClassifier,
    'xgb': xgb.XGBClassifier
}


def get_classification_model(config_path: str):
    config = parse_yaml(config_path)
    model = model_to_class[config['model']]
    params = config['parameters']
    if params is not None:
        return model(**params)
    return model()
