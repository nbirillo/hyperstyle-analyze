from pathlib import Path

import pytest
from hyperstyle.src.python.review.application_config import LanguageVersion
from analysis.src.python.evaluation.utils.pandas_utils import filter_df_by_language
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.src.python.utils.file_utils import get_name_from_path
from analysis.src.python.evaluation.utils.args_utils import get_in_and_out_list
from analysis.test.python.evaluation import INSPECTORS_DIR_PATH

RESOURCES_PATH = INSPECTORS_DIR_PATH / 'filter_by_language'

IN_FILE_TO_LANGUAGES = {
    'in_1.csv': set(LanguageVersion),
    'in_2.csv': set(),
    'in_3.csv': [LanguageVersion.PYTHON_3],
    'in_4.csv': [LanguageVersion.PYTHON_3, LanguageVersion.PYTHON_3],
    'in_5.csv': [LanguageVersion.PYTHON_3, LanguageVersion.JAVA_11],
}

IN_AND_OUT_FILES = get_in_and_out_list(RESOURCES_PATH)


@pytest.mark.parametrize(('in_file', 'out_file'), IN_AND_OUT_FILES)
def test(in_file: Path, out_file: Path):
    in_df = read_df(in_file)
    out_df = read_df(out_file)
    languages = IN_FILE_TO_LANGUAGES[get_name_from_path(in_file)]
    filtered_df = filter_df_by_language(in_df, languages)
    assert equal_df(out_df, filtered_df)
