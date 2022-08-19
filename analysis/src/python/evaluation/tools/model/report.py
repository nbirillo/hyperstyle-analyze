from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class BaseIssue:
    """ All code quality issues which a going to be analyzed should implement this abstract class. """

    @abstractmethod
    def get_name(self) -> str:
        """ Rerun issue name (e.x. MissingBreakInSwitch). """
        pass

    @abstractmethod
    def get_text(self) -> str:
        """ Rerun issue text description (e.x. Break in switch is missed). """
        pass

    @abstractmethod
    def get_line_number(self) -> int:
        """ Rerun line number where issue appeared (starting from 1). """
        pass

    @abstractmethod
    def get_column_number(self) -> int:
        """ Rerun column number where issue appeared (starting from 1). """
        pass

    @abstractmethod
    def get_category(self) -> str:
        """ Rerun issue category (e.x. ERROR_PRONE). """
        pass

    @abstractmethod
    def get_difficulty(self) -> str:
        """ Rerun issue difficulty (e.x. HARD). """
        pass

    def __eq__(self, other):
        return self.get_name() == other.get_name() and \
               self.get_text() == other.get_text() and \
               self.get_line_number() == other.get_line_number() and \
               self.get_column_number() == other.get_column_number() and \
               self.get_category() == other.get_category() and \
               self.get_difficulty() == other.get_difficulty()


@dataclass_json
@dataclass(frozen=True)
class BaseReport:
    """ All code quality reports which a going to be analyzed should implement this abstract class. """

    def has_issue(self, name: str):
        for issue in self.get_issues():
            if issue.get_name() == name:
                return True
        return False

    @abstractmethod
    def get_issues(self) -> List[BaseIssue]:
        pass

    @abstractmethod
    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'BaseReport':
        """ Leave issues in report which satisfy given `predicate`. """
        pass
