# Searching code quality errors in the task templates

This module allows running the algorithm of searching code quality errors in the task templates and analyze its result.

## Searching algorithm

The algorithm pipeline is the following: 

![The general pipeline of the algorithm for detecting code quality errors in pre-written templates.](./images/algorithm_pipeline.png "The general pipeline of the algorithm for detecting code quality errors in pre-written templates.")

The output file contains the following columns:

### Usage

Run the [search.py](search.py) script with the arguments from command line.

Required arguments:

`submissions_path` — Path to .csv file with submissions. The file must contain the following columns: `id`, `step_id`, `code`, `group`, `attempt`, `raw_issues`.
`steps_path` — Path to .csv file with steps. The file must contain the following columns: `id`, `code_templates`.
`result_path` — Path to resulting .csv file with issues ranking.

Optional arguments:

Argument | Description
--- | ---
|**steps_with_groups_count**| Path to new .csv file with steps and counted number of groups. The resulted file will be equal to the initial `steps_path`, but with an additional column `groups_cnt`. The default value is `None`, it means the initial file `steps_path` will be rewritten.|
|**&#8209;N** | Number of top issues for every step. The default value is `50`.|
|**&#8209;equal** | Function for lines comparing. Possible functions: `char_by_char`, `edit_distance`. The default value is `char_by_char`.|
