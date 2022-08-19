# Example for working with code quality reports and issues

## Example 1: Parse all issues in dataframe

```python
df = read_df(df_path)

df[SubmissionColumns.HYPERSTYLE_ISSUES.value] = \
    df.apply(parse_report, column=SubmissionColumns.HYPERSTYLE_ISSUES.value, axis=1)

df[SubmissionColumns.QODANA_ISSUES.value] = \
    df.apply(parse_report, column=SubmissionColumns.QODANA_ISSUES.value, axis=1)
```

## Example 2: Print all issue names from dataframe

```python

def print_issue_names(submission: pd.Series) -> None:
    report = parse_report(submission, SubmissionColumns.HYPERSTYLE_ISSUES.value)
    for issue in report.get_issues():
        print(issue.get_name())

df = read_df(df_path)
df.apply(print_issue_names, axis=1)
```

## Example 3: Filter some issues by name from dataframe

```python

def filter_issues(submission: pd.Series, ignore_issue_names: List[str]) -> str:
    report = parse_report(submission, SubmissionColumns.HYPERSTYLE_ISSUES.value)
    filtered_report = report.filter_issues(lambda issue: issue not in ignore_issue_names)
    return filtered_report.to_json()

df = read_df(df_path)
df[SubmissionColumns.HYPERSTYLE_ISSUES.value] = \
    df.apply(filter_issues, ignore_issue_names=['MagicNumberCheck'], axis=1)
```

```python

def filter_issues(str_report: str, ignore_issue_names: List[str]) -> str:
    report = parse_str_report(str_report, SubmissionColumns.HYPERSTYLE_ISSUES.value)
    filtered_report = report.filter_issues(lambda issue: issue not in ignore_issue_names)
    return filtered_report.to_json()

df = read_df(df_path)
df[SubmissionColumns.HYPERSTYLE_ISSUES.value] = \
    df[SubmissionColumns.HYPERSTYLE_ISSUES.value].apply(filter_issues, ignore_issue_names=['MagicNumberCheck'])
```