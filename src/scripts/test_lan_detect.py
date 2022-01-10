from textblob import TextBlob


if __name__ == '__main__':
    line = 'frase de prueba'
    print(TextBlob(str(line)).detect_language())