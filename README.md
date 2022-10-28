# Locust based load testing for RESTful app

## Setup environment
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade virtualenv
python3 -m virtualenv .venv
```
Activate virtual env: ```source .venv/bin/activate```
Install dependencies: ```python3 -m pip install -r requirements.txt```
Confirm locust: ```python3 -m locust --help```

## Start the test server
Run Flask-based server at http://localhost:5000

```python3 -m flask --app hello_timestamp.py --debug run```

Refer: https://github.com/productiveAnalytics/flask-py-sandbox/tree/feature/another_RESTful_flask_app/another_RESTFful_flask_app

## Start locust
```python3 -m locust --host http://localhost:5000 --locustfile locustfile.py```
```python3 -m locust --host https://eastus-1.azure.cloud2.influxdata.com --locustfile influxdb_locustfiles/locust_query_simple.py```

Visit locust UI at http://localhost:8089

Choose the number of users (e.g. 10) and spawn rate (e.g. 1 user per second)