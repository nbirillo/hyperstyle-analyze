# Code Quality tools evaluation module

This module contains methods for various code quality tools evaluation on datasets with a lot of code samples.

## Implemented tools:

For now you perform large scale code quality evaluation using [hyperstyle](hyperstyle) and [qodana](qodana) tools.
As input files they are given a submissions dataset with columns:

* id - submission id
* code - submission code
* 