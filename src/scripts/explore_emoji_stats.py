import os

import joblib
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

from src.scripts.prob.mutual_information import mutual_information_from_counts
from src.scripts.utils.nlp import merge_and_add_person_feature, get_value_counts_lastprev_words
from src.scripts.utils.plot import descending_bar_plot, stacked_histogram
from src.scripts.utils.save import save_emoji_stats, save_counts_stats
import numpy as np

if __name__ == '__main__':
    results_folder = os.path.join('..', 'data', 'emojis')
    save_csv = False
    sequential_emojis = False
    save_plots = True
    label_scale = 1
    res_path = os.path.join(results_folder, ('sequential' if sequential_emojis else 'single'), 'results.z')
    img_path = os.path.join('..', 'results', ('sequential' if sequential_emojis else 'single'), 'img')
    results_path = os.path.join('..', 'results', ('sequential' if sequential_emojis else 'single'))
    os.makedirs(results_path, exist_ok=True)
    results = joblib.load(res_path)
    print('...file loaded')

    # %% Get counts and plot
    total_counts = [res['stats']['count'] for res in results]
    total_counts = pd.concat(total_counts, axis=0).groupby(by='emoji').sum().sort_values(by='count', ascending=False)
    counts = total_counts.to_dict()['count']

    print('unique emojis: {}, emojis count: {}'.format(len(counts), sum(total_counts['count'])))
    total_counts.to_csv(os.path.join(results_path, 'total_count.csv'))

    # %% Aggregate stats
    all_stats = [pd.concat(res['stats']['positions'], axis=0) for res in results]
    emoji_stats = pd.concat(all_stats, axis=0)

    # %% Plot counts
    feature = 'genero' #, 'edad', 'lugar_nacimiento']
    plot_top = 50

    counts_emoji, all_lines = merge_and_add_person_feature(feature, results)
    counts_emoji = counts_emoji.loc[counts_emoji[feature] != 'N/A', :]
    dfs = []
    for g, df_ss in counts_emoji.groupby(feature):
        df_ss['perc'] = df_ss['count'] / sum(df_ss['count'])
        dfs.append(df_ss)
    counts_emoji = pd.concat(dfs, axis=0)

    total_counts_gender = counts_emoji.pivot_table(values=['count', 'perc'], columns='genero', index='emoji')
    total_counts_gender.fillna(0, inplace=True)
    total_counts_gender = total_counts_gender.astype(float)
    total_counts_gender['total'] = total_counts_gender['count']['Masculino'] + total_counts_gender['count']['Femenino']
    total_counts_gender.sort_values(by='total', ascending=False, inplace=True)
    total_counts_gender.reset_index(inplace=True)

    pvals = []
    for ix, row in total_counts_gender.iterrows():
        ixs_sorted = row['perc'].argsort().sort_values(ascending=False)
        if np.any(row['count'] == 0):
            pvals.append(np.nan)
        else:
            total = (row['count'] / row['perc'])[ixs_sorted.index]
            percs = row['perc'][ixs_sorted.index]
            count = row['count'][ixs_sorted.index]
            stat, pval = proportions_ztest(count.values, total.values, alternative='two-sided')
            pvals.append(pval)

    total_counts_gender['pval'] = pvals

    descending_bar_plot(counts_emoji,
                        x='emoji',
                        y='perc',
                        color=feature,
                        plot_top=plot_top,
                        file_path=os.path.join(img_path, '{}_count'.format(feature)),
                        label_scale=label_scale,
                        save=save_plots)

    total_counts_gender.to_csv(os.path.join(results_path, 'total_count_genero.csv'),index=False, encoding='utf-8-sig')

    #%% Mutual information
    # lines_count = all_lines.shape[0]
    masculino_count = sum(all_lines['genero'] == 'Masculino')
    femenino_count = sum(all_lines['genero'] == 'Femenino')

    em_keys, mis, gens, perc_m, perc_f = [] , [], [], [], []
    for emoji_key, df_ss in all_lines.groupby('emoji'):
        c_m = sum(df_ss['genero'] == 'Masculino')
        c_f = sum(df_ss['genero'] == 'Femenino')
        gens.append('Masculino' if c_m/masculino_count > c_f/femenino_count else 'Femenino')
        arr = np.array([[c_m, c_f], [masculino_count, femenino_count]])
        em_keys.append(emoji_key)
        mis.append(mutual_information_from_counts(arr))
        perc_m.append(c_m/masculino_count)
        perc_f.append(c_f/femenino_count)

    mi = pd.DataFrame()
    mi['emoji'] = em_keys
    mi['mi'] = mis
    mi['genero'] = gens
    mi['msgsPercFemenino'] = perc_f
    mi['msgsPercMasculino'] = perc_m
    mi.sort_values('mi', inplace=True, ascending=False)

    total_counts_gender.columns = [''.join(col) for col in total_counts_gender.columns]
    final_stats = pd.merge(total_counts_gender, mi, on='emoji', how='outer')
    final_stats.to_csv(os.path.join(results_path, 'mutual_information.csv'), encoding='utf-8-sig')

    # %% Filter top n emojis
    max_top = 10
    mask = emoji_stats['emoji'].isin(list(total_counts.index[:max_top]))
    filtered_stats = emoji_stats[mask]

    #%%
    filtered_stats_with_letters = emoji_stats.loc[emoji_stats['n_letters'] > emoji_stats['n_emojis']]
    stacked_histogram(filtered_stats_with_letters,
                      'rel_pos_in_letters',
                      groupby=None,
                      end=1,
                      bin_size=0.05,
                      file_path=os.path.join(img_path, 'rel_pos_in_letters_filtered_all'),
                      label_scale=label_scale,
                      save=save_plots)

    filtered_stats_with_letters.to_csv(os.path.join(results_path, 'filtered_stats_with_letters.csv'),
                                       encoding='utf-8-sig')

    #%% Get frequency of previous and following words
    freq_bigrams = {}
    for emoji_key, df_ss in filtered_stats.groupby(by=['emoji']):
        freq_bigrams[emoji_key] = {}
        freq_bigrams[emoji_key]['previous_words_count'] = df_ss['previous_words'].value_counts()
        freq_bigrams[emoji_key]['following_words_count'] = df_ss['following_words'].value_counts()
        freq_bigrams[emoji_key]['count'] = df_ss.shape[0]

        compiled_df = get_value_counts_lastprev_words(df_ss, emoji_key)

        if save_csv:
            save_counts_stats(compiled_df, emoji_key, df_ss.shape[0], sequential=sequential_emojis)

    #%% Save
    if save_csv:
        save_emoji_stats(filtered_stats, counts, save_agg=True, sequential=sequential_emojis)

    # %% Plot position distribution
    # plot_cfgs = [{'feature': 'n_letters', 'end': 100, 'bin_size': 1},
    #              {'feature': 'n_words', 'end': 10, 'bin_size': 1},
    #              {'feature': 'rel_pos_in_letters', 'end': 1, 'bin_size': 0.05},
    #              {'feature': 'pos_in_letters', 'end': 50, 'bin_size': 1},
    #              {'feature': 'rel_pos_in_words', 'end': 1, 'bin_size': 0.05},
    #              {'feature': 'pos_in_words', 'end': 15, 'bin_size': 1},
    #              ]
    # for p_cfg in plot_cfgs:
    #     stacked_histogram(filtered_stats,
    #                       p_cfg['feature'],
    #                       groupby='emoji',
    #                       end=p_cfg['end'],
    #                       bin_size=p_cfg['bin_size'],
    #                       file_path=os.path.join(img_path, p_cfg['feature']),
    #                       label_scale=label_scale,
    #                       save=save_plots)
    #%%
    filtered_stats_with_letters = filtered_stats.loc[filtered_stats['n_letters'] > filtered_stats['n_emojis']]
    filtered_stats_with_letters['rel_pos_in_letters_1'] = (filtered_stats_with_letters['pos_in_letters'] + 1) / \
                                                          filtered_stats_with_letters['n_letters']
    stacked_histogram(filtered_stats_with_letters,
                      'rel_pos_in_letters',
                      groupby='emoji',
                      end=1,
                      bin_size=0.05,
                      file_path=os.path.join(img_path, 'rel_pos_in_letters_filtered'),
                      label_scale=label_scale,
                      save=save_plots)

    # stacked_histogram(filtered_stats_with_letters,
    #                   'rel_pos_in_letters_1',
    #                   groupby='emoji',
    #                   end=1,
    #                   bin_size=0.05,
    #                   file_path=os.path.join(img_path, 'rel_pos_in_letters_filtered'),
    #                   label_scale=label_scale,
    #                   save=save_plots)

