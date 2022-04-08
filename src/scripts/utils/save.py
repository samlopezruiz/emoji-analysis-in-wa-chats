import os

import pandas as pd


def get_agg_func(df):
    str_cols = ['line_in_chat', 'file', 'text', 'emoji', 'previous_words', 'following_words']
    f = {}
    for col in df.columns:
        f[col] = 'last' if col in str_cols else 'mean'
    f['count'] = 'sum'
    return f


def save_counts_stats(df, emoji_key, count, sequential=False):
    emojis_path = os.path.join('..', 'results', ('sequential' if sequential else 'single'), 'bigrams')
    os.makedirs(emojis_path, exist_ok=True)
    print('Saving: {}'.format(emoji_key), end='\r')
    file_path = os.path.join(emojis_path, '{}_{}_bigrams.csv'.format(count, emoji_key))
    df.to_csv(file_path, encoding='utf-8-sig')


def save_emoji_stats(emoji_stats, counts, save_agg=False, sequential=False):
    emojis_path = os.path.join('..', 'results', ('sequential' if sequential else 'single'), 'chats')
    os.makedirs(emojis_path, exist_ok=True)
    f = get_agg_func(emoji_stats)
    unique_emojis = len(emoji_stats['emoji'].unique())
    print('\n')

    emoji_stats.to_csv(os.path.join(emojis_path, 'top_emojis_chats.csv'), encoding='utf-8-sig', index=True)

    emoji_stats['count'] = 1
    grp_df = emoji_stats.groupby(by='emoji')

    emoji_index = {'emoji': [], 'count': []}
    for i, (emoji_key, df_ss) in enumerate(grp_df):
        print('Saving: {}/{}'.format(i + 1, unique_emojis), end='\r')
        file_path = os.path.join(emojis_path, '{}_{}_{}.csv'.format(i, counts[emoji_key], emoji_key))
        df_ss.to_csv(file_path, encoding='utf-8-sig')

        emoji_index['emoji'].append(emoji_key)
        emoji_index['count'].append(sum(df_ss['count']))

        if save_agg:
            df_ss_agg = df_ss.groupby(by=['file', 'line_in_chat']).agg(f)
            file_path = os.path.join(emojis_path, '{}_{}_{}_agg.csv'.format(i, counts[emoji_key], emoji_key))
            df_ss_agg.to_csv(file_path, encoding='utf-8-sig')

    emoji_index = pd.DataFrame.from_dict(emoji_index)
    emoji_index.to_csv(os.path.join(emojis_path, 'top_emojis_index.csv'), encoding='utf-8-sig', index=True)
