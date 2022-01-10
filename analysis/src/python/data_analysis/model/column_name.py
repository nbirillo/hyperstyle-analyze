from enum import Enum, unique


@unique
class StepColumns(str, Enum):
    ID = 'id'
    COMMENTS = 'comments_statistics'
    LIKES = 'likes_statistics'
    STEPIC_LESSON_ID = 'lesson_stepik_id'
    POSITION = 'position'
    SECONDS_TO_COMPLETE = 'seconds_to_complete'
    SOLVED_BY = 'solved_by'
    STAGE = 'stage'
    STEPIK_ID = 'stepik_id'
    SUCCESS_RATE = 'success_rate'
    TOPIC = 'topic'
    TOPIC_THEORY = 'topic_theory'
    TYPE = 'type'
    TITLE = 'title'
    POPULAR_IDE = 'popular_ide'
    PROJECT = 'project'
    IS_IDE_COMPATIBLE = 'is_ide_compatible'
    OPTIONS = 'options'
    DEPTH = 'depth'

    BLOCK = 'block'
    TEXT = 'text'

    HEADER_LINES_COUNT = 'code_templates_header_lines_count'
    FOOTER_LINES_COUNT = 'code_templates_footer_lines_count'
    HAS_TEMPLATE = 'has_template'
    HAS_CONSTANT = 'has_constant'

    COMPLEXITY = 'complexity'
    DIFFICULTY = 'difficulty'


@unique
class Complexity(Enum):
    SHALLOW = 'shallow'
    MIDDLE = 'middle'
    DEEP = 'deep'


@unique
class Difficulty(Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


@unique
class TopicColumns(str, Enum):
    ID = 'id'
    CHILDREN = 'children'
    DEPTH = 'depth'
    HIERARCHY = 'hierarchy'
    PREREQUISITES = 'prerequisites'
    ROOT_ID = 'root_id'
    TITLE = 'title'
    TOPOLOGICAL_INDEX = 'topological_index'
    THEORY = 'theory'
    PARENT_ID = 'parent_id'


@unique
class SubmissionColumns(str, Enum):
    ID = 'id'
    USER_ID = 'user_id'
    GROUP = 'group'
    ATTEMPT = 'attempt'
    LAST_ATTEMPT = 'last_attempt'
    BASE_CLIENT = 'base_client'
    CLIENT = 'client'
    STEP_ID = 'step_id'
    CODE = 'code'
    LANG = 'lang'
    TIME = 'time'
    CODE_STYLE = 'code_style'
    # issues
    RAW_ISSUES = 'raw_issues'
    RAW_ISSUE_CLASS = 'origin_class'
    ISSUE_TYPE = 'type'
    QODANA_ISSUES = 'qodana_issues'
    QODANA_ISSUE_CLASS = 'problem_id'

    STATUS = 'status'


@unique
class SubmissionColumnsStats(str, Enum):
    ATTEMPTS = 'attempts'
    RAW_ISSUE_COUNT = 'raw_issues_count'
    QODANA_ISSUE_COUNT = 'qodana_issues_count'
    CODE_ROWS_COUNT = 'code_rows_count'
    CODE_SYMBOLS_COUNT = 'code_symbols_count'

    FIRST_SUFFIX = '_first'
    LAST_SUFFIX = '_last'


@unique
class IssuesColumns(str, Enum):
    CLASS = 'class'
    TYPE = 'type'


@unique
class Client(str, Enum):
    WEB = 'web'
    IDEA = 'idea'


@unique
class UserColumns(str, Enum):
    ID = 'id'
    COMMENTS = 'comments_posted'
    GAMIFICATION = 'gamification'
    LEVEL = 'level'
    # gamification
    ACTIVE_DAYS = 'active_days'
    DAILY_STEP_COMPLETED_COUNT = 'daily_step_completed_count'
    PASSED_PROBLEMS = 'passed_problems'
    PASSED_PROJECTS = 'passed_projects'
    PASSED_TOPICS = 'passed_topics'
    # comments
    COMMENT = 'comment'
    HINT = 'hint'
    USEFUL_LINK = 'useful_link'
    SOLUTIONS = 'solutions'


@unique
class Level(Enum):
    LOW = 'low'
    AVERAGE = 'average'
    HIGH = 'high'
