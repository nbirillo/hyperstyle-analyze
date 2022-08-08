from enum import Enum
from typing import Callable, List

import numpy as np


class AggregateFunction(Enum):
    MIN = 'min'
    MAX = 'max'
    MEAN = 'mean'
    MEDIAN = 'median'

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]

    def to_function(self) -> Callable:
        to_function = {
            AggregateFunction.MIN: np.min,
            AggregateFunction.MAX: np.max,
            AggregateFunction.MEAN: np.mean,
            AggregateFunction.MEDIAN: np.median,
        }

        return to_function[self]
