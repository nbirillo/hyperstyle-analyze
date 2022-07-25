import logging
import time
from typing import List

from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_evaluation_command(command: List[str]):
    logger.info('Start evaluation')
    start = time.time()

    logger.info('Executing command: ' + (' '.join(command)))
    results = run_in_subprocess(command)

    end = time.time()
    logger.info(f'Finish evaluation time={end - start}s output={len(results)}')

    return results
