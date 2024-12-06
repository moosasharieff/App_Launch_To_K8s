"""
This file will contains code which will store and fetch
metrics data from exposed Metrics Service API of Kubernetes
cluster.
"""

from bs4 import BeautifulSoup
import requests
import json
import pytz
from datetime import datetime

from custom_exceptions import AlreadyExistsError


class Metric_Data:
    """This class will store below information
    of the Pods."""
    NAME = set()
    CPU = {}
    DATETIME = {}
    DATETIME_LIST = []

    def append_datetime_list(self, dt):
        val = self._convert_dub_datetime(dt)
        self.DATETIME_LIST.append(val)
        self.DATETIME_LIST.sort()

    def _convert_dub_datetime(self, dt):
        utc_time = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')
        utc_zone = pytz.utc
        utc_time = utc_zone.localize(utc_time)
        dublin_zone = pytz.timezone('Europe/Dublin')
        dublin_time = utc_time.astimezone(dublin_zone)
        return dublin_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')


class Metrics_Collector(Metric_Data):
    """This class collects various information from
    the exposed Metrics Service of Kubernetes cluster."""

    def __init__(self, metrics_url):
        super().__init__()
        self.metrics_url = metrics_url

    def get_metrics(self) -> json:
        response = requests.get(self.metrics_url)
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        json_response = json.loads(soup.text)

        return json_response['items']


class Pod_CPU_Collector(Metric_Data):
    """This method communicates with Metrics Service URL
    and Inherited cls: Metric_Data to store values."""

    def __init__(self):
        super().__init__()

    def extract(self, metrics: json) -> int:
        """Collects all the CPU Metrics of the pods from the provided
        json response."""

        n = len(metrics)
        values = []

        for i in range(n):
            pod_metrics = metrics[i]
            name = pod_metrics['metadata']['name']
            cpu = pod_metrics['containers'][0]['usage']['cpu']

            values.append((name, cpu))

        return values

    def get(self, pod_name: str) -> str:
        """Return CPU value for the pod name else raise KeyError."""
        if pod_name not in self.CPU:
            raise KeyError(f"Pod name '{pod_name}' not found in CPU Storage.")
        return self.CPU.get(pod_name)

    def add(self, pod_name: str, cpu_val: int) -> None:
        """Add the collected pod name and cpu value to
        cls: Metric_Data()
        """
        self.CPU[pod_name] = cpu_val

    def remove(self, pod_name: str) -> None:
        self.CPU.pop(pod_name)


class Pod_NAME_Collector(Metric_Data):
    """This method communicates with Metrics Service URL
        and Inherited cls: Metric_Data to store values."""

    def __init__(self):
        super().__init__()

    def extract(self, metrics: json) -> int:
        """Collects all the Name value from Metrics of the pods from the provided
        json response."""

        n = len(metrics)
        values = []

        for i in range(n):
            pod_metrics = metrics[i]
            name = pod_metrics['metadata']['name']

            values.append(name)

        return values

    def add(self, pod_name) -> None:
        """Adds Pod names in memory"""
        # raise AlreadyExistsError(f"{pod_name} is already present in collection.")
        if pod_name in self.NAME:
            raise AlreadyExistsError('')
        self.NAME.add(pod_name)

    def is_present(self, pod_name: str) -> bool:
        """Checks Pod name and confirms if they are
        present in memory or not."""
        return pod_name in self.NAME

    def remove(self, pod_name: str) -> None:
        """Removes pods name from collection."""
        return self.NAME.remove(pod_name)
