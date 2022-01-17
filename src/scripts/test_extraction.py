from copy import copy

import numpy as np
from emoji import demojize, emojize

from src.scripts.utils.nlp import get_stats_from_emojis, find_emojis
from src.scripts.utils.util import shift_left_according_to_another_list

if __name__ == '__main__':
    #%%
    # text = '🖕🏿🖕🏿🖕🏿'
    text = '👇👇🏻 👇👇🏻👇🏿🖕🏿🖕🏿'
    # text = 'Me gusta traerte loco, así como tu a mí y lo sabes porque ver notaaaa ❤ que me traes loca sacas lo romantico en mí, escuchó música y lo primero que se me viene a la mente eres tú! Y más cosas.❤️❣️🤤'
    # text = 'Mientras no este ☠ aún puedo 👩‍❤‍💋‍👩'
    # text = 'How to print 😁😁😛😋🤣emojis 🖕🏿🖕🏿🖕🏿 using python🐍 😁😛🖕🏿😋'
    # text = 'Te quiero recuérdalo mucho!💗🕵🏻‍♀'
    # text = 'Te amo más 👯🏻‍♀💜'

    ems_loc = find_emojis(text)
    ignore_skins = False
    res = get_stats_from_emojis(ems_loc, text, ignore_skins=ignore_skins)

    print(res['text'])
    print(res['n_letters'])
    print(res['n_words'])
    print(res['emojis'])
    print(res['count'])
    print(res['pos_in_words'])
    print(res['pos_in_letters'])