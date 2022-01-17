import numpy as np


def sort_dict_by_key(sort_key, dict_to_sort, key_name='emoji', reverse=True):
    new_list = []
    for key, val in dict_to_sort.items():
        val[key_name] = key
        new_list.append(val)

    new_list.sort(key=lambda x: x[sort_key], reverse=reverse)
    return new_list

def shift_left_according_to_another_list(list_to_shift, indexes):
    shifted_list = np.copy(list_to_shift)
    secondary_list_counter = 0
    current_shift = 0
    for i in range(len(list_to_shift)):
        if shifted_list[i] > indexes[secondary_list_counter]:
            current_shift += 1
            if secondary_list_counter < len(indexes):
                secondary_list_counter += 1

        shifted_list[i] -= current_shift
    return shifted_list