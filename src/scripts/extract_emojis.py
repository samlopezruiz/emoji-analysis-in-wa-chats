import os

import joblib
import pandas as pd

from src.scripts.utils.emoji_lib import get_df_from_emoji_stats
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_unique_emoji_stats, get_emojis_stats, get_person_categories, \
    get_counts_per_person_feature, get_value_counts_lastprev_words
from src.scripts.utils.plot import descending_bar_plot, stacked_histogram
from src.scripts.utils.save import save_emoji_stats, save_counts_stats
from src.scripts.utils.util import sort_dict_by_key

if __name__ == '__main__':
    es_folder = os.path.join('..', 'data', 'es')
    csv_files = os.listdir(es_folder)
    verbose = False
    save_results = True
    sequential_emojis = False
    print('{} spanish chats found'.format(len(csv_files)))

    black_list = ['']
    results = []
    for i, csv_file in enumerate(csv_files[:700]):
        if verbose:
            print('\nProcessing chat: {}'.format(csv_file))
        else:
            print('Progress: {}/{}'.format(i, len(csv_files)), end='\r')

        file_path = os.path.join(es_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)
        persons_cat = [get_person_categories(person) for person in [person_A, person_B]]
        emojis_found = get_emojis_stats(chat, max_thold=10, sequential=sequential_emojis)
        unique_emojis = get_unique_emoji_stats(emojis_found, csv_file)
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
    if save_results:
        print('...saving results.z')
        joblib.dump(results, os.path.join('..', 'data', 'emojis', ('sequential' if sequential_emojis else 'single'), 'results.z'))

