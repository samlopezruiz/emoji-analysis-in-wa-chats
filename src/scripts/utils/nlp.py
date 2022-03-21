import re
from copy import deepcopy, copy

import emoji
import numpy as np
import pandas as pd
from emoji import emoji_lis, demojize, emojize

from src.scripts.utils.util import shift_left_according_to_another_list

person_features = [
                    ('edad', 'E'),
                    ('genero', 'G'),
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
            substring = ls[ini_ix[0] + 1][0]
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


def sequential_emojis(text, emojis):
    diff = np.insert(np.diff([int(l in emojis) for l in text]), 0, int(text[0] in emojis))
    starts, ends = np.where(diff == 1)[0], np.where(diff == -1)[0]
    ends = np.append(ends, len(text)) if len(ends) < len(starts) else ends

    sizes = [e - s - 1 for s, e in zip(starts, ends)]
    seq_emojis = [emojize(demojize(text[s:e])) for s, e in zip(starts, ends)]
    return {'starts': starts,
            'ends': ends,
            'sizes': sizes,
            'seq_emojis': seq_emojis}


# def prev_follow_words(text, emojis):
# # ems_loc = find_emojis(text)
# # unique_ems, count = np.unique([demojize(e) for e in ems], return_counts=True)
# diff = np.insert(np.diff([int(l in emojis) for l in text]), 0, int(text[0] in emojis))
# starts, ends = np.where(diff == 1)[0], np.where(diff == -1)[0]
# ends = np.append(ends, len(text)) if len(ends) < len(starts) else ends
# contiguous_emojis = [emojize(demojize(text[s:e])) for s, e in zip(starts, ends)]
#
# previous_words = [''] * len(contiguous_emojis)
# following_words = [''] * len(contiguous_emojis)
# for i, (s, e) in enumerate(zip(starts, ends)):
#     if s > 1:
#         p = s - 1 if text[s - 1] != ' ' else s - 2
#         while text[p] != ' ' and p > 0:
#             p -= 1
#         previous_words[i] = text[p:s].strip()
#
#     if e < len(text) - 1:
#         p = e if text[e] != ' ' else e + 1
#         while p < len(text) and text[p] != ' ':
#             p += 1
#         following_words[i] = text[e:p].strip()
#
# return contiguous_emojis, previous_words, following_words

def prev_follow_words(unique_emojis, text, starts, ends=None):
    # ems_loc = find_emojis(text)
    # unique_ems, count = np.unique([demojize(e) for e in ems], return_counts=True)
    # diff = np.insert(np.diff([int(l in emojis) for l in text]), 0, int(text[0] in emojis))
    # starts, ends = np.where(diff == 1)[0], np.where(diff == -1)[0]
    if ends is None:
        ends = np.array(starts) + 1
        # ends = np.array(starts) + [len(em) for em in unique_emojis]

    ends = np.append(ends, len(text)) if len(ends) < len(starts) else ends
    contiguous_emojis = [emojize(demojize(text[s:e])) for s, e in zip(starts, ends)]

    previous_words = [''] * len(contiguous_emojis)
    following_words = [''] * len(contiguous_emojis)
    for i, (s, e) in enumerate(zip(starts, ends)):
        if s >= 1:
            p = s - 1 if text[s - 1] != ' ' else s - 2
            while text[p] != ' ' and p > 0:
                p -= 1
            previous_words[i] = text[p:s].strip()

        if e < len(text) :
            p = e if text[e] != ' ' else e + 1
            while p < len(text) and text[p] != ' ':
                p += 1
            following_words[i] = text[e:p].strip()

    prev_words = [[] for _ in range(len(unique_emojis))]
    foll_words = [[] for _ in range(len(unique_emojis))]

    for j, (p_words, f_words, c_emoji) in enumerate(zip(previous_words, following_words, contiguous_emojis)):
        for i, u_emoji in enumerate(unique_emojis):
            if demojize(c_emoji) == demojize(u_emoji):
                prev_words[i].append(p_words)
                foll_words[i].append(f_words)

    return {'previous_words': prev_words,
            'following_words': foll_words,
            }


def get_emojis_and_clean_text(ems_loc, text, ignore_skins=True):
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
    skins_pos = [np.array([i for i in range(len(orig_text)) if orig_text.startswith(skin, i)]) for skin in
                 np.unique(skins)]

    if len(skins_pos) > 0:
        skins_pos = np.concatenate(skins_pos)
        skins_pos.sort()
        pos = shift_left_according_to_another_list(pos, skins_pos)

    if ignore_skins:
        for skin in np.unique(skins):
            text = text.replace(skin, "")

    return {'emojis': ems,
            'positions': pos,
            'text': text}


def get_unique_emojis(emojis_list):
    unique_ems, count = np.unique([demojize(e) for e in emojis_list], return_counts=True)
    unique_ems_emojize = [emojize(e) for e in unique_ems]

    return {'unique_emojis': unique_ems_emojize,
            'demojized_unique_emojis': unique_ems,
            'count': count}


def get_word_letter_positions(text, unique_emojis, all_emojis, all_emojis_position):
    # words = text.split()
    # pos_words = [[] for _ in unique_emojis]
    if len(unique_emojis) == 0:
        return {'pos_in_words': [],
                'pos_in_letters': [],
                'n_words': 0}

    pos_letters = [[] for _ in unique_emojis]

    spaces = [m.start() for m in re.finditer(' ', text)] + [len(text)]
    words = {}
    for em in unique_emojis:
        words[demojize(em)] = []

    spaces_pointer = 0
    for i, s in enumerate(all_emojis_position):
        while s > spaces[spaces_pointer] and spaces_pointer < len(spaces) - 1:
            spaces_pointer += 1
        words[demojize(all_emojis[i])].append(spaces_pointer)

    pos_words = [words[demojize(em)] for em in unique_emojis]

    # for w, word in enumerate(words):
    #     for i, em in enumerate(unique_emojis):
    #         for _ in range(demojize(word).count(demojize(em))):
    #             pos_words[i].append(w)

    for j, val in enumerate(unique_emojis):
        for i, em in enumerate(all_emojis):
            if demojize(em) == demojize(val):
                pos_letters[j].append(all_emojis_position[i])

    # Raise error if computation is wrong
    if len(np.concatenate(pos_letters)) != len(np.concatenate(pos_words)):
        raise Exception('Error extracting emojis from: {}'.format(text))

    return {'pos_in_words': pos_words,
            'pos_in_letters': pos_letters,
            'n_words': len(spaces)}

def shift_positions_seq_emojis(starts, sizes, unique_emojis, all_emojis):
    new_positions = shift_left_according_to_another_list(starts,
                                                         starts,
                                                         aux=sizes)

    new_positions_unique = [[] for _ in range(len(unique_emojis))]

    for j, (p, c_emoji) in enumerate(zip(new_positions, all_emojis)):
        for i, u_emoji in enumerate(unique_emojis):
            if demojize(c_emoji) == demojize(u_emoji):
                new_positions_unique[i].append(p)

    # new_positions = shift_left_according_to_another_list(seq_emojis['starts'],
    #                                                      seq_emojis['starts'],
    #                                                      aux=seq_emojis['sizes'])
    #
    # new_positions_unique = [[] for _ in range(len(unique_emojis['unique_emojis']))]
    #
    # for j, (p, c_emoji) in enumerate(zip(new_positions, seq_emojis['seq_emojis'])):
    #     for i, u_emoji in enumerate(unique_emojis['unique_emojis']):
    #         if demojize(c_emoji) == demojize(u_emoji):
    #             new_positions_unique[i].append(p)

    return new_positions_unique


def get_stats_from_emojis(ems_loc, text, static_info=None, ignore_skins=True, sequencial=True):
    clean_text = get_emojis_and_clean_text(ems_loc, text, ignore_skins=ignore_skins)
    if sequencial:
        seq_emojis = sequential_emojis(clean_text['text'], clean_text['emojis'])
        unique_emojis = get_unique_emojis(seq_emojis['seq_emojis'])

        prev_foll_words = prev_follow_words(unique_emojis['unique_emojis'],
                                            clean_text['text'],
                                            seq_emojis['starts'],
                                            seq_emojis['ends'])

        positions = get_word_letter_positions(clean_text['text'],
                                              unique_emojis['unique_emojis'],
                                              seq_emojis['seq_emojis'],
                                              seq_emojis['starts'])

        # new_positions = shift_left_according_to_another_list(seq_emojis['starts'],
        #                                                      seq_emojis['starts'],
        #                                                      aux=seq_emojis['sizes'])
        #
        # new_positions_unique = [[] for _ in range(len(unique_emojis['unique_emojis']))]
        #
        # for j, (p, c_emoji) in enumerate(zip(new_positions, seq_emojis['seq_emojis'])):
        #     for i, u_emoji in enumerate(unique_emojis['unique_emojis']):
        #         if demojize(c_emoji) == demojize(u_emoji):
        #             new_positions_unique[i].append(p)

        positions['pos_in_letters'] = shift_positions_seq_emojis(seq_emojis['starts'],
                                                                 seq_emojis['sizes'],
                                                                 unique_emojis['unique_emojis'],
                                                                 seq_emojis['seq_emojis'])
    else:
        unique_emojis = get_unique_emojis(clean_text['emojis'])
        ends = np.array(clean_text['positions']) + [len(em) for em in clean_text['emojis']]
        prev_foll_words = prev_follow_words(unique_emojis['unique_emojis'],
                                            clean_text['text'],
                                            clean_text['positions'],
                                            ends)

        positions = get_word_letter_positions(clean_text['text'],
                                              unique_emojis['unique_emojis'],
                                              clean_text['emojis'],
                                              clean_text['positions'])

    result = {**clean_text, **unique_emojis, **positions, **prev_foll_words}
    result['all_emojis'], result['emojis'] = result['emojis'], result['unique_emojis']
    result['n_letters'] = len(clean_text['text']) - (sum(seq_emojis['sizes']) if sequencial else 0)
    result['n_emojis'] = len(clean_text['emojis'])

    if static_info is not None:
        for info in static_info:
            result[info] = static_info[info]
    return result


# def get_stats_from_emojis(ems_loc, text, static_info=None, ignore_skins=True, sequencial=False):
#     orig_text = copy(text)
#     pos = [em['location'] for em in ems_loc]
#
#     # Remove skin tone from emojis if needed
#     ems, skins = [], []
#     for em in ems_loc:
#         if 'skin_tone' in demojize(em['emoji']):
#             remove_skin_pos = -1
#             for i, c in enumerate(em['emoji']):
#                 if 'skin_tone' in demojize(c):
#                     remove_skin_pos = i
#                     skins.append(em['emoji'][i])
#
#             if ignore_skins:
#                 emoji_wo_skin_color = em['emoji'][:remove_skin_pos] + em['emoji'][remove_skin_pos + 1:]
#             else:
#                 emoji_wo_skin_color = em['emoji']
#
#             ems.append(emoji_wo_skin_color)
#         else:
#             ems.append(em['emoji'])
#
#     # Process text depending on ignore_skin preference
#     skins_pos = [np.array([i for i in range(len(orig_text)) if orig_text.startswith(skin, i)]) for skin in
#                  np.unique(skins)]
#
#     if len(skins_pos) > 0:
#         skins_pos = np.concatenate(skins_pos)
#         skins_pos.sort()
#         pos = shift_left_according_to_another_list(pos, skins_pos)
#
#     if ignore_skins:
#         for skin in np.unique(skins):
#             text = text.replace(skin, "")
#         n_letters = len(text)
#     else:
#         n_letters = len(text) - len(skins_pos)
#
#     # Count unique emojis
#     unique_ems, count = np.unique([demojize(e) for e in ems], return_counts=True)
#     unique_ems_emojize = [emojize(e) for e in unique_ems]
#
#     contiguous_emojis, previous_words, following_words = prev_follow_words(text, ems)
#
#     # Get list of letter and word positions for each emoji
#     words = text.split()
#     pos_words = [[] for _ in unique_ems]
#     pos_letters = [[] for _ in unique_ems]
#
#     for w, word in enumerate(words):
#         for i, em in enumerate(unique_ems):
#             for _ in range(demojize(word).count(em)):
#                 pos_words[i].append(w)
#
#     for j, val in enumerate(unique_ems):
#         for i, em in enumerate(ems):
#             if demojize(em) == val:
#                 pos_letters[j].append(pos[i])
#
#     # Raise error if computation is wrong
#     if len(np.concatenate(pos_letters)) != len(np.concatenate(pos_words)):
#         raise Exception('Error extracting emojis from: {}'.format(orig_text))
#
#     result = {"text": text,
#               "n_emojis": len(ems),
#               "n_unique_emojis": len(unique_ems),
#               "n_letters": n_letters,
#               "n_words": len(words),
#               "emojis": unique_ems_emojize,
#               "count": count,
#               "pos_in_letters": pos_letters,
#               "pos_in_words": pos_words,
#               "contiguous_emojis": contiguous_emojis,
#               "previous_words": previous_words,
#               "following_words": following_words,
#               }
#
#     if static_info is not None:
#         for info in static_info:
#             result[info] = static_info[info]
#     return result


def get_emojis_stats(chat, max_thold=100, sequential=False):
    # persons_cat = [get_person_categories(person) for person in persons]

    emojis_found = []
    for i in range(chat.shape[0]):
        text = chat.iloc[i, 1]

        if text is not np.nan and len(text) > 0:
            ems = find_emojis(text)

            if len(ems) > 0 and len(ems) <= max_thold:
                static_info = {'line': i,
                               'person': chat.iloc[i, 0]
                               }
                try:
                    stats = get_stats_from_emojis(ems, text, static_info, sequencial=sequential)
                    if len(stats['emojis']) > 0:
                        emojis_found.append(stats)
                except Exception as e:
                    print(e)
                    print('error in line: {}'.format(text))
            # else:
            #     print('excluding line with {} emojis and {} characters'.format(len(ems), len(text)))

    return emojis_found


def get_unique_emoji_stats(emojis_found, file):
    unique_emojis = {}
    for j, em_found in enumerate(emojis_found):
        for i, em in enumerate(em_found['emojis']):
            if (len(em_found['pos_in_letters'][i]) != len(em_found['pos_in_words'][i])) or \
                    (len(em_found['pos_in_letters'][i]) != len(em_found['previous_words'][i])) or \
                    (len(em_found['pos_in_letters'][i]) != len(em_found['following_words'][i])):
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
                                              'n_emojis': [em_found['n_emojis'] for _ in em_found['pos_in_letters'][i]],
                                              'text_': [em_found['text']],
                                              'text': [em_found['text'] for _ in em_found['pos_in_letters'][i]],
                                              'previous_words': em_found['previous_words'][i],
                                              'following_words': em_found['following_words'][i],
                                              'n_letters': [em_found['n_letters'] for _ in
                                                            em_found['pos_in_letters'][i]],
                                              'n_words': [em_found['n_words'] for _ in em_found['pos_in_words'][i]],
                                              'pos_in_letters': em_found['pos_in_letters'][i],
                                              'rel_pos_in_letters': [a / em_found['n_letters'] for a in
                                                                     em_found['pos_in_letters'][i]],
                                              'pos_in_words': em_found['pos_in_words'][i],
                                              'rel_pos_in_words': [a / em_found['n_words'] for a in
                                                                   em_found['pos_in_words'][i]],
                                              })
            else:
                unique_emojis[em]['n_lines'] += 1
                unique_emojis[em]['ix'].append(j)
                unique_emojis[em]['person'].append(em_found['person'])
                unique_emojis[em]['lines'].append(em_found['line'])
                unique_emojis[em]['count'].append(em_found['count'][i])
                unique_emojis[em]['total_count'] += em_found['count'][i]
                [unique_emojis[em]['file'].append(file) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['n_emojis'].append(em_found['n_emojis']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['line_in_chat'].append(em_found['line']) for _ in em_found['pos_in_letters'][i]]
                unique_emojis[em]['text_'].append(em_found['text'])
                [unique_emojis[em]['text'].append(em_found['text']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['previous_words'].append(a) for a in em_found['previous_words'][i]]
                [unique_emojis[em]['following_words'].append(a) for a in em_found['following_words'][i]]
                [unique_emojis[em]['n_letters'].append(em_found['n_letters']) for _ in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['n_words'].append(em_found['n_words']) for _ in em_found['pos_in_words'][i]]
                [unique_emojis[em]['pos_in_letters'].append(a) for a in em_found['pos_in_letters'][i]]
                [unique_emojis[em]['rel_pos_in_letters'].append(a / em_found['n_letters']) for a in
                 em_found['pos_in_letters'][i]]
                [unique_emojis[em]['pos_in_words'].append(a) for a in em_found['pos_in_words'][i]]
                [unique_emojis[em]['rel_pos_in_words'].append(a / em_found['n_words']) for a in
                 em_found['pos_in_words'][i]]

    return unique_emojis


# def get_unique_contiguous_emoji_stats(emojis_found, file):
#     unique_emojis = {}
#     for j, em_found in enumerate(emojis_found):
#         for i, em in enumerate(em_found['contiguous_emojis']):
#             if em not in unique_emojis:
#                 unique_emojis[em] = deepcopy({'n_lines': 1,
#                                               'ix': [j],
#                                               'person': [em_found['person']],
#                                               'count': [1],
#                                               'total_count': 1,
#                                               'file': [file],
#                                               'line_in_chat': [em_found['line']],
#                                               'text': [em_found['text']],
#                                               'n_letters': [em_found['n_letters']],
#                                               'n_words': [em_found['n_words']],
#                                               'previous_words': [em_found['previous_words'][i]],
#                                               'following_words': [em_found['following_words'][i]],
#                                               })
#             else:
#                 unique_emojis[em]['n_lines'] += 1
#                 unique_emojis[em]['ix'].append(j)
#                 unique_emojis[em]['person'].append(em_found['person'])
#                 unique_emojis[em]['count'].append(1)
#                 unique_emojis[em]['total_count'] += 1
#                 unique_emojis[em]['file'].append(file)
#                 unique_emojis[em]['line_in_chat'].append(em_found['line'])
#                 unique_emojis[em]['text'].append(em_found['text'])
#                 unique_emojis[em]['n_letters'].append(em_found['n_letters'])
#                 unique_emojis[em]['n_words'].append(em_found['n_words'])
#                 unique_emojis[em]['previous_words'].append(em_found['previous_words'][i])
#                 unique_emojis[em]['following_words'].append(em_found['following_words'][i])
#
#     return unique_emojis


def merge_and_add_person_feature(feature, results, stat_key='stats'):
    all = [[]]*2
    for i, res in enumerate(results):
        if len(res['unique_emojis']) > 0:
            dfs = [res[stat_key]['count'], pd.concat(res[stat_key]['messages'], axis=0)]
            try:
                for i, df in enumerate(dfs):
                    feature_col = [res['persons'][p][feature] for p in df['person']]
                    df[feature] = feature_col
                    df['file'] = res['filename']
                    all[i].append(df)
            except KeyError as e:
                print('person feature not found in file: {}'.format(res['filename']))

    df_with_feature = pd.concat(all[0], axis=0).sort_values(by='count', ascending=False)
    counts_emoji = df_with_feature.groupby(by=['emoji', feature]).sum().reset_index().sort_values(by='count', ascending=False)

    all_lines = pd.concat(all[1], axis=0)
    return counts_emoji, all_lines

def concat_and_put_person_feature(features, results):
    dfs = [[] for i in range(3)]
    for i, res in enumerate(results):
        for j, df in enumerate([res['chat'], res['lines_with_emojis'], res['chats_wo_media']]):
            if len(df) > 0:
                try:
                    for feature in features:
                        feature_col = [(res['persons'][p][feature] if p in res['persons'] else '')  for p in df['person']]
                        df[feature] = feature_col
                    dfs[j].append(df)
                except KeyError as e:
                    print('person feature not found in file: {}'.format(res['filename']))

    res = [pd.concat(d) for d in dfs]
    return {'chats': res[0], 'all_lines_with_emojis': res[1], 'chat_wo_media': res[2]}


def get_value_counts_lastprev_words(df_ss, emoji_key):
    df_ss['last_character'] = df_ss['previous_words'].str[-1:]
    df_ss['first_character'] = df_ss['following_words'].str[:1]

    last_character_count = df_ss['last_character'].value_counts()
    first_character_count = df_ss['first_character'].value_counts()
    previous_words_count = df_ss['previous_words'].value_counts()
    following_words_count = df_ss['following_words'].value_counts()

    df1 = pd.DataFrame(previous_words_count).rename(columns={'previous_words': 'count1'}).rename_axis(
        'previous_word').reset_index()
    df2 = pd.DataFrame(following_words_count).rename(columns={'following_words': 'count2'}).rename_axis(
        'following_word').reset_index()
    df3 = pd.DataFrame(last_character_count).rename(columns={'last_character': 'count3'}).rename_axis(
        'last_character').reset_index()
    df4 = pd.DataFrame(first_character_count).rename(columns={'first_character': 'count4'}).rename_axis(
        'first_character').reset_index()

    df = df1.join(df2, how='outer').join(df3, how='outer').join(df4, how='outer')
    df['emoji'] = emoji_key
    return df

def filter_media_from_chat(chat):
    chat = chat.loc[chat['conversacion'] != '<Multimedia omitido>', :]
    chat = chat.loc[chat['conversacion'] != 'Video omitido', :]
    chat = chat.loc[chat['conversacion'] != '‎audio omitido', :]
    chat = chat.loc[chat['conversacion'] != '‎imagen omitida', :]

    return chat

def get_general_stats(chat, emojis_found, csv_file):
    chat = chat.copy()
    chat['file'] = csv_file

    n_words = [(len(line.split(' ')) if isinstance(line, str) else 0) for line in chat['conversacion']]
    chat['n_words'] = n_words
    chat['text_wo_e'] = chat['conversacion'].astype(str).apply(remove_emojis_from_text)
    chat['n_words_wo_e'] = chat['text_wo_e'].str.split(' ').str.len()
    chat['n_letters'] = chat['conversacion'].str.len()

    chats_wo_media = filter_media_from_chat(chat)

    if len(emojis_found) == 0:
        return {'chat': chat, 'lines_with_emojis': pd.DataFrame(), 'chats_wo_media': chats_wo_media}

    keys = ['person', 'n_words', 'n_letters', 'line', 'n_emojis']
    cols = {}

    for line in emojis_found:
        for k in keys:
            if k in cols:
                cols[k].append(line[k])
            else:
                cols[k] = [line[k]]

    df = pd.DataFrame()
    for k in keys:
        df[k] = cols[k]
    df['file'] = csv_file


    return {'chat': chat, 'lines_with_emojis': df, 'chats_wo_media': chats_wo_media}

def remove_emojis_from_text(text):
    return emoji.get_emoji_regexp().sub('', text).strip()
