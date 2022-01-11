import numpy as np

def get_language(df, translate_client):
    ixs = np.random.randint(0, df.shape[0], size=10)
    random_lines = [df.iloc[ix, 1] for ix in ixs]

    langs = []
    for line in random_lines:
        try:
            lan = detect_language(line, translate_client)
            if not isinstance(lan['language'], list):
                langs.append(lan['language'])
        except:
            pass

    vals, count = np.unique(langs, return_counts=True)
    return vals[count.argmax()]


def detect_language(text, translate_client):
    """Detects the text's language."""
    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)

    return result