import numpy as np

def get_language(df, translator):
    ixs = np.random.randint(0, df.shape[0], size=10)
    random_lines = [df.iloc[ix, 1] for ix in ixs]

    langs = []
    for line in random_lines:
        try:
            lan = translator.detect(line).lang
            if not isinstance(lan, list):
                langs.append(translator.detect(line).lang)
        except:
            pass

    vals, count = np.unique(langs, return_counts=True)
    return vals[count.argmax()]