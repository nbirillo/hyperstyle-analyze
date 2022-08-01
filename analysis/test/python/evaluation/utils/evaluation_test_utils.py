from pathlib import Path
from typing import Any, Callable, List, TypeVar

import pandas as pd

from analysis.src.python.evaluation.utils.evaluation_utils import EvaluationConfig
from analysis.src.python.utils.df_utils import equal_df, read_df

C = TypeVar('C', bound=EvaluationConfig)


def run_evaluation_test(input_path: Path,
                        output_path: Path,
                        config: EvaluationConfig,
                        evaluate: Callable[[pd.DataFrame, C], pd.DataFrame]):
    """ Run evaluation on dataframe from `input_path` and compare its output with expected from `output_path`. """
    in_df = read_df(input_path)
    inspected_df = evaluate(in_df, config)
    out_df = read_df(output_path)

    assert equal_df(inspected_df, out_df)


def run_evaluation_parsing_test(
        result_path: Path,
        parse_result: Callable[[Path], pd.DataFrame],
        get_result_issues: Callable[[pd.Series], List[Any]],
        result_shape: int,
        result_row_shapes: List[int]
):
    """ Parse evaluation results and compare its shapes with expected `result_shape` and `result_content_shape`. """
    df_result = parse_result(result_path)
    assert df_result.shape[0] == result_shape
    for i, result_row in df_result.iterrows():
        issues = get_result_issues(result_row)
        assert len(issues) == result_row_shapes[i]
