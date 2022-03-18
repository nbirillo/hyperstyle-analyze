import logging

import pandas as pd
import torch
from analysis.src.python.evaluation.common.csv_util import ColumnName
from torch.utils.data import Dataset
from transformers import RobertaTokenizer

from analysis.src.python.evaluation.qodana.imitation_model.roberta.util import DatasetColumnArgument

logger = logging.getLogger(__name__)


class QodanaDataset(Dataset):
    """ MarkingArgument.ID.value is an id of the solution that corresponds to the line
        MarkingArgument.INSPECTIONS.value is a target column name in dataset
        ColumnName.CODE.value is an observation column name in dataset where lines of code are stored
    """

    def __init__(self, data_path: str, context_length: int):
        super().__init__()
        df = pd.read_csv(data_path)
        tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        code = list(map(str, df[ColumnName.CODE.value]))
        self.target = torch.tensor(df.iloc[:, 1:].astype(float).values)
        self.code_encoded = tokenizer(
            code, padding=True, truncation=True, max_length=context_length, return_tensors="pt",
        )[DatasetColumnArgument.INPUT_IDS.value]

    def __getitem__(self, idx):
        return {DatasetColumnArgument.INPUT_IDS.value: self.code_encoded[idx],
                DatasetColumnArgument.LABELS.value: self.target[idx]}

    def __len__(self):
        return len(self.target)
