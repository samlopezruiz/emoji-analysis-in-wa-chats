import os
from shutil import copyfile
from googletrans import Translator
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_language

if __name__ == '__main__':
    translator = Translator()
    data_folder = os.path.join('..', 'data', 'csv')
    es_folder = os.path.join('..', 'data', 'es')

    os.makedirs(es_folder, exist_ok=True)

    csv_files = os.listdir(data_folder)

    for i, csv_file in enumerate(csv_files):
        # print('{}% done'.format(round(100*(i+1)/len(csv_files), 2)), end='\r')
        file_path = os.path.join(data_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)

        lan = get_language(chat, translator)
        print('{}: {}'.format(i, lan))
        if chat.shape[0] > 50 and lan == 'es':
            copyfile(file_path, os.path.join(es_folder, csv_file))