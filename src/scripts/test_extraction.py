import numpy as np
import pandas as pd
# import pretty_errors
from emoji import demojize, emojize
from src.scripts.utils.nlp import get_stats_from_emojis, find_emojis, get_emojis_and_clean_text, \
    get_unique_emojis, get_word_letter_positions, sequential_emojis, prev_follow_words, remove_emojis_from_text
from src.scripts.utils.util import shift_left_according_to_another_list

if __name__ == '__main__':
    #%%

    # text = '🖕🏿🖕🏿🖕🏿'
    text = '😁😁 👇👇🏻mano 👇👇🏻👇🏿🖕🏿🖕🏿 otro text😁😁'
    text = '😔😔😔'
    text_wo_emojis = remove_emojis_from_text(text)
    print(text_wo_emojis)
    print(len(text_wo_emojis))

    # text = '🤦🏽‍♀😅 no manches que mal viaje'
    # text = '❤❤❤❤'
    # text = '🙋\u200d♂️'
    # text = '💪🏾💪🏾💪🏾👌🏾💅🏻'
    # text = '😫😫😫😫'
    # text = '😅 Siii'
    # text = '❤❤❤❤'
    # text = 'Me gusta traerte loco, así como tu a mí y lo sabes porque ver notaaaa ❤ que me traes loca sacas lo romantico en mí, escuchó música y lo primero que se me viene a la mente eres tú! Y más cosas.❤️❣️🤤'
    # text = 'Mientras no este ☠ aún puedo 👩‍❤‍💋‍👩'
    # text = 'How to print 😁😁😛😋🤣emojis 🖕🏿🖕🏿🖕🏿 using python🐍 😁😛🖕🏿😋'
    # text = 'Te quiero recuérdalo mucho!💗🕵🏻‍♀'
    # text = 'Te amo más 👯🏻‍♀💜'

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

