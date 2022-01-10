from textblob import TextBlob

def detect_language(text):
    """Detects the text's language."""
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)

    print("Text: {}".format(text))
    print("Confidence: {}".format(result["confidence"]))
    print("Language: {}".format(result["language"]))

from googletrans import Translator

if __name__ == '__main__':
    translator = Translator()
    line = 'frase de prueba'
    # print(detect_language(line))
    lan = translator.detect(line).lang
    # print(translator.detect(line))
    # print(TextBlob(str(line)).detect_language())