# Code Quality Report And Issues

Here you can find the instruction how to use existing and support new code quality issues reports from various code quality analysis tools.

**Code quality report** usually contains overall stats about code quality of some piece of code and 
the list of **code quality issues** detected by some code quality analysis tool. 
You can find the examples of such reports for [hyperstyle](../hyperstyle/README.md) and [qodana](../qodana/README.md) tools by following links.

## Json support
Usually report is provided as json file. To parse json easily we use two libraries:
* [dataclasses](https://pypi.org/project/dataclasses/) library which provides a simple API for encoding and decoding dataclasses to and from dict.
    With this annotation class will have two extra methods `.to_dict()` and `.from_dict()` for encoding and decoding respectively.
* [dataclass_json](https://pypi.org/project/dataclasses-json/0.0.12/) library which provides a simple API for encoding and decoding dataclasses to and from JSON.
    With this annotation class will have two extra methods `.to_json()` and `.from_json()` for encoding and decoding respectively.

## Code Quality Issue And Report Model
Each code quality report and issue should implement `BaseReport` and `BaseIssue` classes from [report.py](report.py).

### BaseIssue implementation

`BaseIssue` is an interface that every custom issue should implement.
Further you can see main facts that you should know to implement your own `BaseIssue` inheritor or use existing:

* `BaseIssue` class has @dataclass(frozen=True) and @dataclass_json annotation. 
So the inheritor `MyIssue` should put this annotations too to be serializable.

```python
@dataclass_json
@dataclass(frozen=True)
class BaseIssue:

@dataclass_json
@dataclass(frozen=True) # Can not be modified
class MyIssue(BaseIssue): # Inheritor class declaration
```   

* Being an issue, `BaseIssue` should provide information about issue (like name, line and column number). 
So the inheritor `MyIssue` should implement several `getters` which are defined in `BaseIssue` interface:

```python
@abstractmethod
def get_name(self) -> str: # Interface method in BaseIssue class
    pass

@abstractmethod
def get_name(self) -> str: # Interface method implication in MyIssue class
    return self.name
```

```python
@abstractmethod
def get_line_number(self) -> int: # Interface method in BaseIssue class
    pass

@abstractmethod
def get_line_number(self) -> int: # Interface method implication in MyIssue class
    return self.line_no
``` 

### BaseReport implementation

`BaseReport` is an abstract class that every custom report should implement.
Further you can see main facts that you should know to implement your own `BaseReport` inheritor or use existing:

* `BaseReport` class has @dataclass(frozen=True) and @dataclass_json annotation. 
So the inheritor `MyReport` should put this annotations too.

```python
@dataclass_json
@dataclass(frozen=True)
class BaseReport:

@dataclass_json
@dataclass(frozen=True) # Can not be modified
class MyReport(BaseReport): # Inheritor class declaration
```   

* `MyReport` class will has extra methods for encoding and decoding from JSON:

To create `MyReport` instance from json string use:
```python
report = MyReport.from_json(str_report)
```
To dump `MyReport` instance to json string use:
```python 
str_report = report.to_json()
```

* Being a report, `BaseReport` should provide and ability to get and filter issues. 
For this `BaseReport` class has two abstract methods which have to be defined in `MyReport`:

Should provide list of issues from report:
```python
@abstractmethod
def get_issues(self) -> List[BaseIssue]:
    pass
```

Should leave issues in report which satisfy given `predicate` and return filtered copy:
```python
@abstractmethod
def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'BaseReport':
    pass
```
