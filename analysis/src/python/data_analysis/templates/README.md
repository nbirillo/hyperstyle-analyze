# Searching code quality errors in the task templates

This module allows running the algorithm of searching code quality errors in the task templates and analyze its result.

## Searching algorithm

Firstly we need to indicate issues which remains in all submissions of concrete user for concrete step 
(which student do not during all attempts to pass step).

The algorithm pipeline is the following: 

![The general pipeline of the algorithm for detecting code quality errors in pre-written templates.](./images/algorithm_pipeline.png "The general pipeline of the algorithm for detecting code quality errors in pre-written templates.")

The output file contains the following columns:

### Usage

Run the [search.py](search.py) script with the arguments from command line.

Required arguments:

- `submissions_path` — Path to .csv file with submissions. The file must contain the following columns: `id`, `lang`, `step_id`, `code`, `group`, `attempt`, `hyperskill_issues`/`qodana_issues` (please, use [preprocess_submissions.py](../preprocessing/preprocess_submissions.py) script to get  `group` and `attempt` columns).
- `steps_path` — Path to .csv file with steps. The file must contain the following columns: `id`, and `code_template` OR `code_templates`.
- `repetitive_issues_path` — Path to resulting .csv file with repetitive issues.
- `issues_column` — Column name in .csv file with submissions where issues are stored (can be `hyperstyle_issues` ot `qodana_issues`).

Optional arguments:

| Argument                                                     | Description                                                                                                                         |
|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;ic**, **&#8209;&#8209;ignore-trailing-comments**    | Ignore trailing (in the end of line) comments while comparing two code lines.                                                       |
| **&#8209;iw**, **&#8209;&#8209;ignore-trailing-whitespaces** | Ignore trailing whitespaces while comparing two code lines.                                                                         |
| **&#8209;equal**                                             | Function for lines comparing. Possible functions: `edit_distance`, `edit_ratio`, `substring`. The default value is `edit_distance`. |


Example for output csv with repetitive issues:
  - `step_id` - id of step where repetitive issue found
  - `name` - issue name
  - `description` - the message about this issue which student see
  - `pos_in_template` - position of issue in template code (can be null if not detected)
  - `line` - example of line of code where repetitive issue is detected
  - `frequency` - % of submission series with such repetitive issue
  - `count` - number of submission series with such repetitive issue
  - `total_count` - number of all submission series for such step
  - `groups` - ids of submission series (groups) with such repetitive issue


| step_id | name                 | description                             | pos_in_template | line                                  | frequency  | count  | total_count             | groups            | 
|---------|----------------------|-----------------------------------------|-----------------|---------------------------------------|------------|--------|-------------------------|-------------------|
| 2262    | WhitespaceAfterCheck | "if' is not followed by whitespace ..." | <null>          | "\tif(x < y) {"                       | 0.09967585 | 123    | 1234                    | "[30, 33, 36]"    |
| 5203    | IndentationCheck     | "for' has incorrect indentation ..."    | 10              | "\t\t\t\tfor(int k = i; k > 0; k--){" | 0.80433251 | 4567   | 5678                    | "[130, 133, 136]" |


## Postprocessing

This script allows processing the results of the repetitive issues search algorithm to convert into more user-friendly format:

First, we apply basic issues filtering by frequency, because if a repetitive issue is found in a small percentage of submissions series,
it is most likely not an issue in the template and the students just don't want (or know how to) to fix it.
We have chosen 10% as such a threshold.
This threshold was chosen empirically.

If within the same task there are several same code quality issues, with different frequencies, but with the None position 
in the template, keep the most frequent of them.

The results of the algorithm are divided into several tables: 
- template errors (**Template** type, frequency of at least 51%)
- common typical errors (**Typical** type, frequency from 25% to 51%)
- rare typical errors (**Typical** type, frequency 10% to 25%)

Also, additional supporting information can be received:
- random student solutions containing a given issue in a given task
- all submissions group ids which given repetitive issue
- line of code with given issues
- issue description

### Usage

Run the [postprocessing.py](postprocess.py) script with the arguments from command line.

Required arguments:

- `repetitive_issues_path` — Path to .csv file with issues in templates, that can be calculated on the previous step (run search.py).
- `result_path` — Path to resulting folder with processed issues.
- `submissions_path` — Path to .csv file with submissions issues. By default, it is `None`. If this argument is not `None`, the resulting file will contain the `description` column for each task and the students solutions will be gathered.
- `issues_column` — Column name in .csv file with submissions where issues are stored (can be `hyperstyle_issues` ot `qodana_issues`).

Optional arguments:

| Argument                                                                 | Description                                                                                                                         |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;ft**, **&#8209;&#8209;freq-to-separate-template-issues**        | The threshold of frequency to separate template issues and keep them in the result table. The default value is `51`.                |
| **&#8209;fr**, **&#8209;&#8209;freq-to-remove**                          | The threshold of frequency to remove issues from the final table. The default value is `10`.                                        |
| **&#8209;fs**, **&#8209;&#8209;freq-to-separate-rare-and-common-issues** | The threshold of frequency to separate issues into typical issues to rare and common in the final table. The default value is `25`. |
| **&#8209;n**, **&#8209;&#8209;solutions-number**                         | Tne number of random students solutions that should be gathered for each task. The default value is `5`.                            |
| **&#8209;url**, **&#8209;&#8209;base-task-url**                          | Base url to the tasks on an education platform. The default value is `https://hyperskill.org/learn/step`.                           |

