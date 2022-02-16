import pandas as pd


def client():
    df = pd.read_csv('new_client.csv')
    d = {
        'issue': list(df['issue'].unique()),
        'idea': list(df[df['client'] == 'idea']['count']),
        'web': list(df[df['client'] == 'web']['count']),
    }
    pd.DataFrame.from_dict(d).to_csv('issues_by_client_stats_python.csv', index=False)
    df = pd.read_csv('issues_by_client_stats_python.csv')
    df2 = pd.read_csv('../data/python/raw_issues.csv')
    raw_issues = {r['class']: r['name'] for i, r in df2.iterrows()}
    df['name'] = [raw_issues[issue] for issue in df['issue'].values]
    df.to_csv('issues_by_client_stats_python.csv', index=False)


def complexity():
    df = pd.read_csv('new_complexity.csv')
    d = {
        'issue': list(df['issue'][::3]),
        'shallow': list(df[df['complexity'] == 'shallow']['count']),
        'moderate': list(df[df['complexity'] == 'middle']['count']),
        'deep': list(df[df['complexity'] == 'deep']['count']),
    }
    pd.DataFrame.from_dict(d).to_csv('qodana_issues_by_complexity_stats_java_all.csv', index=False)
    # df = pd.read_csv('issues_by_client_stats_python.csv')
    # df2 = pd.read_csv('../data/python/raw_issues.csv')
    # raw_issues = {r['class']: r['name'] for i, r in df2.iterrows()}
    # df['name'] = [raw_issues[issue] for issue in df['issue'].values]
    # df.to_csv('issues_by_client_stats_python.csv', index=False)


if __name__ == '__main__':
    complexity()
