import numpy as np
import pandas as pd
# import pretty_errors
from emoji import demojize, emojize
from src.scripts.utils.nlp import get_stats_from_emojis, find_emojis, get_emojis_and_clean_text, \
    get_unique_emojis, get_word_letter_positions, sequential_emojis, prev_follow_words, remove_emojis_from_text
from src.scripts.utils.util import shift_left_according_to_another_list

if __name__ == '__main__':
    #%%

    # text = 'ππΏππΏππΏ'
    text = 'ππ πππ»mano πππ»ππΏππΏππΏ otro textππ'
    text = 'πππ'
    text_wo_emojis = remove_emojis_from_text(text)
    print(text_wo_emojis)
    print(len(text_wo_emojis))

    # text = 'π€¦π½ββπ no manches que mal viaje'
    # text = 'β€β€β€β€'
    # text = 'π\u200dβοΈ'
    # text = 'πͺπΎπͺπΎπͺπΎππΎππ»'
    # text = 'π«π«π«π«'
    # text = 'π Siii'
    # text = 'β€β€β€β€'
    # text = 'Me gusta traerte loco, asΓ­ como tu a mΓ­ y lo sabes porque ver notaaaa β€ que me traes loca sacas lo romantico en mΓ­, escuchΓ³ mΓΊsica y lo primero que se me viene a la mente eres tΓΊ! Y mΓ‘s cosas.β€οΈβ£οΈπ€€'
    # text = 'Mientras no este β  aΓΊn puedo π©ββ€βπβπ©'
    # text = 'How to print πππππ€£emojis ππΏππΏππΏ using pythonπ ππππΏπ'
    # text = 'Te quiero recuΓ©rdalo mucho!ππ΅π»ββ'
    # text = 'Te amo mΓ‘s π―π»ββπ'

    ems_loc = find_emojis(text)
    res = get_stats_from_emojis(ems_loc,
                                text,
                                ignore_skins=True,
                                sequencial=True)


    print('text:', res['text'])
    print('n_letters:', res['n_letters'])
    print('n_words:', res['n_words'])
    print('emojis:', res['emojis'])
    print('count:', res['count'])
    print('pos_in_words:', res['pos_in_words'])
    print('pos_in_letters:', res['pos_in_letters'])
    print('previous_words:', res['previous_words'])
    print('following_words:', res['following_words'])

    ems_loc = find_emojis(text)
    res = get_stats_from_emojis(ems_loc,
                                text,
                                ignore_skins=True,
                                sequencial=False)
    print('-'*20)
    print('text:', res['text'])
    print('n_letters:', res['n_letters'])
    print('n_words:', res['n_words'])
    print('emojis:', res['emojis'])
    print('count:', res['count'])
    print('pos_in_words:', res['pos_in_words'])
    print('pos_in_letters:', res['pos_in_letters'])
    print('previous_words:', res['previous_words'])
    print('following_words:', res['following_words'])

