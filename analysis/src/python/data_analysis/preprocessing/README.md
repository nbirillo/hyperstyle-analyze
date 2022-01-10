# Hyperskill data preprocessing

This module contains methods to preprocess and prepare data, collected from Hyperskill educational platform, 
for further analysis. 

To run data preprocessing, run following python scripts in stated order:

1. [build_submissions_with_issues.py](build_submissions_with_issues.py) - merges submissions with detected issues. 

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**raw_issues_path**| Path to .csv file with `raw issues` to submission relation. |
    |**qodana_issues_path**| Path to .csv file with qodana `issues` to submission relation. |
    |**submissions_with_issues_path**| Path to .csv output file with submissions with issues. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;users-to-submissions-path** | Path to file with `user` to submission relation (if data is not presented in submissions dataset or was anonymized). |


2. [build_submissions_series.py](build_submissions_series.py) - add information to submissions about submission's
   series (number of attempts, total number of attempts in series, series number). Submission series is the number of 
   attempts of one user to solve one step's problem.

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**submissions_series_path**| Path to .csv file with filtered submissions with series info. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;diff-ratio** | Ration to remove submissions which has lines change more than in `diff_ratio` times. |

3. [build_issues.py](build_issues.py) - collect information about issues, which are detected in all submissions. 
   Must be invoked twice (both for raw and qodana issues).
   
    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**issues_type**| Type of issues to analyse (can be raw or qodana). |
    |**issues_path**| Path to .csv file where issues info will be saved. |

4. [preprocess_steps.py](preprocess_steps.py) - add information about topic depth in knowledge tree.

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**topics_path**| Path to .csv file with topics info. |


5. [preprocess_topics.py](preprocess_topics.py) - add information about steps complexity, difficulty, 
   template and assignment features.

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**steps_path**| Path to .csv file with steps. |
    |**topics_path**| Path to .csv file with topics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;complexity-borders** | Topic depth to consider steps as shallow, middle or deep (default is 3 for shallow 7 for deep). |
    | **&#8209;&#8209;difficulty-borders** | Steps success rate to consider steps as easy, medium or hard (default is 1/3 for easy 2/3 for hard). |

6. [preprocess_users.py](preprocess_users.py) - add information about users level.

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**steps_path**| Path to .csv file with steps. |
    |**topics_path**| Path to .csv file with topics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;complexity-borders** | Topic depth to consider steps as shallow, middle or deep (default is 3 for shallow 7 for deep). |
    | **&#8209;&#8209;difficulty-borders** | Steps success rate to consider steps as easy, medium or hard (default is 1/3 for easy 2/3 for hard). |

7. [preprocess_submissions.py](preprocess_submissions.py) - add information about client, filter submissions with many 
   attempts, select subset of steps, topics, and users, mentioned in submissions dataset.

    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with submissions. |
    |**steps_path**| Path to .csv file with steps. |
    |**topics_path**| Path to .csv file with topics. |
    |**users_path**| Path to .csv file with users. |
    |**result_directory_path**| Path to directory with all preprocessed data for anasysis. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;max-attempts** | Maximum number of attempts to leave in dataset (submissions with many attempts considered as noise). |

After all preprocessing stages you will get directory with all preprocessed data, 
which can be used for further analysis.