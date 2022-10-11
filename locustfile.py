from datetime import datetime
from locust import HttpUser, task, between, run_single_user

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    # for DEBUG purpose only, prefer to pass using --host
    host = "http://localhost:5000"

    def __init__(self, env):
        super().__init__(env)
        self.user_timestamp = datetime.utcnow().isoformat(sep=' ', timespec='microseconds')

    def on_start(self):
        print(f'START: locust test: {self.user_timestamp}')

    def on_stop(self):
        print(f'FINISH: locust test: {self.user_timestamp}')

    @task
    def test_index(self):
        with self.client.get("/", catch_response=True) as resp:
            pass # maybe set a breakpoint here to analyze the resp object?

    @task
    def test_time(self):
        with self.client.get("/time", catch_response=True) as resp:
            pass # maybe set a breakpoint here to analyze the resp object?

    # will have weightage of 2
    @task(2)
    def test_hello_time(self):
        with self.client.get("/time/prod8ctive", catch_response=True) as resp:
            pass # maybe set a breakpoint here to analyze the resp object?


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(QuickstartUser)