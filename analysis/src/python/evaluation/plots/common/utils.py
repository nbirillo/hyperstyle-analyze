import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from hyperstyle.src.python.review.common.file_system import Extension
from analysis.src.python.evaluation.plots.common import plotly_consts
from analysis.src.python.utils.extension_utils import AnalysisExtension

COLOR = Optional[plotly_consts.COLOR]
COLORWAY = Optional[plotly_consts.COLORWAY]
MARGIN = Optional[plotly_consts.MARGIN]
SORT_ORDER = Optional[plotly_consts.SORT_ORDER]
LINES = Optional[Dict[int, Optional[str]]]


def get_supported_extensions() -> List[str]:
    extensions = AnalysisExtension.get_image_extensions()
    extensions.append(AnalysisExtension.JSON)
    extensions.append(AnalysisExtension.HTML)
    return [extension.value for extension in extensions]


def create_bar_plot(
    df: pd.DataFrame,
    *,
    x_axis: str,
    y_axis: str,
    margin: MARGIN = None,
    sort_order: SORT_ORDER = None,
    color: COLOR = None,
    title: Optional[str] = None
) -> go.Figure:
    fig = px.bar(df, x=x_axis, y=y_axis, text=y_axis)
    update_figure(fig, margin=margin, sort_order=sort_order, color=color, title=title)
    return fig


def create_box_trace(
        df: pd.DataFrame,
        *,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        color: COLOR = None,
        name: Optional[str] = None,
) -> go.Box:
    return go.Box(
        x=df[x_column] if x_column is not None else None,
        y=df[y_column] if y_column is not None else None,
        line={'color': color.value if color is not None else None},
        name=name,
    )


def create_box_plot(
        df: pd.DataFrame,
        *,
        x_axis: Optional[str],
        y_axis: Optional[str],
        margin: MARGIN = None,
        sort_order: SORT_ORDER = None,
        color: COLOR = None,
        horizontal_lines: LINES = None,
        title: Optional[str] = None,
) -> go.Figure:
    fig = go.Figure(create_box_trace(df, x_column=x_axis, y_column=y_axis, color=color))
    update_figure(
        fig,
        margin=margin,
        sort_order=sort_order,
        horizontal_lines=horizontal_lines,
        x_axis_name=x_axis,
        y_axis_name=y_axis,
        title=title,
    )
    return fig


def create_scatter_trace(
        df: pd.DataFrame,
        *,
        x_column: str,
        y_column: str,
        name: Optional[str] = None,
        color: COLOR = None,
) -> go.Scatter:
    return go.Scatter(
        x=df[x_column],
        y=df[y_column],
        line={'color': color.value if color is not None else None},
        name=name,
    )


def create_line_chart(
        df: pd.DataFrame,
        *,
        x_axis: str,
        y_axis: str,
        margin: MARGIN = None,
        color: COLOR = None,
        vertical_lines: LINES = None,
        title: Optional[str] = None,
) -> go.Figure:
    fig = go.Figure(create_scatter_trace(df, x_column=x_axis, y_column=y_axis, color=color))
    update_figure(
        fig,
        margin=margin,
        vertical_lines=vertical_lines,
        x_axis_name=x_axis,
        y_axis_name=y_axis,
        title=title,
    )
    return fig


def create_histogram(
        df: pd.DataFrame,
        *,
        x_axis: str,
        y_axis: str,
        n_bins: Optional[int] = None,
        margin: MARGIN = None,
        color: COLOR = None,
        vertical_lines: LINES = None,
        title: Optional[None] = None,
) -> go.Figure:
    fig = px.histogram(df, x=x_axis, y=y_axis, nbins=n_bins)
    update_figure(
        fig,
        margin=margin,
        color=color,
        vertical_lines=vertical_lines,
        x_axis_name=x_axis,
        y_axis_name=y_axis,
        title=title,
    )
    return fig


def update_figure(
        fig: go.Figure,
        *,
        margin: MARGIN = None,
        sort_order: SORT_ORDER = None,
        color: COLOR = None,
        colorway: COLORWAY = None,
        horizontal_lines: LINES = None,
        vertical_lines: LINES = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
) -> None:
    new_layout = {}

    if margin is not None:
        new_layout["margin"] = margin.value

    if sort_order is not None:
        new_layout["xaxis"] = {"categoryorder": sort_order.value}

    if x_axis_name is not None:
        new_layout['xaxis_title'] = x_axis_name

    if y_axis_name is not None:
        new_layout['yaxis_title'] = y_axis_name

    if colorway is not None:
        new_layout['colorway'] = colorway.value

    if title is not None:
        new_layout['title'] = title

    fig.update_layout(**new_layout)

    new_trace = {}

    if color is not None:
        new_trace["marker"] = {"color": color.value}

    fig.update_traces(**new_trace)

    if horizontal_lines is not None:
        for y, annotation in horizontal_lines.items():
            fig.add_hline(y=y, annotation_text=annotation)

    if vertical_lines is not None:
        for x, annotation in vertical_lines.items():
            fig.add_vline(x=x, annotation_text=annotation, annotation_textangle=90)


def save_plot(
        fig: go.Figure,
        dir_path: Path,
        plot_name: str = "result_plot",
        extension: Union[Extension, AnalysisExtension] = AnalysisExtension.SVG,
) -> None:
    os.makedirs(dir_path, exist_ok=True)
    file = dir_path / f"{plot_name}{extension.value}"
    if extension == AnalysisExtension.HTML:
        fig.write_html(str(file))
    else:
        fig.write_image(str(file))
