def sort_dict_by_key(sort_key, dict_to_sort, key_name='emoji', reverse=True):
    new_list = []
    for key, val in dict_to_sort.items():
        val[key_name] = key
        new_list.append(val)

    new_list.sort(key=lambda x: x[sort_key], reverse=reverse)
    return new_list