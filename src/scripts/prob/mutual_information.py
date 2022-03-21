# def mi_counts(df):
# from math import log2

import numpy as np
import pandas as pd
from numpy import log2
from sklearn.metrics import mutual_info_score


def mutual_information_from_counts(arr):
    n = np.sum(arr)
    n_f = np.sum(arr, axis=1)
    n_c = np.sum(arr, axis=0)
    mi = arr[0][0] / n * log2((n * arr[0][0]) / (n_f[0] * n_c[0]))
    mi += arr[1][0] / n * log2((n * arr[1][0]) / (n_f[1] * n_c[0]))
    mi += arr[0][1] / n * log2((n * arr[0][1]) / (n_f[0] * n_c[1]))
    mi += arr[1][1] / n * log2((n * arr[1][1]) / (n_f[1] * n_c[1]))
    return mi

if __name__ == "__main__":
    #%%
    df = pd.DataFrame(data=np.array([[49, 27652], [141, 774106]]), columns=['c=1', 'c=0']).astype(np.float64)
    df.index = ['f=1', 'f=0']

    arr = df.to_numpy()

    print(mutual_information_from_counts(arr))
    # print(mutual_info_score(labels_true=None, labels_pred=None, contingency=arr))