import os
import sys
from pathlib import Path

MAIN_FOLDER = Path(__file__)
HYPERSTYLE_PATH = f'{MAIN_FOLDER.parent.parent}/main/venv/src'
sys.path.append(HYPERSTYLE_PATH)
if os.getenv('HYPERSTYLE_RUNNER_PATH') is not None:
    HYPERSTYLE_RUNNER_PATH = os.getenv('HYPERSTYLE_RUNNER_PATH')
    print(f'HYPERSTYLE_RUNNER_PATH ENV: {HYPERSTYLE_RUNNER_PATH}')
else:
    HYPERSTYLE_RUNNER_PATH = Path(HYPERSTYLE_PATH) / 'hyperstyle/src/python/review/run_tool.py'
    print(f'HYPERSTYLE_RUNNER_PATH: {HYPERSTYLE_RUNNER_PATH}')
