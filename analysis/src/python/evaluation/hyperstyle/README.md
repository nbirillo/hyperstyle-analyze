# Hyperstyle evaluation

This tool allows running the `Hyperstyle` tool on a `xlsx` or `csv` table to get code quality for all code fragments. 
Please, note that your input file should consist of at least 2 obligatory columns to run the tool on its code fragments:

- `code`
- `lang`

Possible values for column `lang` are: `python3`, `kotlin`, `java8`, `java11`.

Output file is a new `xlsx` or `csv` file with the all columns from the input file and one additional - `traceback` 
which contains full traceback of [hyperstyle](https://github.com/hyperskill/hyperstyle/blob/main/README.md)  code quality analysis tool.
For this evaluation you need to download ocker image `stepik/hyperstyle:1.2.2` (with preinstalled hyperstyle tool) 
or build your own docker container.
This evaluation fully represents solution code quality accessing in hyperskill platform.

## Usage

Run the [evaluate.py](evaluate.py) with the arguments from command line.

Required arguments:

`solutions_file_path` — path to xlsx-file or csv-file with code samples to inspect.

Optional arguments:

 Argument                                                              | Description                                                                                                                          
-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------
| **&#8209;tp**, **&#8209;&#8209;tool&#8209;path**                      | Path to docker (USER/NAME:VERSION) to run evaluation on. By default `stepik/hyperstyle:1.2.2` is used.                               |
| **&#8209;tp**, **&#8209;&#8209;tool&#8209;path**                      | Path to run-tool inside docker. Default is `review/hyperstyle/src/python/review/run_tool.py` .                                       |
| **&#8209;&#8209;output&#8209;allow&#8209;duplicates** | Allow duplicate issues found by different linters. By default, duplicates are skipped.                                               |
| **&#8209;&#8209;output&#8209;with&#8209;all&#8209;categories** | Without this flag, all issues will be categorized into 5 main categories: CODE_STYLE, BEST_PRACTICES, ERROR_PRONE, COMPLEXITY, INFO. |
