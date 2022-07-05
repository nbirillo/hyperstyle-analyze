from enum import Enum, unique


@unique
class ColumnName(Enum):
    CODE = 'code'
    LANG = 'lang'
    LANGUAGE = 'language'
    GRADE = 'grade'
    ID = 'id'
    COLUMN = 'column'
    ROW = 'row'
    OLD = 'old'
    NEW = 'new'
    IS_PUBLIC = 'is_public'
    DECREASED_GRADE = 'decreased_grade'
    PENALTY = 'penalty'
    USER = 'user'
    HISTORY = 'history'
    TIME = 'time'
    TRACEBACK = 'traceback'
    EXTRACTED_ISSUES = 'extracted_issues'
