# Sample selection

This module will allow you to select several submission samples from certain groups.

## Usage

Run the [sample_selection.py](sample_selection.py) with the arguments from command line.

**Required arguments**:

- `submissions_path` — Path to .csv file with submissions.
- `output_path` — Path to .csv file where to save the samples.

**Optional arguments**:

| Argument                           | Description                                                                                       |
|------------------------------------|---------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;stats&#8209;path** | Path to .csv file with additional columns to be added. The merge will be done by the `id` column. |
| **&#8209;&#8209;config**           | Path to a config file. For more information, see [Config](#config) section.                       |

## Config

The config is a yaml file that must contain the name of the strategy 
by which the data must be grouped for further sample selection.

The strategy can have its own configuration arguments. The possible arguments for each strategy 
are described in the corresponding subsection of the [Strategies](#strategies) section.

There are also several **optional** arguments for all strategies:

| Argument              | Description                                                                                                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **number_of_samples** | Sets the number of samples in each group. If there are fewer samples than `number_of_samples` in a group, all elements from the group will be taken. The default value is `100`. |
| **random_seed**       | Sets a seed for the random generator.                                                                                                                                            |

### Example

```yaml
number_of_samples: 250
random_seed: 42

strategy_name:
  strategy_arg_1: "arg_value"
  strategy_arg_2: [ 0, 1, 1, 2, 3, 5, 8, 13 ]
```

## Strategies

There are several strategies for grouping data:

- `by_code_lines_count` — grouping is done by the `code_lines_count` column, where the code lines count is specified.
- `by_step_id` — grouping is done by the `step_id` column, where the step ID is specified.

### `by_code_lines_count` strategy config

There must be a `code_lines_count` column in the table.

A config must contain either the `count` value or the `bins` value.

`count` may be:

1) An integer number `step`.
   In this case only those code line counts which are multiples of `step` will be used for grouping.
   Also, if you want to include boundaries, you can do it with the optional `include_boundaries` flag. 
   By default, it is False.
2) An array of integers.
   In this case only those code line counts which are specified in the array will be used for grouping.

The `bins` must be an array of integers in which the boundaries of the bins will be specified.

#### Examples

```yaml
by_code_lines_count:
  step: 4
  include_boundaries: true
```

```yaml
by_code_lines_count:
  bins: [ 0, 10, 20, 30, 50, 100 ]
```

### `by_step_id` strategy config

There must be a `step_id` column in the table.

A config must contain the `ids` value. The `ids` is an array of integers by which the grouping will be done.

#### Example

```yaml
by_step_id:
  ids: [ 1, 42, 100, 101 ]
```
