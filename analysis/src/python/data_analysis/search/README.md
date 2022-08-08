# Hyperskill data search

This module contains methods to search relevant data in submissions data (e.x. submissions with specific code quality issue). 

## Search submissions

[search_submissions.py](search_submissions.py) - search submissions which contains specific issues and save them to files. This is helpful for manual submissions analysis and comparing submission with and without issues to find triggers.

**Required arguments:**

| Argument             | Description                                                                                                                   | 
|----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **submissions_path** | Path to .csv file with `preprocessed submissions` (to get this data run scripts in [preprocessing](../preprocessing) module). |
| **output_path**      | Path to .csv file where to save detected submissions with issues.                                                             |
| **issues_column**    | Type of issue to analyse (can be `hyperstyle_issues` or `qodana_issues`).                                                     |

**Optional arguments:**

| Argument                            | Description                                                                                                      |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;issue-name**        | Issue to find submissions examples with.                                                                         |
| **&#8209;&#8209;step**              | Step id to find submissions examples for.                                                                        |
| **&#8209;&#8209;steps-issues-path** | If there are several pairs of (step, issues) to search they can be put into .scv with step_id and issue columns. |
| **&#8209;&#8209;count**             | Number of submission with and without issue to search.                                                           |
| **&#8209;&#8209;log-path**          | Path to directory where to create log file.                                                                      |



## Search submissions series

[search_submission_series.py](search_submission_series.py) - search submissions series with required number of total attempts and save them to files. Issues information added as comments.

**Required arguments:**

| Argument             | Description                                                                                                                   | 
|----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **submissions_path** | Path to .csv file with `preprocessed submissions` (to get this data run scripts in [preprocessing](../preprocessing) module). |
| **output_path**      | Path to .csv file where to save detected submissions with issues.                                                             |
| **issues_column**    | Type of issue to analyse (can be `hyperstyle_issues` or `qodana_issues`).                                                     |

 **Optional arguments:**


| Argument                            | Description                                                                                                      |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;total-attempts**    | Number if attempts to serach series with.                                                                        |
| **&#8209;&#8209;count**             | Number of submission series.                                                                                     |
| **&#8209;&#8209;steps-issues-path** | If there are several pairs of (step, issues) to serach they can be put into .scv with step_id and issue columns. |
| **&#8209;&#8209;log-path**          | Path to directory where to create log file.                                                                      |




## Search steps templates

[search_templates.py](search_templates.py) - search steps templates and save them to files. Issues information added as comments.

**Required arguments:**

| Argument             | Description                                                                                                                    | 
|----------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **submissions_path** | Path to .csv file with `preprocessed submissions` (to get this data run scripts in [preprocessing](../preprocessing) module).  |
| **output_path**      | Path to .csv file where to save detected submissions with issues.                                                              |
| **issues_column**    | Type of issue to analyse (can be `hyperstyle_issues` or `qodana_issues`).                                                      |

 **Optional arguments:**


| Argument                            | Description                                                                                                    |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;issue-name**        | Issue to find template examples with.                                                                          |
| **&#8209;&#8209;step**              | Step id to find template examples for.                                                                         |
| **&#8209;&#8209;log-path**          | Path to directory where to create log file.                                                                    |
