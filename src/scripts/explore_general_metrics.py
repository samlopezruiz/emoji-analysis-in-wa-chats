import os
from pprint import pprint

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from src.scripts.utils.emoji_lib import get_persons_attributes
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_emojis_stats, get_person_categories, \
    get_general_stats, concat_and_put_person_feature, remove_emojis_from_text
from src.scripts.utils.plot import stacked_histogram, plotly_save

if __name__ == '__main__':
    results_folder = os.path.join('..', 'data', 'emojis')
    save_csv = True
    sequential_emojis = False
    save_plots = False

    res_path = os.path.join(results_folder, ('sequential' if sequential_emojis else 'single'), 'all_general_stats.z')
    img_path = os.path.join('..', 'results', ('sequential' if sequential_emojis else 'single'), 'img', 'general')
    results = joblib.load(res_path)
    print('...file loaded')

    # %% Get counts and plot
    feature = ['genero', 'edad']
    res = concat_and_put_person_feature(feature, results)

    # %% General stats
    print('total n_words including emojis: {}'.format(sum(res['chats']['n_words'])))
    print('total n_words (inlcuding emojis) of lines with emojis: {}'.format(sum(res['all_lines_with_emojis']['n_words'])))
    print('total n_words excluding emojis: {}'.format(sum(res['chats']['n_words_wo_e'])))

    # %% Line count per gender
    generos = ['Masculino', 'Femenino']
    line_counts = {}
    for g in generos:
        all = sum((res['chats']['genero'] == g).astype(int))
        w_emojis = sum((res['all_lines_with_emojis']['genero'] == g).astype(int))
        line_counts[g] = {'total': all, 'count': w_emojis, 'perc': w_emojis / all}

    pprint(line_counts)
    #%%
    feats = ['edad', 'genero']
    persons = get_persons_attributes(results, feats)

    # %%
    persons_ages = persons.loc[persons['edad'] != 'N/A', :]
    persons_ages['edad'] = persons_ages['edad'].astype(int)
    fig = px.histogram(data_frame=persons_ages, x='edad')
    fig.show()

    series = persons_ages['edad']
    print('edad: media={}, std={}'.format(round(series.mean(), 4), round(series.std(), 4)))
    for g in ['Masculino', 'Femenino']:
        series = persons_ages.loc[persons_ages['genero'] == g, :]['edad']
        print('{} edad: media={}, std={}'.format(g, round(series.mean(), 4), round(series.std(), 4)))

    #%% count number of turns
    person_in_lines = (res['chats']['person'] == 'A').astype(int)
    diff_person = person_in_lines.diff() #.dropna()
    ones = np.where(diff_person == 1)[0]
    minus_one = np.where(diff_person == -1)[0]
    print('{} {}'.format(ones.shape, minus_one.shape))

    l = min(ones.shape[0], minus_one.shape[0])
    if ones[0] > minus_one[0]:
        turn_lengthsA = ones[:l] - minus_one[:l]
        turn_lengthsB = minus_one[1:l] - ones[:l-1]
    else:
        turn_lengthsA = minus_one[:l] - ones[:l]
        turn_lengthsB = ones[1:l] - minus_one[:l-1]

    turns = np.hstack([turn_lengthsA, turn_lengthsB])
    print('average length per turn: {}'.format(np.mean(turns)))
    print('total turn changes: {}'.format(len(turn_lengthsA)))

    # %%
    label_scale = 1
    stats = res['all_lines_with_emojis']
    plot_cfgs = [{'feature': 'n_letters', 'end': 100, 'bin_size': 1},
                 {'feature': 'n_words', 'end': 10, 'bin_size': 1},
                 {'feature': 'edad', 'end': 100, 'bin_size': 1},
                 {'feature': 'n_emojis', 'end': 10, 'bin_size': 1}]

    for p_cfg in plot_cfgs:
        stacked_histogram(stats,
                          p_cfg['feature'],
                          groupby=None,
                          end=p_cfg['end'],
                          bin_size=p_cfg['bin_size'],
                          file_path=os.path.join(img_path, p_cfg['feature']),
                          label_scale=label_scale,
                          save=save_plots)

    # %%
    from statsmodels.stats.proportion import proportions_ztest

    ixs = np.flip(np.array([val['perc'] for _, val in line_counts.items()]).argsort())
    percs = np.array([val['perc'] for _, val in line_counts.items()])[ixs]
    features = np.array([k for k, val in line_counts.items()])[ixs]
    total = np.array([val['total'] for _, val in line_counts.items()])[ixs]
    count = np.array([val['count'] for _, val in line_counts.items()])[ixs]

    stat, pval = proportions_ztest(count, total)
    if pval <= 0.05:
        print('p:{} < 0.05, usage for features: {} is not the same: {}'.format(pval, features,
                                                                               percs))
    else:
        print('p:{} > 0.05, usage for features: {} is nos significantly different: {}'.format(pval, features,
                                                                                              percs))

    stat, pval = proportions_ztest(count, total, alternative='larger')
    if pval <= 0.05:
        print('p:{} < 0.05, usage for feature: {} is larger than {}: {} > {}'.format(pval, features[0], features[1],
                                                                                     percs[0], percs[1]))
    else:
        print('p:{} > 0.05, usage for feature: {} is not larger than {}: {} > {}'.format(pval, features[0], features[1],
                                                                                         percs[0], percs[1]))
    all_counts = total
    all_tota = total
    stat, pval = proportions_ztest(all_counts, total)
    # %%
    import plotly.express as px

    df = pd.DataFrame()
    df['feature'] = features
    df['percs'] = percs
    df['wo/emoji'] = total - count
    df['w/emoji'] = count

    # df = pd.melt(df, id_vars=['feature'], value_vars=['wo/emoji', 'w/emoji'])
    # fig = px.bar(df, x="feature", y="value", color="variable", title="Chat line counts")
    # fig.show()

    #%%
    key = 'chats'
    df = res[key].loc[res[key]['genero'] != '', :]
    df = df.loc[df['genero'] != 'N/A', :]
    all_fig = stacked_histogram(df, feature='n_words', end=30, bin_size=1, return_fig=True, legend_name='all chats')

    key = 'all_lines_with_emojis'
    df = res[key].loc[res[key]['genero'] != '', :]
    df = df.loc[df['genero'] != 'N/A', :]
    e_fig = stacked_histogram(df, feature='n_words', end=30, bin_size=1, return_fig=True, legend_name='with emojis')

    fig = make_subplots(rows=1, cols=2)
    fig.add_traces(all_fig.data,  rows=1, cols=1)
    fig.add_traces(e_fig.data,  rows=1, cols=2)
    fig.update_layout(title='Distibution of: n_words')
    fig.show()

    key = 'chats'
    df = res[key].loc[res[key]['genero'] != '', :]
    df = df.loc[df['genero'] != 'N/A', :]
    all_fig = stacked_histogram(df, feature='n_letters', end=30, bin_size=1, return_fig=True, legend_name='all chats')

    key = 'all_lines_with_emojis'
    df = res[key].loc[res[key]['genero'] != '', :]
    df = df.loc[df['genero'] != 'N/A', :]
    e_fig = stacked_histogram(df, feature='n_letters', end=30, bin_size=1, return_fig=True, legend_name='with emojis')

    fig = make_subplots(rows=1, cols=2)
    fig.add_traces(all_fig.data, rows=1, cols=1)
    fig.add_traces(e_fig.data, rows=1, cols=2)
    fig.update_layout(title='Distibution of: n_letters')
    fig.show()

    if img_path is not None and save_plots:
        plotly_save(fig, os.path.join(img_path, 'n_words_distribution'), size=(1980, 1080))


    #%%
    all_persons = []
    for r in results:
        for _, p in r['persons'].items():
            if 'genero' in p:
                all_persons.append(p['genero'])

    all_persons = np.array(all_persons)
    count_gender = np.unique(all_persons, return_counts=True)
    pprint(count_gender)