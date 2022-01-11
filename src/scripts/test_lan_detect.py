import os

from src.scripts.utils.nlp import detect_language

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\\MEGA\\Proyectos\\Moni LV\\Tesis\\nlp-chats-8004be07cbd4.json'

if __name__ == '__main__':
    line = 'frase de prueba'

    lan2 = detect_language(line)
    print(lan2['language'])
