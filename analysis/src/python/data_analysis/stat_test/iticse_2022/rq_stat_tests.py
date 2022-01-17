import argparse
from typing import Set, Dict, Any, List
import pandas as pd
from pingouin import ttest
from statsmodels.stats import multitest

from data_analysis.utils.df_utils import read_df
from evaluation.common.pandas_util import filter_df_by_single_value

SEPARATOR = '######################################'
P_VALUE_COLUMN = 'p-val'
MAX_NUMBER_OF_ATTEMPTS = 5


def run_rq1(df: pd.DataFrame, issue_types: Set[str]):
    # RQ1: Which code quality issues are the most prevalent
    # in Java and in Python solutions?

    # H0: The task's complexity and code quality issue's type not influence
    # on the percentage of submissions with code quality issues
    # Note: consider H0 for each issues type from the set of them
    print(SEPARATOR)
    print(f'{SEPARATOR}RQ1{SEPARATOR}')
    print('H0: The task\'s complexity and code quality issue\'s type '
          'not influence on the percentage of submissions with code quality issues')
    for issue_type in issue_types:
        print(f'{SEPARATOR}ISSUE TYPE: {issue_type}{SEPARATOR}')
        print(df.anova(dv=issue_type, between='complexity', detailed=True))
    print(SEPARATOR)


def _bonferroni_correction(p_values: Dict[Any, Any]) -> List[str]:
    issue_column = 'issue'
    p_values_df = pd.DataFrame(p_values.items(), columns=[issue_column, P_VALUE_COLUMN])
    p_values_df[P_VALUE_COLUMN] = multitest.multipletests(p_values_df[P_VALUE_COLUMN], method='b')[1]
    p_values_df = p_values_df.loc[p_values_df[P_VALUE_COLUMN] < 0.001]
    return list(p_values_df[issue_column].unique())


def run_rq2(df: pd.DataFrame):
    # RQ2: How do the students fix various types of issues as they
    # update their solutions with further attempts?

    # H0: Over time, the number of code quality errors does not change
    print(SEPARATOR)
    print(f'{SEPARATOR}RQ2{SEPARATOR}')
    print('H0: The number of code quality issues does not decrease over time in submissions chains')
    for attempts_count in range(2, MAX_NUMBER_OF_ATTEMPTS + 1):
        print(f'{SEPARATOR}ATTEMPTS COUNT: {attempts_count}{SEPARATOR}')
        filtered_df = filter_df_by_single_value(df, 'total_attempts', attempts_count)
        print(filtered_df.rm_anova(dv='raw_issues_count', within='attempt', subject='group', detailed=True))
    print(SEPARATOR)


def run_rq3(df: pd.DataFrame, issue_types: Set[str]):
    # RQ3: How often do students use the web-based environment and the IDE,
    # and what differences are there between solutions written in them?

    # H0: Web redactor and IDE have the same number of line of the code in the solution
    print(SEPARATOR)
    print(f'{SEPARATOR}RQ3{SEPARATOR}')
    df_web = filter_df_by_single_value(df, 'client', 'web')
    df_ide = filter_df_by_single_value(df, 'client', 'idea')

    print('H0: Web redactor and IDE have the different number of line of the code in the solution')
    print(ttest(df_web['code_rows_count'], df_ide['code_rows_count'], alternative='less'))
    print(SEPARATOR)

    # H0: The client and code quality issue's type not influence
    # on the percentage of submissions with code quality issues
    # Note: consider H0 for each issues type from the set of them
    print(SEPARATOR)
    print('H0: The client and code quality issue\'s type not influence on '
          'the percentage of submissions with code quality issues:')
    p_values = {}
    for issue_type in issue_types:
        print(f'{SEPARATOR}ISSUE TYPE: {issue_type}. '
              f'WEB mean: {df_web[issue_type].mean().round(3)}, '
              f'IDE mean: {df_ide[issue_type].mean().round(3)} '
              f'{SEPARATOR}')
        ttest_result = ttest(df_web[issue_type], df_ide[issue_type])
        print(ttest_result)
        p_values[issue_type] = ttest_result.iloc[0][P_VALUE_COLUMN]
    valid_issues = ', '.join(_bonferroni_correction(p_values))
    print(f'THE ISSUES FOR VALID ANALYSIS: {valid_issues}')
    print(SEPARATOR)


