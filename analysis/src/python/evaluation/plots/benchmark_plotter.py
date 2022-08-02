import argparse
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from analysis.src.python.evaluation.plots.common.plotly_consts import COLOR, MARGIN, SORT_ORDER
from analysis.src.python.evaluation.plots.common.utils import (
    create_box_plot,
    create_scatter_trace,
    get_supported_extensions,
    save_plot,
    update_figure,
)
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.utils.yaml_utils import parse_yaml


class ConfigFields(Enum):
    GROUP_BY = 'group_by'
    TIMING_COLUMN = 'timing_column'
    #
    AS_BOX_PLOT = 'as_box_plot'
    BINS = 'bins'
    #
    X_AXIS_NAME = 'x_axis_name'
    Y_AXIS_NAME = 'y_axis_name'
    MARGIN = 'margin'
    SORT_ORDER = 'sort_order'
    COLOR = 'color'


def plot_as_line_chart(
    df: pd.DataFrame,
    group_by: str,
    timing_column: str,
    bins: Optional[List[int]] = None,
    x_axis_name: Optional[str] = None,
    y_axis_name: Optional[str] = None,
    margin: Optional[MARGIN] = None,
    sort_order: Optional[SORT_ORDER] = None,
    color: Optional[List[COLOR]] = None,
) -> go.Figure:
    if bins is not None:
        df[group_by] = pd.cut(df[group_by], bins).astype(str)

    grouped_df = df.groupby(group_by)

    max_data = grouped_df[timing_column].max().reset_index()
    median_data = grouped_df[timing_column].median().reset_index()
    min_data = grouped_df[timing_column].min().reset_index()

    if color is not None:
        max_color, median_color, min_color = color
    else:
        max_color, median_color, min_color = [None] * 3

    max_trace = create_scatter_trace(
        max_data,
        x_column=group_by,
        y_column=timing_column,
        color=max_color,
        name='Max',
    )

    median_color = create_scatter_trace(
        median_data,
        x_column=group_by,
        y_column=timing_column,
        color=median_color,
        name='Median',
    )

    min_color = create_scatter_trace(
        min_data,
        x_column=group_by,
        y_column=timing_column,
        color=min_color,
        name='Min',
    )

    fig = go.Figure()
    fig.add_trace(max_trace)
    fig.add_trace(median_color)
    fig.add_trace(min_color)

    update_figure(
        fig,
        margin=margin,
        sort_order=sort_order,
        x_axis_name=group_by if x_axis_name is None else x_axis_name,
        y_axis_name=timing_column if y_axis_name is None else y_axis_name,
    )

    return fig


def plot_as_box_plot(
    df: pd.DataFrame,
    group_by: str,
    timing_column: str,
    bins: Optional[List[int]] = None,
    x_axis_name: Optional[str] = None,
    y_axis_name: Optional[str] = None,
    margin: Optional[MARGIN] = None,
    sort_order: Optional[SORT_ORDER] = None,
    color: Optional[COLOR] = None,
) -> go.Figure:
    if bins is not None:
        df[group_by] = pd.cut(df[group_by], bins).astype(str)

    fig = create_box_plot(
        df,
        x_axis=group_by,
        y_axis=timing_column,
        margin=margin,
        sort_order=sort_order,
        color=color,
    )

    update_figure(
        fig,
        x_axis_name=group_by if x_axis_name is None else x_axis_name,
        y_axis_name=timing_column if y_axis_name is None else y_axis_name,
    )

    return fig


def parse_config(config: Dict) -> None:
    if ConfigFields.MARGIN.value in config:
        config[ConfigFields.MARGIN.value] = MARGIN[config[ConfigFields.MARGIN.value].upper()]

    if ConfigFields.SORT_ORDER.value in config:
        config[ConfigFields.SORT_ORDER.value] = SORT_ORDER[config[ConfigFields.SORT_ORDER.value].upper()]

    if ConfigFields.COLOR.value in config:
        if isinstance(config[ConfigFields.COLOR.value], list):
            config[ConfigFields.COLOR.value] = list(
                map(lambda color: COLOR[color.upper()], config[ConfigFields.COLOR.value]),
            )
        else:
            config[ConfigFields.COLOR.value] = COLOR[config[ConfigFields.COLOR.value].upper()]


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_with_timings',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions and timings.',
    )

    parser.add_argument(
        'save_dir',
        type=lambda value: Path(value).absolute(),
        help='Path where the plotted chart will be saved.',
    )

    parser.add_argument(
        'config',
        type=lambda value: Path(value).absolute(),
        help='Path to .yml config file. For more information, see README.',
    )

    parser.add_argument(
        '--file-extension',
        type=str,
        default=AnalysisExtension.SVG.value,
        choices=get_supported_extensions(),
        help='Extension of output file.',
    )


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    args = parser.parse_args()

    config = parse_yaml(args.config)
    parse_config(config)

    df = read_df(args.submissions_with_timings)

    if config.get(ConfigFields.AS_BOX_PLOT.value):
        plot_function = plot_as_box_plot
    else:
        plot_function = plot_as_line_chart

    fig = plot_function(
        df,
        config.get(ConfigFields.GROUP_BY.value),
        config.get(ConfigFields.TIMING_COLUMN.value),
        config.get(ConfigFields.BINS.value),
        config.get(ConfigFields.X_AXIS_NAME.value),
        config.get(ConfigFields.Y_AXIS_NAME.value),
        config.get(ConfigFields.MARGIN.value),
        config.get(ConfigFields.SORT_ORDER.value),
        config.get(ConfigFields.COLOR.value),
    )

    save_plot(
        fig,
        args.save_dir,
        config.get(ConfigFields.TIMING_COLUMN.value),
        extension=AnalysisExtension(args.file_extension),
    )


if __name__ == '__main__':
    main()
