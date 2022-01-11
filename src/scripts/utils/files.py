import pandas as pd


def read_chat(file_path):
    df = pd.read_csv(file_path, index_col=0)

    person_A = df.iloc[0, 1]
    person_B = df.iloc[1, 1]

    chat = df.iloc[3:, :]
    return person_A, person_B, chat
