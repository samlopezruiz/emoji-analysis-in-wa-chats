import pandas as pd


def get_df_from_emoji_stats(stats):
    df = pd.DataFrame()
    df['emoji'] = [row['emoji'] for row in stats]
    df['count'] = [row['count'] for row in stats]
    return df