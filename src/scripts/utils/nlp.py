from copy import deepcopy, copy

import numpy as np
import pandas as pd
from emoji import emoji_lis, demojize, emojize

from src.scripts.utils.util import shift_left_according_to_another_list

person_features = [('genero', 'G'),
                   ('orientacion_sexual', 'OS'),
                   ('lugar_nacimiento', 'LN'),
                   ('lugar_residencia', 'LR'),
                   ('idioma_natal', 'OL'),
                   ('nivel_estudio', 'NL'),
                   ('facultad', 'F'),
                   ('carrera', 'L'),
                   ('ocupacion', 'OC'),
                   ('sin_clasificar', 'PuO'),
                   ('referencia', 'Re'),
                   ]

def get_person_categories(s):
    if not isinstance(s, str):
        return {}

    categories = {}
    ls = np.array(s.split())
    for feature, ini_sep in person_features:
        ini_ix = np.where(ls == ini_sep)
        if len(ini_ix) > 0:
            substring = ls[ini_ix[0]+1][0]
            categories[feature] = substring

    return categories

def get_language(df, translate_client):
    ixs = np.random.randint(0, df.shape[0], size=10)
    random_lines = [df.iloc[ix, 1] for ix in ixs]

    langs = []
    for line in random_lines:
        try:
            lan = detect_language(line, translate_client)
            if not isinstance(lan['language'], list):
                langs.append(lan['language'])
        except:
            pass

    vals, count = np.unique(langs, return_counts=True)
    return vals[count.argmax()]


def detect_language(text, translate_client):
    """Detects the text's language."""
    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)

    return result

def find_emojis(s):
    return emoji_lis(s)


def get_stats_from_emojis(ems_loc, text, static_info=None, ignore_skins=True):
    orig_text = copy(text)
    pos = [em['location'] for em in ems_loc]

    # Remove skin tone from emojis if needed
    ems, skins = [], []
    for em in ems_loc:
        if 'skin_tone' in demojize(em['emoji']):
            remove_skin_pos = -1
            for i, c in enumerate(em['emoji']):
                if 'skin_tone' in demojize(c):
                    remove_skin_pos = i
                    skins.append(em['emoji'][i])

            if ignore_skins:
                emoji_wo_skin_color = em['emoji'][:remove_skin_pos] + em['emoji'][remove_skin_pos + 1:]
            else:
                emoji_wo_skin_color = em['emoji']

            ems.append(emoji_wo_skin_color)
        else:
            ems.append(em['emoji'])

    # Process text depending on ignore_skin preference


    skins_pos = [np.array([i for i in range(len(orig_text)) if orig_text.startswith(skin, i)]) for skin in np.unique(skins)]

    if len(skins_pos) > 0:
        skins_pos = np.concatenate(skins_pos)
        pos = shift_left_according_to_another_list(pos, skins_pos)

    if ignore_skins:
        for skin in np.unique(skins):
            text = text.replace(skin, "")
        n_letters = len(text)
    else:
        n_letters = len(text) - len(skins_pos)

    # Count unique emojis
    unique_ems, count = np.unique([demojize(e) for e in ems], return_counts=True)
    unique_ems_emojize = [emojize(e) for e in unique_ems]

    # Get list of letter and word positions for each emoji
    words = text.split()
    pos_words = [[] for _ in unique_ems]
    pos_letters = [[] for _ in unique_ems]

    for w, word in enumerate(words):
        for i, em in enumerate(unique_ems):
            for _ in range(demojize(word).count(em)):
                pos_words[i].append(w)

    for j, val in enumerate(unique_ems):
        for i, em in enumerate(ems):
            if demojize(em) == val:
                pos_letters[j].append(pos[i])

    # Raise error if computation is wrong
    if len(np.concatenate(pos_letters)) != len(np.concatenate(pos_words)):
        raise Exception('Error extracting emojis from: {}'.format(orig_text))

    result = {"text": text,
              "n_emojis": len(ems),
              "n_unique_emojis": len(unique_ems),
              "n_letters": n_letters,
              "n_words": len(words),
              "emojis": unique_ems_emojize,
              "count": count,
              "pos_in_letters": pos_letters,
              "pos_in_words": pos_words,
              }

    if static_info is not None:
        for info in static_info:
            result[info] = static_info[info]
    return result



