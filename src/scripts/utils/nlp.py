from copy import deepcopy

import emoji
import numpy as np

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
    return [c for c in s if c in emoji.UNICODE_EMOJI['en']]


def get_stats_from_emojis(ems, text):
    unique_ems, count = np.unique(ems, return_counts=True)

    em_wpos = [[] for _ in unique_ems]
    em_pos = [[] for _ in unique_ems]
    em_count = [0 for _ in unique_ems]

    pos = []
    start = 0
    for em in ems:
        e_pos = text[start:].find(em)
        pos.append(e_pos + start)
        start += e_pos

    for j, val in enumerate(unique_ems):
        for i, em in enumerate(ems):
            if em == val:
                em_pos[j].append(pos[i])
                em_count[j] += 1

    words = text.split()
    for i, word in enumerate(words):
        for j, val in enumerate(unique_ems):
            if val in word:
                em_wpos[j].append(i)

    result = {"text": text,
              "n_emojis": len(ems),
              "n_unique_emojis": len(unique_ems),
              "n_letters": len(text),
              "n_words": len(words),
              "emojis": unique_ems,
              "count": em_count,
              "pos_in_letters": em_pos,
              "pos_in_words": em_wpos,
              }

    return result

def get_emojis_stats(chat):
    emojis_found = []
    for i in range(chat.shape[0]):
        text = chat.iloc[i, 1]

        if text is not np.nan and len(text) > 0:
            ems = find_emojis(text)

            if len(ems) > 0:
                stats = get_stats_from_emojis(ems, text)
                stats['line'] = i
                emojis_found.append(stats)

    return emojis_found

def get_unique_emoji_stats(emojis_found):
    unique_emojis = {}
    for j, em_found in enumerate(emojis_found):
        for i, em in enumerate(em_found['emojis']):
            if em not in unique_emojis:
                unique_emojis[em] = deepcopy({'n_lines': 1,
                                              'ix': [j],
                                              'lines': [em_found['line']],
                                              'count': em_found['count'][i],
                                              'n_letters': [em_found['n_letters']],
                                              'n_words': [em_found['n_words']],
                                              'pos_in_letters': em_found['pos_in_letters'][i],
                                              'pos_in_words': em_found['pos_in_words'][i],
                                              })
            else:
                unique_emojis[em]['n_lines'] += 1
                unique_emojis[em]['ix'].append(j)
                unique_emojis[em]['lines'].append(em_found['line'])
                unique_emojis[em]['count'] += em_found['count'][i]
                unique_emojis[em]['n_letters'].append(em_found['n_letters'])
                unique_emojis[em]['n_words'].append(em_found['n_words'])
                [unique_emojis[em]['pos_in_letters'].append(a) for a in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['pos_in_words'].append(a) for a in em_found['pos_in_words'][i]]

    return unique_emojis