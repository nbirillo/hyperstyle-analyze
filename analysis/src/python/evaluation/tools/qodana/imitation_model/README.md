# Qodana imitation model

# Dataset preparation

### 1. Qodana Evaluation

Run qodana tool on submissions dataset using [evaluate.py](analysis/src/python/evaluation/tools/qodana/evaluate.py) script. 
As the result you will get dataset where 
in column `qodana_issues` you can find list of qodana issues detected in each submission.

### 2. Qodana Issues List

Get list of all qodana issues from received dataset using [preprocess_issues.py](analysis/src/python/data_analysis/preprocessing/preprocess_issues.py) script. 
It will generate csv file with list of all unique (by name) qodana issues detected in all submissions.

### 3. Qodana Issues to IDs Mapping

Run [evaluate.py](analysis/src/python/evaluation/tools/qodana/evaluate.py) script. 
