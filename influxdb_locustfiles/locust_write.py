import sys
import time
from datetime import datetime
from locust import HttpUser, task, between, constant, run_single_user
from locust.env import Environment

from constants import INFLUXDB_TOKEN, RETRY_TIME_IN_SECONDS
from data_generator import read_data

DATALOAD_BATCH_SIZE:int=125000

class Write_API_User(HttpUser):
    # wait_time = between(min_wait=1, max_wait=3)
    # wait_time = constant(wait_time=2)
    wait_time = constant(wait_time=60)

    # for DEBUG/TEST only, pass via --host for actual load test
    host = 'https://eastus-1.azure.cloud2.influxdata.com'

    all_data_dict:dict = None

    @staticmethod
    def get_data_size(data_string:str) -> int:
        enc_str:bytes = data_string.encode(encoding='UTF-8')
        
        # memory_in_bytes:int = enc_str.__size__()
        memory_in_bytes:int = sys.getsizeof(enc_str)

        length_in_bytes:int = len(enc_str)

        return length_in_bytes

    @classmethod
    def load_data(cls, data_dict:dict):
        if (data_dict and len(data_dict) > 0):
            cls.all_data_dict = data_dict

    def __init__(self, env:Environment):
        super().__init__(env)
        self.user_timestamp = datetime.utcnow().isoformat(sep=' ', timespec='microseconds')

        # build the URL using bucket
        self.url = '/api/v2/write?bucket=dfl_MICROGRID_seriesEntry&precision=ms'

        self.headers = {
            "Authorization": f"Token {INFLUXDB_TOKEN}",
            "Accept": "application/csv",
            "Content-type": "application/vnd.flux"
        }

        self._start_index = 0
        self._end_index = 0

        self.retry_after = RETRY_TIME_IN_SECONDS

        self.exec_counter = 0


    def _update_range(self, start_position:int, end_position:int) -> None:
        total_data_size = len(self.all_data_dict)
        LOWER_BOUND:int = 0
        UPPER_BOUND:int = total_data_size - 1

        def _confirm_within_range(position:int) -> int:
            if position < 0:
                return LOWER_BOUND
            elif position >= total_data_size:
                return UPPER_BOUND
            else:
                return position

        self._start_index   = _confirm_within_range(start_position)
        self._end_index     = _confirm_within_range(end_position)


    def _pause(self, expo_backoff_on:bool=False) -> None:
        if expo_backoff_on:
            expo_backoff_retry_time = 2 * self.retry_after
            self.retry_after = expo_backoff_retry_time

        time.sleep(self.retry_after)
        print('[{exec_id}] INGEST WAIT: {retry_delay}'.format(exec_id=self._get_execution_id(), retry_delay=self.retry_after))


    def _setup_next(self, mode:str='cumulative') -> None:
        new_start:int = self._start_index
        new_end:int = self._end_index

        if mode in {'cumulative', 'slide'}:
            new_end:int = self._end_index + DATALOAD_BATCH_SIZE
            
            if mode == 'slide':
                new_start = self._end_index
        else:
            # "same" data range
            pass

        self._update_range(start_position=new_start, end_position=new_end)


    # TODO: catch error if the range moves outside the dataset
    def _get_data(self) -> list:
        data_set_range:range = range(self._start_index, self._end_index)
        test_data_list:list = [self.all_data_dict[index_key] for index_key in data_set_range]

        # single_record:str = 'raw,provider=emas,object=site,siteId=intencityExternal acquisitionDate="2022-08-01T00:00:11.000+00:00",receptionDate="2022-08-01T00:00:14.634+00:00",lastAcquisitionDate="2022-08-31T00:00:01Z" 1659312011000'
        # test_data_list = [ single_record ]

        # from pprint import pprint
        # pprint(test_data_list)

        return test_data_list

    def _get_execution_id(self) -> str:
        return '{runner_name}#{run_count:03d}'.format(runner_name=self.user_timestamp, run_count=self.exec_counter)


    def on_start(self):
        if (not self.all_data_dict):
            all_data_as_dict:dict = read_data(file_path='data/extract-intencity.txt')
            self.load_data(data_dict=all_data_as_dict)
            print(f'DATA_LOAD: By locust test: {self.user_timestamp}')

            offset_position:int = 0
            # offset_position = 1000000

            batch_start_index:int = offset_position
            batch_end_index:int = DATALOAD_BATCH_SIZE
            batch_end_index = (batch_start_index + DATALOAD_BATCH_SIZE)

            # start with one record data set
            # self._update_range(start_position=0, end_position=1)
            self._update_range(start_position=batch_start_index, end_position=batch_end_index)

        print(f'START: Ingest locust test: {self.user_timestamp}')

    def on_stop(self):
        print(f'FINISH: Ingest locust test: {self.user_timestamp}')


    @task
    def test_index(self):
        self.exec_counter += 1 

        exec_id:str = self._get_execution_id()

        load_test_data_list:list = self._get_data()

        print(f'[{exec_id}] INGEST data size={len(load_test_data_list)}')
        load_test_data:str = "\n".join(load_test_data_list)

        load_data_size_in_bytes:int = Write_API_User.get_data_size(data_string=load_test_data)

        with self.client.post(url=self.url, headers=self.headers, data=load_test_data, catch_response=True) as resp:
            status_cd = resp.status_code
            print(f'[{exec_id}] INGEST Response status code: {status_cd} for data load (bytes): {load_data_size_in_bytes}')

            if status_cd == 401:
                print(f'[{exec_id}] INGEST 401-TOKEN EXPIRED! Quitting!')
                self.environment.runner.quit()
            else:
                print(f'[{exec_id}] INGEST Response: {resp}')

                if status_cd == 429:
                    # retry after sleep
                    self._pause(expo_backoff_on=True)
                    pass
                else:
                    # Be ready for next round

                    #self._setup_next(mode='same')
                    #self._setup_next(mode='cumulative')
                    self._setup_next(mode='slide')
                    
                    self.retry_after = RETRY_TIME_IN_SECONDS
                


if __name__ == "__main__":
    run_single_user(Write_API_User)