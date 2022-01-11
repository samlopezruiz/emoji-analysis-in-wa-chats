import os
from shutil import copyfile
from src.scripts.utils.files import read_chat
from src.scripts.utils.nlp import get_language
from google.cloud import translate_v2 as translate
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\\MEGA\\Proyectos\\Moni LV\\Tesis\\nlp-chats-8004be07cbd4.json'

if __name__ == '__main__':
    translate_client = translate.Client()
    data_folder = os.path.join('..', 'data', 'csv')
    es_folder = os.path.join('..', 'data', 'es')

    os.makedirs(es_folder, exist_ok=True)

    csv_files = os.listdir(data_folder)

    es_count = 0
    for i, csv_file in enumerate(csv_files):
        print('{}%, es files: {}'.format(round(100*(i+1)/len(csv_files), 2), es_count), end='\r')
        file_path = os.path.join(data_folder, csv_file)

        person_A, person_B, chat = read_chat(file_path)

        lan = get_language(chat, translate_client)

        if isinstance(lan, list):
            lan = lan[0]

        if chat.shape[0] > 50 and lan == 'es':
            es_count += 1
            copyfile(file_path, os.path.join(es_folder, csv_file))