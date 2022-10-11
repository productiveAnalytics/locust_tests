from datetime import datetime
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    def __init__(self, env):
        super().__init__(env)
        self.user_timestamp = datetime.utcnow().isoformat(sep=' ', timespec='microseconds')

    def on_start(self):
        print(f'START: locust test: {self.user_timestamp}')

    def on_stop(self):
        print(f'FINISH: locust test: {self.user_timestamp}')

    @task
    def test_index(self):
        self.client.get("/")

    @task
    def test_time(self):
        self.client.get("/time")

    # will have weightage of 2
    @task(2)
    def test_hello_time(self):
        self.client.get("/time/prod8ctive")