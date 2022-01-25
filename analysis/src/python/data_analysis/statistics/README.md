# Hyperskill data statistics

This module contains methods to calculate statistics on preprocessed data. 

To get statistics on collected and preprocessed data, run following python scripts in stated order:

1. [submissions_metrics_statistics.py](submissions_metrics_statistics.py) - calculate simple submissions' metrics 
   (e.x. code lines, symbols, number of issues). 

    **Required arguments:**

    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `preprocessed submissions`. |
    |**submissions_statistics_path**| Path to .csv file where to save submissions statistics. |

2. [client_statistics.py](client_statistics.py) - build .csv file with submissions series client
   for clients change statistics analysis.
   
    **Required arguments:**
    
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with `preprocessed submissions`. |
    |**client_statistics_path**| Path to .csv file where to save submissions client series statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submission groups which will be processed simultaneously. |

3. [issues_statistics.py](issues_statistics.py) - for each submission calculate number of 
   detected issues of each class.

    **Required arguments:**

    | Argument | Description |
    |----------|-------------|
    |**issues_type**| Type of issue to analyse (can be `raw_issue` or `qodana_issue`). |
    |**submissions_path**| Path to .csv file with `preprocessed submissions`. |
    |**issues_info_path**| Path to .csv file with all issues list (classes and types). |
    |**issues_statistics_path**| Path to .csv file where to save submissions issues statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submissions which will be processed simultaneously. |


4. [issues_change_statistics.py](issues_change_statistics.py) - for each submission calculate 
   diff of number of detected issues of each class. Need for issues fixing patters analysis.
   
    **Required arguments:**

    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with preprocessed submissions with series. |
    |**issues_statistics_path**| Path to .csv file with submissions issues statistics. |
    |**issues_path**| Path to .csv file with all issues list (classes and types). |
    |**issues_change_statistics_path**| Path to .csv file where to save submissions issues change statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;chunk-size** | Number of submission groups which will be processed simultaneously. |

4. [issues_steps_statistics.py](issues_steps_statistics.py) - for each issue type get rating of steps
   by number of its detections.
   
    **Required arguments:**
   
    | Argument | Description |
    |----------|-------------|
    |**submissions_path**| Path to .csv file with preprocessed submissions with series. |
    |**issues_statistics_path**| Path to .csv file with submissions issues statistics. |
    |**issues_info_path**| Path to .csv file with all issues list (classes and types). |
    |**issues_steps_statistics_directory_path**| Path to directory where to save issues steps statistics. |

    **Optional arguments:**
    
    | Argument | Description |
    |----------|-------------|
    | **&#8209;&#8209;attempt-number** | Number of attempt to analyze (None --all, 1 -- first, -1 --last, and other). |


After all preprocessing stages you will get some .scv files which you need for feather analysis.