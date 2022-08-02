import pandas as pd

from analysis.src.python.data_analysis.utils.analysis_issue import AnalysisReport


def load_issues(df_submissions: pd.DataFrame, column: str, from_report: bool = False) -> pd.DataFrame:
    if from_report:
        df_submissions[column] = df_submissions[column].apply(AnalysisReport.from_json_report, column=column)
    else:
        df_submissions[column] = df_submissions[column].apply(AnalysisReport.from_json)
    return df_submissions


def dump_issues(df_submissions: pd.DataFrame, column: str) -> pd.DataFrame:
    df_submissions[column] = df_submissions[column].apply(AnalysisReport.to_json, axis=1)
    return df_submissions
