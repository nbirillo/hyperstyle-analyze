![Python build](https://github.com/hyperskill/hyperstyle/workflows/Python%20build/badge.svg?branch=develop)

# Hyperstyle analysis

A set of analysis utilities for the [Hyperstyle](https://github.com/hyperskill/hyperstyle) tool.
  
---

## Installation

Simply clone the repository and run the following commands:

1`pip install -r requirements.txt`
2`pip install -r requirements-test.txt` for tests
3`pip install -r requirements-roberta.txt` for roberta model

**Note**: you should set up the set of environment variables to `Hyperstyle` work correctly.
Please, follow the [Dockerfile](https://github.com/hyperskill/hyperstyle/blob/bf3c6e2dc42290ad27f2d30ce42d84a53241544b/Dockerfile#L14-L40) 
from the `Hyperstyle` repository.
To check the environment is set up correctly you can output the variables in the terminal, e.g.
```bash
echo $DETEKT_DIRECTORY && echo $DETEKT_VERSION
```
They should not be empty.

## Usage

**TODO**

---

## Tests running

We use [`pytest`](https://docs.pytest.org/en/latest/contents.html) library for tests.

Use `pytest` from the root directory to run __ALL__ tests.

