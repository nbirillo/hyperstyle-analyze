from dataclasses import asdict
from typing import List

from data.common_api.response import Object
from data.utils.csv import CsvWriter


def save_objects_to_csv(objects: List[Object], obj_class: str, obj_type):
    csv_writer = CsvWriter('result', f'{obj_class}s.csv', list(obj_type.__annotations__.keys()))
    for obj in objects:
        csv_writer.write_csv(asdict(obj))
