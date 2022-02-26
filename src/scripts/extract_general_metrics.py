import os

import joblib
import numpy as np
import pandas as pd
import plotly.express as px

from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_emojis_stats, get_person_categories, \
    get_general_stats, concat_and_put_person_feature
from src.scripts.utils.plot import stacked_histogram

if __name__ == '__main__':
    es_folder = os.path.join('..', 'data', 'es')
    csv_files = os.listdir(es_folder)
    save_results = True
    sequential_emojis = False
    print('{} spanish chats found'.format(len(csv_files)))

    black_list = ['']
    results = []
    for i, csv_file in enumerate(csv_files[:700]):
        print('Progress: {}/{}'.format(i, len(csv_files)), end='\r')
        file_path = os.path.join(es_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)
        persons_cat = [get_person_categories(person) for person in [person_A, person_B]]
        emojis_found = get_emojis_stats(chat, max_thold=10, sequential=sequential_emojis)
        stats = get_general_stats(chat, emojis_found, csv_file)

        res = {'filename': csv_file,
               'emojis_in_chat': emojis_found,
               'persons': {"A": persons_cat[0], 'B': persons_cat[1]},
               }
        chat_result = {**res, **stats}

        results.append(chat_result)

    if save_results:
        print('...saving results')
        joblib.dump(results, os.path.join('..', 'data', 'emojis', ('sequential' if sequential_emojis else 'single'),
                                          'all_general_stats.z'))


    # #%%
    # lines_with_emojis = pd.concat([res['lines_with_emojis'] for res in results], axis=0)
    # from scipy import stats
    #
    # n_emojis = lines_with_emojis.loc[:, 'n_emojis']
    # z_score = stats.zscore(n_emojis)
    # removed_lines = n_emojis[z_score > 2]
    # print(min(removed_lines))
    #
    # #%%
    # thold= 10
    # print(1 - sum(n_emojis > thold) / len(n_emojis))
    #
    # #%%
    # fig = px.histogram(lines_with_emojis, x='n_emojis')
    # fig.show()
