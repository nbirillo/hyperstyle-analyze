from typing import List

import numpy as np
import pandas as pd


def down_sample(y: pd.Series, size: int = None, seed: int = 42) -> List[int]:
    np.random.seed(seed)
    subsample = []

    if size is None:
        n_smp = y.value_counts().min()
    else:
        n_smp = int(size / len(y.value_counts().index))

    for label in y.value_counts().index:
        samples = y[y == label].index.values
        index_range = range(samples.shape[0])

        indexes = np.random.choice(index_range, size=n_smp, replace=False)
        subsample += samples[indexes].tolist()

    return subsample
