#! /usr/bin/env python3

from os import path
import time

DATA_FILE = './data/extract-intencity.txt'

def read_data(file_path:str) -> dict:

    def clean_record(line_record:str) -> str:
        return line_record.strip()

    data_dict:dict = dict()

    record_index:int = 0
    line:str = None
    with open(file_path, mode='r') as data_file:
        
        line = clean_record(data_file.readline())
        while (line):
            if (len(line) > 0):
                data_dict[record_index] = line
            else:
                print(f'Skipped empty record at {record_index}')

            record_index += 1
            line = clean_record(data_file.readline())

    return data_dict


if __name__ == '__main__':
    if path.exists(DATA_FILE) and path.isfile(DATA_FILE):
        start_time = time.time()
        data_as_dict:dict = read_data(file_path=DATA_FILE)
        end_time = time.time()

        # from pprint import pprint
        # pprint(data_as_dict)

        # Stats
        print('Total file recrods   = {total_records_cound}'.format(total_records_cound=len(data_as_dict)))
        print('Total file read time = {time_diff}'.format(time_diff=(end_time-start_time)))
    else:
        print(f'ERROR reading file: {DATA_FILE}')
