from datetime import datetime
from random import randint

from locust import HttpUser, task, between, run_single_user
from locust.env import Environment

from constants import INFLUXDB_TOKEN

class Simple_Query_API_User(HttpUser):
    wait_time = between(1, 5)

    # for DEBUG/TEST only, pass via --host for actual load test
    host:str = 'https://eastus-1.azure.cloud2.influxdata.com'

    url:str = '/api/v2/query'

    def __init__(self, env:Environment):
        super().__init__(env)
        self.user_timestamp = datetime.utcnow().isoformat(sep=' ', timespec='microseconds')
        
        self.headers = {
            "Authorization": f"Token {INFLUXDB_TOKEN}",
            "Accept": "application/csv",
            "Content-type": "application/vnd.flux"
        }

    def on_start(self):
        print(f'START: QEURY locust test: {self.user_timestamp}')

    def on_stop(self):
        print(f'FINISH: QEURY locust test: {self.user_timestamp}')

    @task
    def test_index(self):
        random_days_range:int = randint(1, 3000)
        flux_qry = """from(bucket: "dfl_MICROGRID_seriesEntry") 
        |> range(start: -{days_range}d)
        |> count()
        """.format(days_range=random_days_range)

        with self.client.post(url=self.url, headers=self.headers, data=flux_qry, catch_response=True) as resp:
            print(f'Query: {flux_qry} \nResponse status code: {resp.status_code}')


if __name__ == "__main__":
    run_single_user(Simple_Query_API_User)