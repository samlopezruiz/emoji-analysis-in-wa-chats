import os
from pprint import pprint
from tabulate import tabulate
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from src.scripts.utils.emoji_lib import get_persons_attributes
from src.scripts.utils.nlp import concat_and_put_person_feature
from src.scripts.utils.plot import stacked_histogram, plotly_save
from src.scripts.utils.util import tabulate_dict

if __name__ == '__main__':
    results_folder = os.path.join('..', 'data', 'emojis')
    save_csv = False
    sequential_emojis = False
    save_plots = False

    res_path = os.path.join(results_folder, ('sequential' if sequential_emojis else 'single'), 'all_general_stats.z')
    img_path = os.path.join('..', 'results', ('sequential' if sequential_emojis else 'single'), 'img', 'general')
    results = joblib.load(res_path)
    print('...file loaded')

    # %% Get counts and plot
    generos = ['Masculino', 'Femenino']
    feature = ['genero', 'edad']
    res = concat_and_put_person_feature(feature, results)

    # %% No. words
    n_words = float(sum(res['chats']['n_words']))
    n_words_wo_e = float(sum(res['chats']['n_words_wo_e']))

    word_count = {}
    for g in generos:
        word_count_per_gender = float(sum(res['chats']['n_words'].loc[res['chats']['genero'] == g]))
        word_count[g] = {
            # 'total words': n_words,
            # 'total words wo emojis': n_words_wo_e,
            'num words': word_count_per_gender,
            '%': word_count_per_gender / n_words
        }
    float_precisions = [0] * len(list(word_count[list(word_count)[0]].keys()))
    float_precisions[-1] = 4
    print(tabulate_dict(word_count, float_precisions, totals=True))

    # %% Messages count per gender

    line_counts = {}
    for g in generos:
        all = sum((res['chats']['genero'] == g))
        w_emojis = sum((res['all_lines_with_emojis']['genero'] == g))
        line_counts[g] = {'messages': float(all),
                          'messages with emojis': float(w_emojis),
                          '%': w_emojis / all}

    float_precisions = [0] * len(list(line_counts[list(line_counts)[0]].keys()))
    float_precisions[-1] = 4
    print(tabulate_dict(line_counts, float_precisions, totals=True))

    # %%
    feats = ['edad', 'genero']
    persons = get_persons_attributes(results, feats)

    persons_ages = persons.loc[persons['edad'] != 'N/A', :]
    persons_ages['edad'] = persons_ages['edad'].astype(int)
    # fig = px.histogram(data_frame=persons_ages, x='edad')
    # fig.show()

    rows = []
    series = persons_ages['edad']
    rows.append(['All', series.mean(), series.std()])
    for g in ['Masculino', 'Femenino']:
        series = persons_ages.loc[persons_ages['genero'] == g, :]['edad']
        rows.append([g, series.mean(), series.std()])

    print(tabulate(rows,
                   headers=['Age mean', 'Age std'],
                   tablefmt='psql',
                   floatfmt=[None, ",.4f", ",.4f"],
                   stralign="right"))

    # %% count number of turns
    person_in_lines = (res['chats']['person'] == 'A').astype(int)
    diff_person = person_in_lines.diff()  # .dropna()
    ones = np.where(diff_person == 1)[0]
    minus_one = np.where(diff_person == -1)[0]
    print('{} {}'.format(ones.shape, minus_one.shape))

    l = min(ones.shape[0], minus_one.shape[0])
    if ones[0] > minus_one[0]:
        turn_lengthsA = ones[:l] - minus_one[:l]
        turn_lengthsB = minus_one[1:l] - ones[:l - 1]
    else:
        turn_lengthsA = minus_one[:l] - ones[:l]
        turn_lengthsB = ones[1:l] - minus_one[:l - 1]

    turns = np.hstack([turn_lengthsA, turn_lengthsB])
    print('average messages per turn: {}'.format(np.mean(turns)))
    print('total turn changes: {}'.format(len(turn_lengthsA)))

    # %%
    label_scale = 1
    stats = res['all_lines_with_emojis']

    emojis_per_gender = {}
    for g in generos:
        n_emojis = stats['n_emojis'][stats['genero'] == g]
        emojis_per_gender[g] = {'num emojis': float(sum(n_emojis)),
                                'mean per message': np.mean(n_emojis)}

    float_precisions = [0] * len(list(emojis_per_gender[list(emojis_per_gender)[0]].keys()))
    float_precisions[-1] = 4
    print(tabulate_dict(emojis_per_gender, float_precisions, totals=True))

    # %%
    #
    # plot_cfgs = [{'feature': 'n_letters', 'end': 100, 'bin_size': 1},
    #              {'feature': 'n_words', 'end': 10, 'bin_size': 1},
    #              {'feature': 'edad', 'end': 100, 'bin_size': 1},
    #              {'feature': 'n_emojis', 'end': 10, 'bin_size': 1}]
    #
    # for p_cfg in plot_cfgs:
    #     stacked_histogram(stats,
    #                       p_cfg['feature'],
    #                       groupby=None,
    #                       end=p_cfg['end'],
    #                       bin_size=p_cfg['bin_size'],
    #                       file_path=os.path.join(img_path, p_cfg['feature']),
    #                       label_scale=label_scale,
    #                       save=save_plots)

    # %%
    from statsmodels.stats.proportion import proportions_ztest

    ixs = np.flip(np.array([val['%'] for _, val in line_counts.items()]).argsort())
    percs = np.array([val['%'] for _, val in line_counts.items()])[ixs]
    features = np.array([k for k, val in line_counts.items()])[ixs]
    total = np.array([val['messages'] for _, val in line_counts.items()])[ixs]
    count = np.array([val['messages with emojis'] for _, val in line_counts.items()])[ixs]

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

    # df = pd.DataFrame()
    # df['feature'] = features
    # df['percs'] = percs
    # df['wo/emoji'] = total - count
    # df['w/emoji'] = count

    # df = pd.melt(df, id_vars=['feature'], value_vars=['wo/emoji', 'w/emoji'])
    # fig = px.bar(df, x="feature", y="value", color="variable", title="Chat line counts")
    # fig.show()

    # %%
    for feature in ['n_words', 'n_letters']:

        all_fig = stacked_histogram(res['chat_wo_media'], feature=feature, end=30, bin_size=1, return_fig=True,
                                    legend_name='all messages')
        e_fig = stacked_histogram(res['all_lines_with_emojis'], feature=feature, end=30, bin_size=1, return_fig=True,
                                  legend_name='messages with emojis')

        fig = make_subplots(rows=1, cols=2)
        fig.add_traces(all_fig.data, rows=1, cols=1)
        fig.add_traces(e_fig.data, rows=1, cols=2)
        fig.update_layout(title='Distibution of: {}'.format(feature))
        fig.show()

        if img_path is not None and save_plots:
            plotly_save(fig, os.path.join(img_path, '{}_distribution'.format(feature)), size=(1980, 1080))

    # res['chat_wo_media'].to_csv('chat_wo_media.csv', encoding='utf-8-sig')

    # %%
    all_persons = []
    for r in results:
        for _, p in r['persons'].items():
            if 'genero' in p:
                all_persons.append(p['genero'])


    all_persons = np.array(all_persons)
    count_gender = np.unique(all_persons, return_counts=True)
    gender_count = {}
    for key, count in zip(*count_gender):
        gender_count[key] = {'persons': count}

    print(tabulate_dict(gender_count, totals=True))
