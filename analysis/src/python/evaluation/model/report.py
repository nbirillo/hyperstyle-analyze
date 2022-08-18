from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class BaseIssue:

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_line_number(self) -> int:
        pass

    @abstractmethod
    def get_column_number(self) -> int:
        pass

    @abstractmethod
    def get_category(self) -> str:
        pass

    @abstractmethod
    def get_difficulty(self) -> str:
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
        pass
