import logging
from typing import Any, Dict, Optional, Tuple, Union

from analysis.src.python.data_analysis.sample_selection.config import ConfigArguments, DEFAULT_NUMBER_OF_SAMPLES
from analysis.src.python.data_analysis.sample_selection.strategies import GroupStrategy

logger = logging.getLogger(__name__)


def _is_list(value: Any, classinfo: Union[type, Tuple[type, ...]]) -> bool:
    return isinstance(value, list) and all(isinstance(element, classinfo) for element in value)


def _validate_by_code_lines_count(args: Optional[Dict]) -> bool:
    # Only one argument needs to be specified.
    # !(a xor b) <=> a == b
    if args is None or ((ConfigArguments.BINS.value in args) == (ConfigArguments.COUNT.value in args)):
        logger.error(
            f"You must specify either the '{ConfigArguments.BINS.value}' argument or "
            f"the '{ConfigArguments.COUNT.value}' argument.",
        )
        return False

    if ConfigArguments.INCLUDE_BOUNDARIES.value in args and not isinstance(
        args[ConfigArguments.INCLUDE_BOUNDARIES.value],
        bool,
    ):
        logger.error(f"The '{ConfigArguments.INCLUDE_BOUNDARIES.value}' must be a boolean.")
        return False

    if ConfigArguments.INCLUDE_BOUNDARIES.value not in args:
        args[ConfigArguments.INCLUDE_BOUNDARIES.value] = False

    if ConfigArguments.COUNT.value in args and not (
        isinstance(args[ConfigArguments.COUNT.value], int) or _is_list(args[ConfigArguments.COUNT.value], int)
    ):
        logger.error(f"The '{ConfigArguments.COUNT.value}' can either be an integer or a list of integers.")
        return False

    if ConfigArguments.BINS.value in args and not _is_list(args[ConfigArguments.BINS.value], int):
        logger.error(f"The '{ConfigArguments.BINS.value}' must be a list of integers.")
        return False

    return True


def _validate_by_step_id(args: Optional[Dict]) -> bool:
    if args is None or ConfigArguments.IDS.value not in args:
        logger.warning(f"The '{ConfigArguments.IDS.value}' argument is not specified.")
        return False

    if not _is_list(args[ConfigArguments.IDS.value], int):
        logger.warning(f"The '{ConfigArguments.IDS.value}' must be a list of integers.")
        return False

    return True


def validate_config(config: Optional[Dict]) -> bool:
    if config is None:
        logger.error('The config is empty.')
        return False

    if ConfigArguments.NUMBER_OF_SAMPLES.value not in config:
        logger.info(
            f"'{ConfigArguments.NUMBER_OF_SAMPLES.value}' is not specified. "
            f'The default value will be used: {DEFAULT_NUMBER_OF_SAMPLES}.',
        )
        config[ConfigArguments.NUMBER_OF_SAMPLES.value] = DEFAULT_NUMBER_OF_SAMPLES

    if not isinstance(config[ConfigArguments.NUMBER_OF_SAMPLES.value], int):
        logger.error('The number of samples must be a integer.')
        return False

    if ConfigArguments.RANDOM_STATE.value in config and not isinstance(config[ConfigArguments.RANDOM_STATE.value], int):
        logger.error("The 'random_state' must be an integer.")
        return False

    if ConfigArguments.RANDOM_STATE.value not in config:
        config[ConfigArguments.RANDOM_STATE.value] = None

    # Check that there is one and only one strategy in the config
    if sum([strategy in config for strategy in GroupStrategy.strategies()]) != 1:
        logger.error('You must choose one and only one strategy.')
        return False

    strategy = GroupStrategy.from_config(config)
    args = config[strategy.value]

    if strategy is GroupStrategy.BY_CODE_LINES_COUNT and not _validate_by_code_lines_count(args):
        return False

    if strategy is GroupStrategy.BY_STEP_ID and not _validate_by_step_id(args):
        return False

    return True