def run_stat_tests(df_path: str, issue_types: Set[str], rq_set: Set[str]):
    df = read_df(df_path)

    for rq in rq_set:
        rq_upper = rq.upper()
        if rq_upper == 'RQ1':
            run_rq1(df, issue_types)
        elif rq_upper == 'RQ2':
            run_rq2(df)
        elif rq_upper == 'RQ3':
            run_rq3(df, issue_types)
        else:
            print(f'UNEXPECTED RQ: {rq}')


def parse_set_of_arguments(value: str) -> Set[str]:
    return set(value.split(','))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('dataset', type=str, help='Path to .csv file with Python dataset. '
                                                  'The dataset must have several obligatory columns:'

                                                  '- <total_attempts> with information about the '
                                                  'amount of consumption in this series; (RQ2)'
                                                  '- <attempt> with the attempt\'s number; (RQ2)'
                                                  '- <group> with the attempt chain\'s group number; (RQ2)'
                                                  '- <raw_issues_count> with the number of raw issues '
                                                  'in the submission; (RQ2)'

                                                  '- <client> with information where was solved the submission; (RQ3)'
                                                  '- <code_rows_count> with number of rows in the submission; (RQ3)'

                                                  '- columns for all issues, which are used '
                                                  'in the <-i> or <--issues> argument; (RQ1 and RQ3)')
    # Usage example: -i UnusedLocalVariable,MagicNumber
    # We checked the following issues:
    #   Python:
    #       - SC200 (SpellingErrorInName)
    #       - WPS432 (MagicNumber)
    #       - WPS350 (BadAssignPattern)
    #       - E226 (WhitespaceAroundArithmOper)
    #       - E231 (WhitespaceAfter,;:)
    #       - E225 (WhitespaceAroundOperator)
    #       - E265 (BlockCommentError)
    #       - WPS336 (ExplicitStringConcat)
    #       - WPS462 (WrongMultilineStringUsage)
    #       - WPS446 (ApproximateConstantUsage)
    #       - E211 (WhitespaceBefore()
    #       - W0311 (BadIndentation)
    #       - R1716 (SimplifyChainedComparison)
    #       - E261 (SpacesBeforeInlineComment)
    #       - WPS223 (TooManyElifsViolation)
    # The final list for Python:
    #   SC200,WPS432,WPS350,E226,E231,E225,E265,WPS336,WPS462,WPS446,E211,W0311,R1716,E261,WPS223
    #
    #   Java:
    #       - WhitespaceAroundCheck
    #       - MagicNumberCheck
    #       - IndentationCheck
    #       - WhitespaceAfterCheck
    #       - EmptyLineSeparatorCheck
    #       - UnusedLocalVariable
    #       - UnnecessaryParenthesesCheck
    #       - NeedBracesCheck
    #       - CommentsIndentationCheck
    #       - LocalVariableNameCheck
    #       - TypecastParenPadCheck
    #       - RightCurlyCheck
    #       - CallSuperInConstructor
    #       - LeftCurlyCheck
    #       - UnusedImportsCheck
    # The final list for Java:
    #   WhitespaceAroundCheck,MagicNumberCheck,IndentationCheck,WhitespaceAfterCheck,EmptyLineSeparatorCheck,
    #   UnusedLocalVariable,UnnecessaryParenthesesCheck,NeedBracesCheck,CommentsIndentationCheck,LocalVariableNameCheck,
    #   TypecastParenPadCheck,RightCurlyCheck,CallSuperInConstructor,LeftCurlyCheck,UnusedImportsCheck
    parser.add_argument('-i', '--issues',
                        help='Set of issues types that will be considered in RQs',
                        type=parse_set_of_arguments,
                        default=set())

    parser.add_argument('-rq', '--rq-set',
                        help='Set of RQ3 to check',
                        type=parse_set_of_arguments,
                        default={'RQ1', 'RQ2', 'RQ3'})
    args = parser.parse_args()

    print('Results:')
    run_stat_tests(args.dataset, args.issues, args.rq_set)
