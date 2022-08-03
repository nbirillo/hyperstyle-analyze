# Benchmark

This module allows you to test the performance of Hyperstyle and Qodana.

## Usage

Run the [benchmark.py](benchmark.py) with the arguments from command line.

**Required arguments**:

- `submissions_path` — Path to .csv file with submissions.
- `output_path` — Path to .csv file where to save submissions with timings.
- `--analyzer` — Name of the analyzer that needs to be benchmarked. Possible values: `hyperstyle`, `qodana`.
- `--docker-path` — Path to docker (USER/NAME:VERSION) with the analyzer.

**Optional arguments**:

| Argument                            | Description                                                                                                                               |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;repeat**            | Times to repeat time evaluation for averaging. Default: 3.                                                                                |
| **&#8209;&#8209;aggregate**         | The function that will be used to aggregate the values from the different iterations. Possible values: `mean`, `median`. Default: `mean`. |
| **&#8209;&#8209;n&#8209;cpu**       | Number of cpu that can be used to run analyzer (only for Hyperstyle).                                                                     |
| **&#8209;&#8209;time&#8209;column** | Name of the column where the time will be saved. By default, the time will be saved in the `<analyzer_name>_time` column.                 |
| **&#8209;&#8209;tmp&#8209;dir**     | The path to the directory with the temporary files.                                                                                       |

