import argparse
import logging
import os
from pathlib import Path

import torch
from transformers import RobertaForSequenceClassification

from analysis.src.python.evaluation.qodana.imitation_model.common.metric import Measurer
from analysis.src.python.evaluation.qodana.imitation_model.common.train_config import (MultilabelTrainer, TrainingArgs,
                                                                                       configure_arguments)
from analysis.src.python.evaluation.qodana.imitation_model.common.util import DatasetColumnArgument
from analysis.src.python.evaluation.qodana.imitation_model.dataset.dataset import QodanaDataset


def train_model(train_dataset_path: str,
                val_dataset_path: str,
                context_length: int,
                threshold: float,
                batch_size: int,
                val_step: int,
                args):
    train_dataset = QodanaDataset(train_dataset_path, context_length)
    val_dataset = QodanaDataset(val_dataset_path, context_length)

    train_steps_to_be_made = len(train_dataset) // batch_size
    val_steps_to_be_made = train_steps_to_be_made // val_step
    logging.info(f'Steps to be made: {train_steps_to_be_made}, '
                 f'validate each {val_steps_to_be_made}th step.')

    num_labels = train_dataset[0][DatasetColumnArgument.LABELS.value].shape[0]
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=num_labels).to(device)

    metrics = Measurer(threshold)

    train_args = TrainingArgs(args)

    trainer = MultilabelTrainer(model=model,
                                args=train_args.get_training_args(val_steps_to_be_made),
                                train_dataset=train_dataset,
                                eval_dataset=val_dataset,
                                compute_metrics=metrics.compute_metric)
    trainer.train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    if args.trained_weights_directory_path is None:
        args.trained_weights_directory_path = Path(args.train_dataset_path).parent / DatasetColumnArgument.WEIGHTS.value
        os.makedirs(args.trained_weights_directory_path, exist_ok=True)

    train_model(args.train_dataset_path,
                args.val_dataset_path,
                args.context_length,
                args.threshold,
                args.batch_size,
                args.val_step,
                args)
