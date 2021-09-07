import csv
import os
from typing import List


class CsvWriter:

    def __init__(self, result_dir: str, csv_file: str, fieldnames: List[str]):
        os.makedirs(result_dir, exist_ok=True)
        self.csv_path = os.path.join(result_dir, csv_file)
        self.fieldnames = fieldnames

        with open(self.csv_path, 'w+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    def write_csv(self, data: dict):
        with open(self.csv_path, 'a+', newline='', encoding='utf8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow({k: data[k] for k in self.fieldnames})
