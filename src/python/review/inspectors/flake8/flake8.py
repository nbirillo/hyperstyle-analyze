import logging
import re
from pathlib import Path
from typing import List

from src.python.review.common.subprocess_runner import run_in_subprocess
from src.python.review.inspectors.base_inspector import BaseInspector
from src.python.review.inspectors.common import convert_percentage_of_value_to_lack_of_value
from src.python.review.inspectors.flake8.issue_types import CODE_PREFIX_TO_ISSUE_TYPE, CODE_TO_ISSUE_TYPE
from src.python.review.inspectors.inspector_type import InspectorType
from src.python.review.inspectors.issue import (
    BaseIssue,
    CodeIssue,
    CohesionIssue,
    CyclomaticComplexityIssue,
    IssueData,
    IssueType,
)
from src.python.review.inspectors.tips import get_cyclomatic_complexity_tip

logger = logging.getLogger(__name__)

PATH_FLAKE8_CONFIG = Path(__file__).parent / '.flake8'
FORMAT = '%(path)s:%(row)d:%(col)d:%(code)s:%(text)s'
INSPECTOR_NAME = 'flake8'


class Flake8Inspector(BaseInspector):
    inspector_type = InspectorType.FLAKE8

    @classmethod
    def inspect(cls, path: Path, config: dict) -> List[BaseIssue]:
        command = [
            'flake8',
            f'--format={FORMAT}',
            f'--config={PATH_FLAKE8_CONFIG}',
            '--max-complexity', '0',
            '--cohesion-below', '100',
            path,
        ]
        output = run_in_subprocess(command)
        return cls.parse(output)

    @classmethod
    def parse(cls, output: str) -> List[BaseIssue]:
        row_re = re.compile(r'^(.*):(\d+):(\d+):([A-Z]+\d{3}):(.*)$', re.M)
        cc_description_re = re.compile(r"'(.+)' is too complex \((\d+)\)")
        cohesion_description_re = re.compile(r"class has low \((\d*\.?\d*)%\) cohesion")

        issues: List[BaseIssue] = []
        for groups in row_re.findall(output):
            description = groups[4]
            origin_class = groups[3]
            cc_match = cc_description_re.match(description)
            cohesion_match = cohesion_description_re.match(description)
            file_path = Path(groups[0])
            line_no = int(groups[1])

            column_number = int(groups[2]) if int(groups[2]) > 0 else 1
            issue_data = IssueData.get_base_issue_data_dict(file_path,
                                                            cls.inspector_type,
                                                            line_number=line_no,
                                                            column_number=column_number,
                                                            origin_class=origin_class)
            if cc_match is not None:  # mccabe: cyclomatic complexity
                issue_data[IssueData.DESCRIPTION.value] = get_cyclomatic_complexity_tip()
                issue_data[IssueData.CYCLOMATIC_COMPLEXITY.value] = int(cc_match.groups()[1])
                issue_data[IssueData.ISSUE_TYPE.value] = IssueType.CYCLOMATIC_COMPLEXITY
                issues.append(CyclomaticComplexityIssue(**issue_data))
            elif cohesion_match is not None:  # flake8-cohesion
                issue_data[IssueData.DESCRIPTION.value] = description  # TODO: Add tip
                issue_data[IssueData.COHESION_LACK.value] = convert_percentage_of_value_to_lack_of_value(
                    float(cohesion_match.group(1)),
                )
                issue_data[IssueData.ISSUE_TYPE.value] = IssueType.COHESION
                issues.append(CohesionIssue(**issue_data))
            else:
                issue_type = cls.choose_issue_type(origin_class)
                issue_data[IssueData.ISSUE_TYPE.value] = issue_type
                issue_data[IssueData.DESCRIPTION.value] = description
                issues.append(CodeIssue(**issue_data))

        return issues

    @staticmethod
    def choose_issue_type(code: str) -> IssueType:
        # Handling individual codes
        if code in CODE_TO_ISSUE_TYPE:
            return CODE_TO_ISSUE_TYPE[code]

        regex_match = re.match(r'^([A-Z]+)(\d)\d*$', code, re.IGNORECASE)
        code_prefix = regex_match.group(1)
        first_code_number = regex_match.group(2)

        # Handling other issues
        issue_type = (CODE_PREFIX_TO_ISSUE_TYPE.get(code_prefix + first_code_number)
                      or CODE_PREFIX_TO_ISSUE_TYPE.get(code_prefix))
        if not issue_type:
            logger.warning(f'flake8: {code} - unknown error code')
            return IssueType.BEST_PRACTICES

        return issue_type