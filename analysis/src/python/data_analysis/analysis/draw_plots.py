import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from pandas import read_csv


def draw_compare_issues(stats_path: str, issue: str, pdf_filename: str):
    df_stats = read_csv(stats_path)
    df_issues_marked = read_csv('qodana_issues_marked.csv')
    df_issues_marked = df_issues_marked[df_issues_marked['mark'] == 1]
    df_stats = df_stats[df_stats['issue'].isin(df_issues_marked['issue'])][:20]

    sns.set_theme(style='whitegrid', font_scale=1.2, rc={"lines.linewidth": 3, "lines.markersize": 7})

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    for c in complexity:
        sns.lineplot(data=df_stats, x=issue, y=c, label=c, ax=ax, color=complexity_palette[c], marker='o')

    ax.set_ylim([-0.009, 0.3])
    ax.set_xlabel('')
    ax.set_ylabel('Percent of submissions with issue')
    plt.legend()
    plt.xticks(rotation=45, ha="right", rotation_mode='anchor')
    fig.savefig(f"{pdf_filename}.pdf", bbox_inches='tight')


def draw_issues(stats_path: str, pdf_filename: str):
    df_stats = read_csv(stats_path)
    df_issues_marked = read_csv('qodana_issues_marked.csv')
    df_issues_marked = df_issues_marked[df_issues_marked['mark'] == 1]
    df_stats = df_stats[df_stats['issue'].isin(df_issues_marked['issue'])]

    df_stats = df_stats.sort_values('count', axis=0, ascending=False)[:20]

    sns.set_theme(style='whitegrid', font_scale=1.2, rc={"lines.linewidth": 3, "lines.markersize": 7})
    fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=True)
    sns.barplot(data=df_stats, x='issue', y='count', ax=ax, color='grey')

    ax.set_ylim([0, 0.017])
    ax.set_xlabel('')
    ax.set_ylabel('Percent of submissions with issue')
    plt.xticks(rotation=45, ha="right", rotation_mode='anchor')
    fig.savefig(f"{pdf_filename}.pdf", bbox_inches='tight')


def draw_dynamic_issues(dynamic_path: str, pdf_filename: str, replace_path: str = None):
    sns.set_theme(style='whitegrid', font_scale=1.2, rc={"lines.linewidth": 5, "lines.markersize": 10})
    fig, ax = plt.subplots(figsize=(7, 10))

    df_dynamic = read_csv(dynamic_path)
    df_issues_marked = read_csv('qodana_issues_marked.csv')
    df_issues_marked = df_issues_marked[df_issues_marked['mark'] == 1]

    replace = None
    if replace_path is not None:
        df_replace = read_csv(replace_path)
        replace = {replace['class']: replace['name'] for _, replace in df_replace.iterrows()}

    k = -1
    for issue in df_dynamic.columns:
        if issue not in df_issues_marked.values:
            continue
        k += 1
        if k == 15:
            break
        label = issue
        if replace is not None:
            label = replace[label]
        sns.lineplot(data=df_dynamic, x='attempt', y=issue, ax=ax, label=label, marker='o')
    ax.set_ylabel('Percent of submissions with issue')
    ax.set_ylim([-0.005, 0.08])

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="center", bbox_to_anchor=[0.5, -0.15], ncol=1, shadow=True, fancybox=True)
    if ax.get_legend() is not None:
        ax.get_legend().remove()

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    fig.savefig(f"{pdf_filename}.pdf", bbox_inches='tight')


if __name__ == '__main__':
    # draw_compare_issues('raw_issues_by_complexity_stats_java_first.csv', 'issue', 'raw_issues_by_complexity_java_first')
    # draw_compare_issues('raw_issues_by_complexity_stats_python_first.csv', 'name', 'raw_issues_by_complexity_python_first')
    #
    # draw_dynamic_issues('raw_issues_dynamic_java.csv', 'raw_issues_dynamic_java')
    # draw_dynamic_issues('raw_issues_dynamic_python.csv', 'raw_issues_dynamic_python', 'raw_issues.csv')

    # draw_compare_issues('qodana_issues_by_complexity_stats_java_all.csv', 'issue',
    #                     'qodana_issues_by_complexity_java_all')
    # draw_issues('mean_qodana_issues_stats_java_first.csv', 'mean_qodana_issues_stats_java_first')
    # draw_issues('mean_qodana_issues_stats_java.csv', 'mean_qodana_issues_stats_java_all')

    draw_dynamic_issues('issues_dynamic_java.csv', 'qodana_issues_dynamic_java_1')
