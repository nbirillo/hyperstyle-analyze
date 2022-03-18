# Dataset labelling
This script allows you to label a dataset using the found [Qodana](https://github.com/JetBrains/Qodana) inspections.

The dataset must contain at least three columns: `id`, `code` and `lang`, where `id` is a unique solution number, `lang` is the language in which the code is written in the `code` column. The `lang` must belong to one of the following values: `java7`, `java8`, `java9`, `java11`, `python3`, `kotlin`. If `lang` is not equal to any of the values, the row will be skipped.

The dataset must have the format `csv`. The labeled dataset is also in `csv` format, with a new column `inspections` added, which contains a list of all found inspections.

# Usage
Run the [dataset_labeling.py](dataset_labeling.py) with the arguments from command line.

### Required arguments

`dataset_path` — path to dataset.

### Optional arguments

| Argument | Description |
|---|---|
| **&#8209;c**, **&#8209;&#8209;config** | Path to qodana.yaml. If the path is not specified, Qodana will start without a configuration file. |
| **&#8209;l**, **&#8209;&#8209;limit** | Allows you to read only the specified number of first rows from the dataset. If no limit is specified, the whole dataset will be processed. |
| **&#8209;s**, **&#8209;&#8209;chunk&#8209;size** | The number of files that Qodana will process at a time. Default is `5000`. |
| **&#8209;o**, **&#8209;&#8209;output&#8209;path** | The path where the labeled dataset will be saved. If not specified, the original dataset will be overwritten. |

---

# Preprocessing

The model that imitates Qodana analysis gets input from a dataset in a special format. 
This module allows preparing datasets that were graded by [dataset_labeling.py](dataset_labeling.py) script.

Data processing consists of several stages:
- union several `csv` files that were graded by [dataset_labeling.py](dataset_labeling.py) script 
  and filter inspections list if it is necessary;
- get all unique inspections from the dataset;
- convert `csv` file into a special format.

## Filter inspections

This stage allow you to union several `csv` files that were graded by [dataset_labeling.py](dataset_labeling.py) script 
  and filter inspections list if it is necessary.

Please, note that your all input files must be graded by [dataset_labeling.py](dataset_labeling.py) script 
and have `inspections` column.

Output file is a new `csv` file with the all columns from the input files.

#### Usage

Run the [filter_inspections.py](filter_inspections.py) with the arguments from command line.

Required arguments:

`dataset_folder` — path to a folder with csv files graded by Qodana. Each file must have `inspections` column.

Optional arguments:
Argument | Description
--- | ---
|**&#8209;i**, **&#8209;&#8209;inspections**| Set of inspections ids to exclude from the dataset separated by comma. By default all inspections remain. |

The resulting file will be stored in the `dataset_folder`.

___

## Get all unique inspections

This stage allow you to get all unique inspections from a `csv` file graded by Qodana. 
Please, note that your input file must be graded by [dataset_labeling.py](dataset_labeling.py) script 
and has `inspections` column.

Output file is a new `csv` file with four columns: `id`, `inspection_id`, `count_all`, `count_uniq`. 
`id` is unique number for each inspection, minimal value is 1.
`inspection_id` is unique Qoadana id for each inspection.
`count_all` count all fragments where was this inspection (with duplicates).
`count_uniq` count all fragments where was this inspection (without duplicates).

#### Usage

Run the [get_unique_inspectors.py](get_unique_inspectors.py) with the arguments from command line.

Required arguments:

`solutions_file_path` — path to csv-file with code samples graded by [dataset_labeling.py](dataset_labeling.py) script.

Optional arguments:

Argument | Description
--- | ---
|**&#8209;&#8209;uniq**| To count all fragments for each inspection where was this inspection (without duplicates). By default it disabled. |

The resulting file will be stored in the same folder as the input file.

An example of the output file:

```json
id   |  inspection_id      |  count_all   |  count_unique
-----|---------------------|--------------|--------------
1    |  SystemOutErr       |    5         |     2
2    |  ConstantExpression |    1         |     1
```

# Postprocessing

At this stage, you can convert the data received by the Qodana into the format of the Hyperstyle tool for 
analysis and statistics gathering.

## Convert Qodana inspections into Hyperstyle inspections

This stage allows you to convert the `inspections` column from `csv` marked by Qodana into 
`traceback` column with the Hyperstyle tool format.

This stage includes:
- keep only unique code fragments in both datasets (Qodana and Hyperstyle);
- keep only fragments in both datasets that have same ids and same code fragments;
- add a `grade` column into Qodana dataset corresponding to the `grade` column from Hyperstyle dataset;
- add a `traceback` column in the Hyperstyle format into Qodana dataset with inspection from the `inspections` column. 

Please, note that your Qodana input file must be graded by [dataset_labeling.py](dataset_labeling.py) script 
and have `inspections` column. Your Hyperstyle input file must be graded by [evaluation_run_tool.py](../evaluation_run_tool.py) script 
and have `traceback` and `grade` columns.

Output files is two new `csv` files.

#### Usage

Run the [convert_to_hyperstyle_inspections.py](convert_to_hyperstyle_inspections.py) with the arguments from command line.

Required arguments:

- `solutions_file_path_hyperstyle` — path to a `csv` file labelled by Hyperstyle;
- `solutions_file_path_qodana` — path to a `csv` file labelled by Qodana.

Optional arguments:
Argument | Description
--- | ---
|**&#8209;i**, **&#8209;&#8209;issues-to-keep**| Set of issues ids to keep in the dataset separated by comma. By default all issues are deleted. |

The Hyperstyle resulting file will be stored in the same folder with `solutions_file_path_hyperstyle`.
The Qodana resulting file will be stored in the same folder with `solutions_file_path_qodana`.

An example of the Qodana inspections before and after this processing:

1. Before:

```json
{
  "issues": [
    {
      "fragment_id": 0,
      "line": 8,
      "offset": 8,
      "length": 10,
      "highlighted_element": "System.out",
      "description": "Uses of <code>System.out</code> should probably be replaced with more robust logging #loc",
      "problem_id": "SystemOutErr"
    }
  ]
}
```

2. After:

```json
{
  "issues": [
    {
      "code": "SystemOutErr",
      "text": "Uses of <code>System.out</code> should probably be replaced with more robust logging #loc",
      "line": "",
      "line_number": 8,
      "column_number": 8,
      "category": "INFO",
      "influence_on_penalty": 0
    }
  ]
}
```
___
