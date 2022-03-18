# Data preprocessing

This module transforms filtered and labeled dataset into the files that can be used as input
files for [train](src/python/evaluation/qodana/imitation_model/train.py) and 
[evaluation](src/python/evaluation/qodana/imitation_model/evaluation.py) scripts. 

### Step 1

Run the [code_issues_to_ids.py](code_issues_to_ids.py) with the arguments from command line.

Required arguments:

| Argument                  | Description                                              |
|---------------------------|----------------------------------------------------------|
| `submissions_path`        | Path to csv-file with code samples and issues.           |
| `issues_path`             | Path to csv-file with code samples and issues.           |
| `mapped_submissions_path` | Path to csv-file with code and maped to ids inspectios.  |
| `mapped_issues_path`      | Path to csv-file with issue class and id relation.       |

Optional arguments:

| Argument                                | Description                          |
|-----------------------------------------|--------------------------------------|
| **&#8209;&#8209;remove&#8209;by-lines** | Map issues by each line separately   |
| **&#8209;&#8209;remove&#8209;unique**   | Delete duplicates by code and issues |

The resulting file will be stored in the same folder as the input file.

An example of the input file:

```json 
| id   |  code             |  lang         | inspections                                                                                                                   |
|------|-------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|
| 2    |  "// some code"   |  java11       | "{""issues"": []}"                                                                                                   |
| 3    |  "// some code"   |  java11       | "{""issues"": [""{\"... \""problem_id\"": \""SystemOutErr\""}""]}"                                                            |
| 0    |  "// some code"   |  java11       | "{""issues"": [""{\"...\""problem_id\"": \""ConstantExpression\""}"",""{\"...\""problem_id\"": \""ConstantExpression\""}""]}" |
| 1    |  "// some code"   |  java11       | "{""issues"": []}"                                                                                                            |
```  

with the inspections file: 

```json
id   |  inspection_id    
-----|-------------------
1    |  SystemOutErr   
2    |  ConstantExpression
```

An example of the output file with by code block issues mapping:

```json
id   |  code             |  lang         |  inspections
-----|-------------------|---------------|-----------------
2    |  "// some code"   |  java11       |  0
3    |  "// some code"   |  java11       |  1
0    |  "// some code"   |  java11       |  2,2
1    |  "// some code"   |  java11       |  0

```

An example of the output file with by code line issues mapping:

```json
id   |  code                                  |  lang         |  inspections
-----|----------------------------------------|---------------|-----------------
2    |  "// first line from code with id 2"   |  java11       |  0
2    |  "// second line from code with id 2"  |  java11       |  0
3    |  "// first line from code with id 3"   |  java11       |  1
3    |  "// second line from code with id 3"  |  java11       |  0
0    |  "// first line from code with id 0"   |  java11       |  0
0    |  "// second line from code with id 0"  |  java11       |  2,2
1    |  "// first line from code with id 1"   |  java11       |  0
1    |  "// second line from code with id 1"  |  java11       |  0

```

### Step 2

Run [encode_data.py](https://github.com/hyperskill/hyperstyle/blob/roberta-model/src/python/model/preprocessing/encode_data.py) with the
following arguments:

Required arguments:

| Argument              | Description                                        |
|-----------------------|----------------------------------------------------|
| `dataset_path`        | Path to the code issue relation file               |
| `target_dataset_path` | Path to the code with encoded issues relation file |

Optional arguments:

| Argument                                           | Description                                                                                                                                                                                                                       |
|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;ohe**, **&#8209;&#8209;one-hot-encoding** | If `True` target column will be represented as one-hot-encoded vector. The length of each vector is equal to the unique number of classes in dataset. Default is `True`.                                                          |
| **&#8209;c**, **&#8209;&#8209;add-context**        | Should be used only when `dataset_path` is a path to `numbered_ids_line_by_line.csv`. If set to `True` each single line will be substituted by a piece of code – the context created from several lines. Default is `False`.      |
| **&#8209;n**, **&#8209;&#8209;n-lines-to0add**     | A number of lines to append to the target line before and after it. A line is appended only if it matches the same solution. If there are not enough lines in the solution, special token will be appended instead. Default is 2. |


#### Script functionality overview: 
- creates `one-hot-encoding` vectors matches each samples each sample in the dataset **(default)**.
- substitutes `NaN` values in the dataset by `\n` symbol **(default)**.
- transform lines of code into the `context` from several lines of code **(optional)**.



### Step 3

Run [tf_idf.py](code_tf_idf.py) or [code_to_vec.py](code_to_vec.py)  with the following arguments:

Required arguments:

| Argument            | Description                                 |
|---------------------|---------------------------------------------|
| `dataset_path`      | Path to the code issue relation file        |
| `code_dataset_path` | Path to the code as features representation |

Optional arguments:

| Argument                                       | Description                                                                                                                                                                                                                       |
|------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;ohe**, **&#8209;&#8209;n-features**   | Number of features to select for code representation                                                                                                                                                                              |

#### Script functionality overview: 
- creates `one-hot-encoding` vectors matches each samples each sample in the dataset **(default)**.
- substitutes `NaN` values in the dataset by `\n` symbol **(default)**.
- transform lines of code into the `context` from several lines of code **(optional)**.

### Step 4

Run [split_dataset.py](https://github.com/hyperskill/hyperstyle/blob/roberta-model/src/python/model/preprocessing/split_dataset.py)
with the following arguments:

Required arguments:

| Argument            | Description                                 |
|---------------------|---------------------------------------------|
| `dataset_path`      | Path to the code issue relation file        |
| `code_dataset_path` | Path to the code as features representation |

Optional arguments:

 Argument                                     | Description
----------------------------------------------| ---
| **&#8209;o**, **&#8209;&#8209;dataset_path** | Path to the directory where folders for train, test and validation datasets with the corresponding files will be created. If not set, folders will be created in the parent directory of `dataset_path`.|
| **&#8209;ts**, **&#8209;&#8209;test_size**   | Proportion of test dataset. Available values: 0 < n < 1. Default is 0.2.|
| **&#8209;vs**, **&#8209;&#8209;val_size**    | Proportion of validation dataset that will be taken from train dataset. Available values are: 0 < n < 1. Default is 0.3.|
| **&#8209;sh**, **&#8209;&#8209;shuffle**     | If `True` data will be shuffled before split. Default is `True`.|
