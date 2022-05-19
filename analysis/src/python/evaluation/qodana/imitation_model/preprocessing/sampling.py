import numpy as np


def down_sample(target: np.array, size: int = None, random: bool = True, seed: int = 42) -> np.array:
    """ Select data subsample which contains equal samples of each class according to `y`. """

    subsample = []
    values = target.value_counts()
    subsample_size = values.min() if size is None else int(size / values.shape[0])

    if random:
        np.random.seed(seed)

    for value in values.index:
        value_subsample = target[target == value].index.values.tolist()

        if random:
            value_subsample = np.random.choice(value_subsample, size=subsample_size, replace=False)
        else:
            value_subsample = value_subsample[:subsample_size]

        subsample += list(value_subsample)

    return np.array(subsample)
