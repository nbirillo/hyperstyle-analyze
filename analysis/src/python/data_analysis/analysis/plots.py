from typing import Any, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator

from analysis.src.python.data_analysis.analysis.attrs import AttrType, get_attr
from analysis.src.python.data_analysis.analysis.statistics import Stats
from analysis.src.python.data_analysis.model.column_name import SubmissionColumns

sns.set_theme(style='whitegrid', font_scale=2, rc={"lines.linewidth": 5, "lines.markersize": 15})


def get_bins_count(data: List[Any]) -> int:
    """ Count number of bins for histogram. """

    n = len(np.unique(data))
    bins = int(np.ceil(1 + 3.32 * np.log(n)))
    return bins


def get_sub_axis(ax, k: int, rows: int, cols: int):
    """ For plot with subplots table gets subplot's axis by it's order number. """

    i, j = int(np.floor(k / cols)), k % cols
    if cols == 1 and rows == 1:
        return ax
    return ax[j] if rows == 1 else ax[i][j]


def draw_heatmap_compare(df: pd.DataFrame, attr_pairs: List[Tuple[AttrType, AttrType]], features: List[str]):
    """ Draw heatmaps to compare statistics and correlation between attribute pairs. """

    rows, cols = len(attr_pairs), len(features)
    fig, ax = plt.subplots(figsize=(20, 6 * len(attr_pairs)), ncols=cols, nrows=rows, constrained_layout=True)

    for i, attr_pair in enumerate(attr_pairs):

        attr_0, attr_1 = get_attr(attr_pair[0]), get_attr(attr_pair[1])

        for j, feature in enumerate(features):
            ax_sub = get_sub_axis(ax, i * cols + j, rows, cols)

            if feature == 'id':
                corr = df.pivot_table(feature, attr_0.name, attr_1.name, aggfunc='count')
                ax_sub.set_title('Count')
                fmt = 'd'
            else:
                corr = df.pivot_table(feature, attr_0.name, attr_1.name, aggfunc=np.mean)
                ax_sub.set_title(f'Average {feature}')
                fmt = '.2f'

            corr = corr.reindex(attr_0.values, axis=0)
            corr = corr.reindex(attr_1.values, axis=1)
            sns.heatmap(corr, annot=True, fmt=fmt, ax=ax_sub, linewidths=.5, cmap=sns.color_palette('flare'))


def draw_compare(df: pd.DataFrame, feature: str, attr: AttrType,
                 blur_ticks: Optional[List[str]] = None,
                 y_label: str = None,
                 title: str = None):
    """ Draw line plots for feature values distribution for different attributes. """

    attr = get_attr(attr)

    fig, ax = plt.subplots(figsize=(20, 10), constrained_layout=True)
    ranges = list(map(str, df[feature].values))

    for value in attr.values:
        sns.lineplot(x=ranges, y=df[value], ax=ax, label=value, marker='o', color=attr.palette[value])

    if blur_ticks is not None:
        for tick, tick_label in zip(ax.xaxis.get_ticklabels(), df[feature].values):
            if tick_label in blur_ticks:
                tick.set_color('grey')
            else:
                tick.set_color('black')

    if np.any(np.array(list(map(lambda t: len(str(t)), df[feature].values))) > 5):
        plt.xticks(rotation=45, ha="right", rotation_mode='anchor')

    if len(attr.values) > 5:
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", bbox_to_anchor=[0.5, -0.3], ncol=3, shadow=True, fancybox=True)
        if ax.get_legend() is not None:
            ax.get_legend().remove()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.show()

    ax.set_xlabel(feature)
    ax.set_ylabel('% submission' if y_label is None else y_label)
    plt.suptitle(f'Submissions % distributions by {attr.name}' if title is None else title)
    plt.show()


def draw_hist_plots(df: pd.DataFrame, features: List[str],
                    q: int = 0.99, log_scale: bool = False, kde: bool = False, bins: int = None,
                    y_label: str = '', title: str = ''):
    """ Draw hist plots table for given `features`. """

    n = len(features)
    rows, cols = int(np.ceil(n / 2)), min(2, n)
    fig, ax = plt.subplots(figsize=(cols * 12, rows * 7), nrows=rows, ncols=cols)

    for k, feature in enumerate(features):
        ax_sub = get_sub_axis(ax, k, rows, cols)

        df_filtered = df[(df[feature] < df[feature].quantile(q))]
        feature_bins = get_bins_count(df_filtered[feature].values) if bins is None else bins
        sns.histplot(data=df_filtered, x=feature, ax=ax_sub, log_scale=log_scale, kde=kde, bins=feature_bins)

        ax_sub.set_xlabel(feature)
        ax_sub.set_ylabel(y_label)
    plt.suptitle(title)
    plt.show()


def draw_count_plots(df: pd.DataFrame, attrs: List[AttrType],
                     y_label: str = '', title: str = ''):
    """ Draw count plots table for given `attrs`. """

    n = len(attrs)
    rows, cols = int(np.ceil(n / 2)), min(2, n)
    fig, ax = plt.subplots(figsize=(cols * 12, rows * 7), nrows=rows, ncols=cols)

    for k, attr in enumerate(attrs):
        ax_sub = get_sub_axis(ax, k, rows, cols)

        attr = get_attr(attr)
        sns.countplot(data=df, x=attr.name, ax=ax_sub, order=attr.values, palette=attr.palette)

        ax_sub.set_xlabel(attr.name)
        ax_sub.set_ylabel(y_label)
    plt.suptitle(title)
    plt.show()


def draw_stat_plot(df: pd.DataFrame, feature: str):
    fig, ax = plt.subplots(figsize=(20, 10), constrained_layout=True)
    sns.countplot(data=df, ax=ax, x=feature, order=df[feature].value_counts(ascending=False).index, color='grey')
    ax.set_yscale("log")

    plt.xticks(rotation=45, ha="right", rotation_mode='anchor')
    plt.show()


def draw_client_dynamic_graph(df: pd.DataFrame):
    """ Plot client dynamic graph for dataframe got form [statistics.get_submissions_series_client_dynamic]. """

    graph = nx.DiGraph()
    sorted_counts = list(np.sort(np.unique(df[Stats.COUNT.value])))

    for _, client_change in df.iterrows():
        attempt = client_change[SubmissionColumns.ATTEMPT.value]
        client = client_change['from']
        node = f'{client}_{attempt}'
        if not graph.has_node(node):
            dx = 0 if client == 'web' and attempt % 2 == 1 else 0.3
            dy = 0 if client == 'web' else 1
            graph.add_node(node, pos=(attempt + dx, dy))

    for i, client_change in df.iterrows():
        weight = client_change[Stats.COUNT.value]
        width = sorted_counts.index(weight)
        attempt = client_change[SubmissionColumns.ATTEMPT.value]

        client_from, client_to = client_change['from'], client_change['to']
        node_from, node_to = f'{client_from}_{attempt}', f'{client_to}_{attempt + 1}'

        if graph.has_node(node_to):
            graph.add_edge(node_from, node_to, weight=weight, width=(width + 5) / 2)

    plt.subplots(figsize=(15, 5))
    pos = nx.get_node_attributes(graph, 'pos')
    width = [graph[u][v]['width'] for u, v in graph.edges()]
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw(graph, pos, with_labels=True, edge_color='black', font_color='white', node_size=1500, width=width)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.show()
