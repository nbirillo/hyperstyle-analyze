import sys
from pathlib import Path

from src.python import MAIN_FOLDER

ANALYSIS_MAIN_FOLDER = Path(__file__)
HYPERSTYLE_PATH = f'{MAIN_FOLDER.parent.parent}/main/venv/src'
sys.path.append(HYPERSTYLE_PATH)
HYPERSTYLE_RUNNER_PATH = MAIN_FOLDER.parent / 'review/run_tool.py'