def get_emojis_stats(chat, max_thold=100):
    # persons_cat = [get_person_categories(person) for person in persons]

    emojis_found = []
    for i in range(chat.shape[0]):
        text = chat.iloc[i, 1]

        if text is not np.nan and len(text) > 0:
            ems = find_emojis(text)

            if len(ems) > 0:
                if len(ems) <max_thold:
                    static_info = {'line': i,
                                   'person': chat.iloc[i, 0]
                                   }
                    try:
                        stats = get_stats_from_emojis(ems, text, static_info)
                        emojis_found.append(stats)
                    except:
                        print('error in line: {}'.format(text))
                else:
                    print('excluding line with {} emojis'.format(len(ems)))

    return emojis_found

def get_unique_emoji_stats(emojis_found, file):
    unique_emojis = {}
    for j, em_found in enumerate(emojis_found):
        for i, em in enumerate(em_found['emojis']):
            if (len(em_found['pos_in_letters'][i]) != len(em_found['pos_in_words'][i])):
                print(i, em)
                print(em_found)
                raise RuntimeError('len(pos_in_letters) != len(pos_in_words)')
            if em not in unique_emojis:
                unique_emojis[em] = deepcopy({'n_lines': 1,
                                              'ix': [j],
                                              'person': [em_found['person']],
                                              'lines': [em_found['line']],
                                              'count': [em_found['count'][i]],
                                              'total_count': em_found['count'][i],
                                              'file': [file for _ in em_found['pos_in_letters'][i]],
                                              'line_in_chat': [em_found['line'] for _ in em_found['pos_in_letters'][i]],
                                              'text': [em_found['text'] for _ in em_found['pos_in_letters'][i]],
                                              'n_letters': [em_found['n_letters'] for _ in em_found['pos_in_letters'][i]],
                                              'n_words': [em_found['n_words'] for _ in em_found['pos_in_words'][i]],
                                              'pos_in_letters': em_found['pos_in_letters'][i],
                                              'rel_pos_in_letters': [a/em_found['n_letters'] for a in em_found['pos_in_letters'][i]],
                                              'pos_in_words': em_found['pos_in_words'][i],
                                              'rel_pos_in_words': [a/em_found['n_words'] for a in em_found['pos_in_words'][i]],
                                              })
            else:
                unique_emojis[em]['n_lines'] += 1
                unique_emojis[em]['ix'].append(j)
                unique_emojis[em]['person'].append(em_found['person'])
                unique_emojis[em]['lines'].append(em_found['line'])
                unique_emojis[em]['count'].append(em_found['count'][i])
                unique_emojis[em]['total_count'] += em_found['count'][i]
                [unique_emojis[em]['file'].append(file) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['line_in_chat'].append(em_found['line']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['text'].append(em_found['text']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['n_letters'].append(em_found['n_letters']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['n_words'].append(em_found['n_words']) for _ in em_found['pos_in_words'][i]]
                [unique_emojis[em]['pos_in_letters'].append(a) for a in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['rel_pos_in_letters'].append(a/em_found['n_letters']) for a in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['pos_in_words'].append(a) for a in em_found['pos_in_words'][i]]
                [unique_emojis[em]['rel_pos_in_words'].append(a/em_found['n_words']) for a in em_found['pos_in_words'][i]]


    return unique_emojis


def get_counts_per_person_feature(feature, results):
    counts = []
    for i, res in enumerate(results):
        if len(res['unique_emojis']) > 0:
            df = res['stats']['count']
            try:
                feature_col = [res['persons'][p][feature] for p in df['person']]
                df[feature] = feature_col
                df['file'] = res['filename']
                counts.append(df)
            except KeyError as e:
                print('person feature not found in file: {}'.format(res['filename']))

    counts = pd.concat(counts, axis=0).sort_values(by='count', ascending=False)
    counts_emoji = counts.groupby(by=['emoji', feature]).sum().reset_index().sort_values(by='count', ascending=False)

    return counts_emoji