![Python build](https://github.com/hyperskill/hyperstyle/workflows/Python%20build/badge.svg?branch=develop)

# Hyperstyle analysis

A set of analysis utilities for the [Hyperstyle](https://github.com/hyperskill/hyperstyle) tool.
  
---

## Installation

Simply clone the repository and run the following commands:

1. `pip install -e git+https://github.com/hyperskill/hyperstyle.git@develop#egg=review`
2. `pip install -r requirements.txt`
3. `pip install -r requirements-test.txt` for tests
4. `pip install -r requirements-roberta.txt` for roberta model

## Usage

**TODO**

---

## Tests running

We use [`pytest`](https://docs.pytest.org/en/latest/contents.html) library for tests.

__Note__: If you have `ModuleNotFoundError` while you try to run tests, please call `pip install -e .`
 before using the test system.

Use `pytest` from the root directory to run __ALL__ tests.