### Output format
Output directory will contain following directories:
1. `issues` with three csv files:
   - `template_issues.csv` with part of repetitive issues which a considered to be template issues (most important file)
   - `common_typical_issues.csv` with part of repetitive issues which a considered to be common typical students issues
   - `rare_typical_issues.csv` with part of repetitive issues which a considered to be rare typical students issues

2. `samples` with examples of submissions series with template issues occurrence in format
`<step_id>/<issue_class_name>/<group_id>/solution_<submission_id>/attempt_<attempt number>.<extension>`

## Filtering based on repetitive issues

After we have list of issue in template we can filter them from dataset to analyze only students code quality issues.
So the idea is to build matching for student code lines and template code lines and remove all issues 
from student code lines if corresponding template line contains template issue.

### Usage

Run the [filter.py](filter.py) script with the arguments from command line.

Required arguments:

- `templates_issues_path` — Path to .csv file with template issues (from [postprocess.py](postprocess.py) output).
- `submissions_path` — Path to .csv file with submissions. The file must contain the following columns: `id`, `lang`, `step_id`, `code`, `group`, `attempt`, `hyperskill_issues`/`qodana_issues` (please, use [preprocess_submissions.py](../preprocessing/preprocess_submissions.py) script to get  `group` and `attempt` columns).
- `steps_path` — Path to .csv file with steps. The file must contain the following columns: `id`, and `code_template` OR `code_templates`.
- `filtered_submissions_path` — Path to resulting .csv file with submissions with filtered issues.
- `issues_column` — Column name in .csv file with submissions where issues are stored (can be `hyperstyle_issues` ot `qodana_issues`).

Optional arguments:

| Argument                                                     | Description                                                                                                                         |
|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;ic**, **&#8209;&#8209;ignore-trailing-comments**    | Ignore trailing (in the end of line) comments while comparing two code lines.                                                       |
| **&#8209;iw**, **&#8209;&#8209;ignore-trailing-whitespaces** | Ignore trailing whitespaces while comparing two code lines.                                                                         |
| **&#8209;equal**                                             | Function for lines comparing. Possible functions: `edit_distance`, `edit_ratio`, `substring`. The default value is `edit_distance`. |

### Output format
Output csv file will be saved to `filtered_submissions_path` and will contain all data from csv in `submissions_path` but issues from `issues_column` will be modified in following way:
- `issues_column` will contain only students issues with filtered template issues
- `issues_column` + `_diff` will contain filtered template issues
- `issues_column` + `_all` will contain both students and template issues

## Filtering based on difference analysis of code from template and students code

The idea of this algorithm is to build diff between template and students code and consider issue as template if 
it places in code with zero difference from template.

We use [diff-match-patch](https://github.com/google/diff-match-patch) library to find diff between code. 
The example of input and output is following:

```python
template = "x = 1\ny = # your code here\nprint(x, y)"
code = "x = 1\ny = 2\nprint(x, y)"

dmp = diff_match_patch.diff_match_patch()
diff = dmp.diff_main(template, code)
# Result: [(0, "x = 1\ny = "), (-1, "# your code here"), (1, "2"), (0, "\nprint(x, y)")]
```
The result is array of pairs: tag (-1 - deletion, 0 - equal, 1 - addition) and the code substring.
So is issue position falls into code substring with tag 1 (new code added by student) it can be considered as student code issue,
otherwise if  with tag 0 (code is identical to template) it is considered as template issue. 
Deleted parts from template are not considered as they are not presented in code => no information about issues inside them.

As the position of issue is defined as line number + column number, we need to recalculate them considering code as single line test:
```python
x = int(input())
if x == 5:
    print('hello') # MagicNumber line_number=3 column_number=9
```

```python
code = "x = int(input())\nif x == 5:\n\tprint('hello')" # MagicNumber offset=27
```

### Usage

Run the [filter_using_diff.py](filter_using_diff.py) script with the arguments from command line.

Required arguments:

- `submissions_path` — Path to .csv file with submissions. The file must contain the following columns: `id`, `lang`, `step_id`, `code`, `group`, `attempt`, `hyperskill_issues`/`qodana_issues` (please, use [preprocess_submissions.py](../preprocessing/preprocess_submissions.py) script to get  `group` and `attempt` columns).
- `steps_path` — Path to .csv file with steps. The file must contain the following columns: `id`, and `code_template` OR `code_templates`.
- `filtered_submissions_path` — Path to resulting .csv file with submissions with filtered issues.
- `template_issues_path` - Path .csv file with template issues with their positions.
- `issues_column` — Column name in .csv file with submissions where issues are stored (can be `hyperstyle_issues` ot `qodana_issues`).

### Output format
Output csv file will be saved to `filtered_submissions_path` and will contain all data from csv in `submissions_path` but issues from `issues_column` will be modified in following way:
- `issues_column` will contain only students issues with filtered template issues
- `issues_column` + `_diff` will contain filtered template issues
- `issues_column` + `_all` will contain both students and template issues
