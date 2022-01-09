from textblob import TextBlob
import numpy as np

def get_language(df):
    ixs = np.random.randint(0, df.shape[0], size=20)
    random_lines = [df.iloc[ix, 1] for ix in ixs]

    langs = []
    for line in random_lines:
        try:
            langs.append(TextBlob(str(line)).detect_language())
        except:
            pass

    vals, count = np.unique(langs, return_counts=True)
    return vals[count.argmax()]