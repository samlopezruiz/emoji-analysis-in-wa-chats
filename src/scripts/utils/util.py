import numpy as np
from tabulate import tabulate


def sort_dict_by_key(sort_key, dict_to_sort, key_name='emoji', reverse=True):
    new_list = []
    for key, val in dict_to_sort.items():
        val[key_name] = key
        new_list.append(val)

    new_list.sort(key=lambda x: x[sort_key], reverse=reverse)
    return new_list

def shift_left_according_to_another_list(list_to_shift, indexes, aux=None):
    shifted_list = np.copy(list_to_shift)
    secondary_list_counter = 0
    current_shift = 0
    for i in range(len(list_to_shift)):
        if secondary_list_counter < len(indexes) and shifted_list[i] > indexes[secondary_list_counter]:
            current_shift += 1 if aux is None else aux[secondary_list_counter]
            secondary_list_counter += 1

        shifted_list[i] -= current_shift
    return shifted_list


def tabulate_dict(d, float_precisions=None, totals=False):
    headers = list(d[list(d)[0]].keys())
    if float_precisions is not None:
        fmts = [None] + [f",.{f}f" for f in float_precisions]
    else:
        fmts = 'g'

    rows = [[name, *inner.values()] for name, inner in d.items()]
    if totals:
        rows.append([''] + list(np.sum(np.array(rows)[:, 1:].astype(float), axis=0)))
    return tabulate(rows,
                    headers=headers,
                    tablefmt='psql',
                    floatfmt=fmts,
                    stralign="right")