import os

import pandas as pd

from src.scripts.utils.emoji_lib import get_df_from_emoji_stats
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_unique_emoji_stats, get_emojis_stats, get_person_categories, \
    get_counts_per_person_feature
from src.scripts.utils.plot import descending_bar_plot, stacked_histogram
from src.scripts.utils.save import save_emoji_stats
from src.scripts.utils.util import sort_dict_by_key

if __name__ == '__main__':
    es_folder = os.path.join('..', 'data', 'es')
    csv_files = os.listdir(es_folder)
    verbose = False
    save_csv = True
    print('{} spanish chats found'.format(len(csv_files)))

    black_list = ['']
    results = []
    for i, csv_file in enumerate(csv_files[:30]):
        if verbose:
            print('\nProcessing chat: {}'.format(csv_file))
        else:
            print('Progress: {}/{}'.format(i, len(csv_files)), end='\r')

        file_path = os.path.join(es_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)
        persons_cat = [get_person_categories(person) for person in [person_A, person_B]]
        emojis_found = get_emojis_stats(chat, max_thold=100)
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

    # %% Get counts and plot
    total_counts = [res['stats']['count'] for res in results]
    total_counts = pd.concat(total_counts, axis=0).groupby(by='emoji').sum().sort_values(by='count', ascending=False)
    counts = total_counts.to_dict()['count']

    # %% Aggregate stats
    all_stats = [pd.concat(res['stats']['positions'], axis=0) for res in results]
    emoji_stats = pd.concat(all_stats, axis=0)

    # %% Plot counts
    features = ['genero', 'lugar_nacimiento']
    plot_top = 30

    for feature in features:
        counts_emoji = get_counts_per_person_feature(feature, results)
        descending_bar_plot(counts_emoji, x='emoji', y='count', color=feature, plot_top=30)

    # %% Filter top n emojis
    max_top = 10
    mask = emoji_stats['emoji'].isin(list(total_counts.index[:max_top]))
    filtered_positions = emoji_stats[mask]

    #%% Save
    if save_csv:
        save_emoji_stats(filtered_positions, counts, save_agg=True)

    # %% Plot position distribution
    stacked_histogram(filtered_positions, "n_letters", groupby='emoji', end=100, bin_size=1)
    stacked_histogram(filtered_positions, "n_words", groupby='emoji', end=10, bin_size=1)

    stacked_histogram(filtered_positions, "rel_pos_in_letters", groupby='emoji', end=1, bin_size=0.05)
    stacked_histogram(filtered_positions, "pos_in_letters", groupby='emoji', end=100, bin_size=1)
    stacked_histogram(filtered_positions, "rel_pos_in_words", groupby='emoji', end=1, bin_size=0.05)
    stacked_histogram(filtered_positions, "pos_in_words", groupby='emoji', end=20, bin_size=1)

