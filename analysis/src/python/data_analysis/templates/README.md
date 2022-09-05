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
- `issues` with three csv files:
  - `template_issues.csv` with template issues (most important file)
  - `common_typical_issues.csv` with common typical issues
  - `rare_typical_issues.csv` with rare typical issues

Example for each csv:

| step_id  | origin_class       | frequency          | pos_in_template | task_link | description                                                                          |
|----------|--------------------|--------------------|-----------------|-----------|--------------------------------------------------------------------------------------|
| 2262     | UselessParentheses | 0.8195615514333895 | <null>          | LINK      | Useless parentheses.                                                                 |
| 5203     | IndentationCheck   | 0.6465067778936392 | 30, 33, 36      | LINK      | 'method def modifier' has incorrect indentation level 5, expected level should be 4. |

- `samples` with examples of submissions series with template issues occurrence in format
`<step_id>/<issue_class_name>/<group_id>/solution_<submission_id>/attempt_<attempt number>.<extension>`