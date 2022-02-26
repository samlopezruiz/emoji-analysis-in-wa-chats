import numpy as np
import pandas as pd


def get_persons_attributes(results, features):
    cols = {}
    for res in results:
        for _, p in res['persons'].items():
            for feat in features:
                if feat in cols:
                    cols[feat].append(p[feat] if feat in p else 'N/A')
                else:
                    cols[feat] = [(p[feat] if feat in p else 'N/A')]

    persons = pd.DataFrame().from_dict(cols)
    return persons

def get_df_from_emoji_stats(stats, emoji_key='emoji', keys=None):
    if len(stats) == 0:
        return {'count': pd.DataFrame(),
                'positions': [pd.DataFrame()]}

    counts_per_person = []
    for stat in stats:
        count = pd.DataFrame()
        count['count'] = stat['count']
        count['person'] = stat['person']
        df_grp = count.groupby(by='person').sum()
        df_grp[emoji_key] = stat[emoji_key]
        df_grp.reset_index(inplace=True)
        counts_per_person.append(df_grp)

    count_res = pd.concat(counts_per_person, axis=0)

    positions = []
    for i, emoji_stats in enumerate(stats):
        # positions.append(pd.DataFrame.from_dict(emoji_stats))
        # print(i)
        pos = pd.DataFrame()
        if keys is None:
            keys = ['file', 'line_in_chat', 'text', 'n_letters', 'n_words', 'pos_in_words', 'rel_pos_in_words',
                    'pos_in_letters', 'rel_pos_in_letters', 'previous_words', 'following_words', 'n_emojis']
        keys.append(emoji_key)
        for key in keys:
            try:
                pos[key] = emoji_stats[key]
                # pos[key] = np.array(emoji_stats[key]).ravel()
            except Exception as e:
                print(e)
                print(i)
                print(emoji_stats)
        # pos['file'] = emoji_stats['file']
        # pos['line_in_chat'] = emoji_stats['line_in_chat']
        # pos['text'] = emoji_stats['text']
        # pos['n_letters'] = emoji_stats['n_letters']
        # pos['n_words'] = emoji_stats['n_words']
        # pos['pos_in_words'] = emoji_stats['pos_in_words']
        # pos['rel_pos_in_words'] = emoji_stats['rel_pos_in_words']
        # pos['pos_in_letters'] = emoji_stats['pos_in_letters']
        # pos['rel_pos_in_letters'] = emoji_stats['rel_pos_in_letters']
        # pos['emoji'] = emoji_stats['emoji']
        positions.append(pos)


    return {'count': count_res,
            'positions': positions}
