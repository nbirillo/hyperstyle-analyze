# Hyperskill data search

This module contains methods to search relevant data in submissions data (e.x. submissions with specific code quality issue). 

1. [search_submissions.py](search_submissions.py) - search submissions which contains specific issues. This is helpful for manual submissions analysis and comparing submission with and without issues to find triggers.

   **Required arguments:**
   
   | Argument             | Description                                                                                                                    | 
   |--------------------------------------------------------------------------------------------------------------------------------|---|
   | **submissions_path** | Path to .csv file with `preprocessed submissions` (to get this data run scripts in [preprocessing](../preprocessing) module).  |
   | **output_path**      | Path to .csv file where to save detected submissions with issues.                                                              |
   | **issues_type**      | Type of issue to analyse (can be `raw_issues` or `qodana_issues`).                                                             |

    **Optional arguments:**

    | Argument | Description                                                                                                      |
    |---|-------------|
    | **&#8209;&#8209;issue** | Issue to find submissions examples with.                                                                         |
    | **&#8209;&#8209;step** | Step id to find submissions examples for.                                                                        |
    | **&#8209;&#8209;steps-issues-path** | If there are several pairs of (step, issues) to serach they can be put into .scv with step_id and issue columns. |
    | **&#8209;&#8209;count** | Number of submission with and without issue to serach.                                                           |

