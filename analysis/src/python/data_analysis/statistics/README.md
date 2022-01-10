# Hyperskill data statistics

This module contains methods to calculate statistics on preprocessed data. 

To get statistics on collected and preprocessed data, run following python scripts in stated order:

1. [submissions_metrics_statistics.py](submissions_metrics_statistics.py) - calculate simple submissions' metrics 
   (e.x. code lines, symbols, number of issues). 

    **Required arguments:**

    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with preprocessed submissions with issues. |
    |**submissions_statistics_path**| Path to .csv file where to save submissions statistics. |

2. [submissions_client_statistics.py](submissions_client_statistics.py) - build .csv file with submissions series client
   for clients change statistics analysis.
   
    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**submissions_client_series_path**| Path to .csv file with submissions client series statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submission groups which will be processed simultaneously. |

3. [submissions_issues_statistics.py](submissions_issues_statistics.py) - for each submission calculate number of 
   detected issues of each class.

    **Required arguments:**

    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**issues_type**| Type of issue to analyse (can be `raw_issue` or `qodana_issue`). |
    |**issues_path**| Path to .csv file with all issues list (classes and types). |
    |**submissions_issues_statistics_path**| Path to .csv file with submissions issues statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submissions which will be processed simultaneously. |


4. [submissions_issues_change_statistics.py](submissions_issues_change_statistics.py) - for each submission calculate 
   diff of number of detected issues of each class. Need for issues fixing patters analysis.
   
    **Required arguments:**
   
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `submissions`. |
    |**issues_type**| Type of issue to analyse (can be `raw_issue` or `qodana_issue`). |
    |**issues_path**| Path to .csv file with all issues list (classes and types). |
    |**submissions_issues_statistics_path**| Path to .csv file with submissions issues statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submission groups which will be processed simultaneously. |


After all preprocessing stages you will get some .scv files which you need for feather analysis.