
import pandas as pd
import numpy as np
import os


def pretty_process_text(in_path, out_path):
    
    a_file = open(in_path, "r", encoding="utf8")
    
    lines = a_file.read()
    list_of_lists = lines.splitlines()
    a_file.close()
    
    personA = list_of_lists[0]
    personB = list_of_lists[1]
    persons = list_of_lists[:2]
    
    conversation = list_of_lists[2:]
    
    person = []
    conv = []
    
    
    for line in conversation:
        if personA in line:
            person.append('A')
        elif personB in line:
            person.append('B')
        else:
            person.append(np.nan)
        
        if ')):' not in line:
            conv.append(line.strip())
        elif len(line) > 0:
            conv.append(line.split(')):')[1].strip())
        else:
            conv.append('')
            
    
    header = pd.DataFrame()
    header['person'] = ['A', 'B', '-']
    header['conversacion'] = persons + ['---------']
    
    df = pd.DataFrame()
    df['person'] = person
    df['conversacion'] = conv
    df.ffill(axis=0, inplace=True)
    
    df = pd.concat([header, df]).reset_index(drop=True)
    
    df.to_csv(out_path, encoding='utf-8-sig')
    

if __name__ == '__main__':
    in_folder = os.path.join('..', 'data', 'txt')
    out_folder = os.path.join('..', 'data', 'csv')
    
    os.makedirs(out_folder, exist_ok=True)
    
    
    text_files = os.listdir(in_folder)
    
    for file in text_files:
        
        in_path = os.path.join(in_folder, file)
        out_path = os.path.join(out_folder, "{}.csv".format(file.split('.')[0]))
    
        pretty_process_text(in_path, out_path)
