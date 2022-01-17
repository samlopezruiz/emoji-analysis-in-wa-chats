import os

import emoji
import numpy as np
import pandas as pd
import plotly.express as px
from emoji import emojize, demojize, get_emoji_regexp, emoji_lis, distinct_emoji_lis

from src.scripts.utils.emoji_lib import get_df_from_emoji_stats
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_unique_emoji_stats, get_emojis_stats, get_person_categories, \
    get_counts_per_person_feature
from src.scripts.utils.plot import plot_position_histogram, descending_bar_plot
from src.scripts.utils.util import sort_dict_by_key

if __name__ == '__main__':
    es_folder = os.path.join('..', 'data', 'es')
    csv_files = os.listdir(es_folder)
    verbose = False
    print('{} spanish chats found'.format(len(csv_files)))

    black_list = ['']
    results = []
    for i, csv_file in enumerate(csv_files[71:500]):
        if verbose:
            print('\nProcessing chat: {}'.format(csv_file))
        else:
            print('Progress: {}/{}'.format(i, len(csv_files)), end='\r')

        file_path = os.path.join(es_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)

        # %%
        persons_cat = [get_person_categories(person) for person in [person_A, person_B]]
        emojis_found = get_emojis_stats(chat, max_thold=100)
        unique_emojis = get_unique_emoji_stats(emojis_found)
        sorted_unique_emojis = sort_dict_by_key(sort_key='total_count', dict_to_sort=unique_emojis)
        stats = get_df_from_emoji_stats(sorted_unique_emojis)

        if verbose:
            print('{}/{}: {}% lines contain emojis'.format(len(emojis_found),
                                                           chat.shape[0],
                                                           round(len(emojis_found) * 100 / chat.shape[0], 2)))
            print('{} unique emojis found'.format(len(unique_emojis.keys())))

        chat_result = {'filename': csv_file,
                       'emojis_in_chat': emojis_found,
                       'persons': {"A": persons_cat[0], 'B': persons_cat[1]},
                       'unique_emojis': sorted_unique_emojis,
                       'stats': stats
                       }

        results.append(chat_result)

    # %%
    count = results[0]['stats']['count']
    fig = px.bar(count,
                 x='emoji',
                 y='count',
                 color='person',
                 title='Emojis count for chat {}'.format(csv_file),
                 text_auto=True).update_xaxes(categoryorder="total descending")
    fig.update_layout(xaxis=dict(tickfont=dict(size=15)))
    fig.show()

    # %% Plot single histogram of an chat
    file_ix = 0
    emoji_ix = 0
    emojis_in_chat = results[file_ix]['emojis_in_chat']
    sorted_unique_emojis = results[file_ix]['unique_emojis']
    positions = results[file_ix]['stats']['positions'][emoji_ix]

    title = 'Position distribution for emoji: {} <br>Count: {}, Chat: {}'.format(sorted_unique_emojis[emoji_ix]['emoji'],
                                                                                 sorted_unique_emojis[emoji_ix]['total_count'],
                                                                                 results[file_ix]['filename'])
    plot_position_histogram(positions, title)