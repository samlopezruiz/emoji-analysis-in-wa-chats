import os

import plotly.express as px

from src.scripts.utils.emoji import get_df_from_emoji_stats
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_unique_emoji_stats, get_emojis_stats
from src.scripts.utils.util import sort_dict_by_key

if __name__ == '__main__':
    es_folder = os.path.join('..', 'data', 'es')
    csv_files = os.listdir(es_folder)
    verbose = True
    print('{} spanish chats found'.format(len(csv_files)))

    results = []
    for csv_file in csv_files[:10]:
        if verbose:
            print('\nProcessing chat: {}'.format(csv_file))
        file_path = os.path.join(es_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)

        # %%
        emojis_found = get_emojis_stats(chat)
        unique_emojis = get_unique_emoji_stats(emojis_found)
        sorted_unique_emojis = sort_dict_by_key(sort_key='count', dict_to_sort=unique_emojis)
        df = get_df_from_emoji_stats(sorted_unique_emojis)

        if verbose:
            print('{}/{}: {}% lines contain emojis'.format(len(emojis_found),
                                                           chat.shape[0],
                                                           round(len(emojis_found) * 100 / chat.shape[0], 2)))
            print('{} unique emojis found'.format(len(unique_emojis.keys())))

        chat_result = {'filename': csv_file,
                       'emojis_in_chat': emojis_found,
                       'unique_emojis': sorted_unique_emojis,
                       'df': df
                       }

        results.append(chat_result)

    #%%
    df = results[3]['df']
    fig = px.bar(df,
                 x='emoji',
                 y='count',
                 title='Emojis count for chat {}'.format(csv_file),
                 text_auto=True)
    fig.update_layout(xaxis=dict(tickfont=dict(size=15)))
    fig.show()
