from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Dict, Optional

from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

from analysis.src.python.evaluation.common.yaml_util import parse_yaml


@unique
class ModelConfigField(Enum):
    MODEL = 'model'
    PARAMETERS = 'parameters'


@dataclass(frozen=True)
class ModelConfig:
    model: str
    parameters: Optional[Dict[Any, Any]]

    @classmethod
    def from_yalm(cls, config_path: str) -> 'ModelConfig':
        config = parse_yaml(config_path)

        return ModelConfig(config[ModelConfigField.MODEL.value],
                           config[ModelConfigField.PARAMETERS.value])

    def get_line_name(self) -> str:
        name = self.model
        if self.parameters is not None:
            for key, value in self.parameters.items():
                name += f'_{key}_{value}'
        return name


def get_model_config(config_path: str) -> ModelConfig:
    return ModelConfig.from_yalm(config_path)


model_to_class = {
    'knn': KNeighborsClassifier,
    'xgb': XGBClassifier
}


def get_model(config: ModelConfig):
    model = model_to_class.get(config.model)
    if model is None:
        raise Exception(f'Model {config.model} not implemented')
    if config.parameters is not None:
        return model(**config.parameters)
    return model()
