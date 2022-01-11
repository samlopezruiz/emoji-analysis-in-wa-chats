from googletrans import Translator

if __name__ == '__main__':
    translator = Translator()
    line = 'frase de prueba'
    lan = translator.detect(line)
    print(lan.lang)