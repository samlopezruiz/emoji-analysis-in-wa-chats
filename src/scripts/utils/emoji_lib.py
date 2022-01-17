import pandas as pd


def get_df_from_emoji_stats(stats):
    if len(stats) == 0:
        return {'count': pd.DataFrame(),
                'positions': [pd.DataFrame()]}

    counts_per_person = []
    for stat in stats:
        count = pd.DataFrame()
        count['count'] = stat['count']
        count['person'] = stat['person']
        df_grp = count.groupby(by='person').sum()
        df_grp['emoji'] = stat['emoji']
        df_grp.reset_index(inplace=True)
        counts_per_person.append(df_grp)

    count_res = pd.concat(counts_per_person, axis=0)

    positions = []
    for i, emoji_stats in enumerate(stats):
        # print(i)
        pos = pd.DataFrame()
        pos['file'] = emoji_stats['file']
        pos['line_in_chat'] = emoji_stats['line_in_chat']
        pos['text'] = emoji_stats['text']
        pos['n_letters'] = emoji_stats['n_letters']
        pos['n_words'] = emoji_stats['n_words']
        pos['pos_in_words'] = emoji_stats['pos_in_words']
        pos['rel_pos_in_words'] = emoji_stats['rel_pos_in_words']
        pos['pos_in_letters'] = emoji_stats['pos_in_letters']
        pos['rel_pos_in_letters'] = emoji_stats['rel_pos_in_letters']
        pos['emoji'] = emoji_stats['emoji']
        positions.append(pos)


    return {'count': count_res,
            'positions': positions}
