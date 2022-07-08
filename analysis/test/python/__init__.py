import sys
from pathlib import Path

from analysis import HYPERSTYLE_PATH

sys.path.append(HYPERSTYLE_PATH)

TEST_DATA_FOLDER = Path(__file__).parent.parent / 'resources'
