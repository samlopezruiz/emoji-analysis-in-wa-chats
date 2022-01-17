import os


def get_agg_func(df):
    str_cols = ['line_in_chat', 'file', 'text', 'emoji']
    f = {}
    for col in df.columns:
        f[col] = 'last' if col in str_cols else 'mean'
    f['count'] = 'sum'
    return f


def save_emoji_stats(emoji_stats, counts, save_agg=False):
    emojis_path = os.path.join('..', 'data', 'emojis')
    os.makedirs(emojis_path, exist_ok=True)
    f = get_agg_func(emoji_stats)
    unique_emojis = len(emoji_stats['emoji'].unique())
    print('\n')

    emoji_stats.to_csv(os.path.join(emojis_path, 'top_all_emojis.csv'), encoding='utf-8-sig')

    for i, (emoji_key, df_ss) in enumerate(emoji_stats.groupby(by='emoji')):
        print('Saving: {}/{}'.format(i+1, unique_emojis), end='\r')
        file_path = os.path.join(emojis_path, '{}_{}.csv'.format(counts[emoji_key], emoji_key))
        df_ss['count'] = 1
        df_ss.to_csv(file_path, encoding='utf-8-sig')

        if save_agg:
            df_ss_agg = df_ss.groupby(by=['file', 'line_in_chat']).agg(f)
            file_path = os.path.join(emojis_path, '{}_{}_agg.csv'.format(counts[emoji_key], emoji_key))
            df_ss_agg.to_csv(file_path, encoding='utf-8-sig')