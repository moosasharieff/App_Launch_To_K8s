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
    CREATION_DATETIME = {}

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
        """
        Return CPU value for the pod name else raise KeyError.
        :param pod_name: Name of the pod.
        :return: consumed microsecond core value of CPU for a Pod
        """
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

    def __init__(self, metrics):
        """
        Initiate cls: Metrics_Collector() to get json_response
        of the pod metrics.

        :param metrics: JSON response of Pod's metrics.
        """
        super().__init__()
        self._extract(metrics)

    def _extract(self, metrics: json) -> bool:
        """
        Collects all the Name value from Metrics of the pods
        from the provided json response.

        :param metrics: Namespace URL of the Metrics Server
        :return:
        """

        n = len(metrics)
        count = 0

        for i in range(n):
            pod_metrics = metrics[i]
            name = pod_metrics['metadata']['name']

            count += 1
            self.NAME.add(name)

        return n == count

    def get_all(self) -> set:
        """
        :return: Set of all pod names
        """
        return self.NAME

    def no_of_pods(self) -> int:
        """
        :return: No of pods
        """
        return len(self.NAME)

    def is_present(self, pod_name: str) -> bool:
        """Checks Pod name and confirms if they are
        present in memory or not."""
        return pod_name in self.NAME

    def remove(self, pod_name: str) -> None:
        """Removes pods name from collection."""
        return self.NAME.remove(pod_name)


class Pod_Datetime_Collector(Metric_Data):
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
            pod_metrics = metrics[i]['metadata']
            name = pod_metrics['name']
            dt = pod_metrics['creationTimestamp']

            values.append((name, dt))

        return values

    def add(self, pod_name: str, pod_creation_dt: str) -> None:
        """Adds Pod names in memory"""
        if pod_name in self.CREATION_DATETIME:
            raise AlreadyExistsError(f"{pod_name} already exists "
                                     f"in self.CREATION_DATETIME collection.")
        self.CREATION_DATETIME[pod_name] = pod_creation_dt

    def get(self, pod_name: str) -> str:
        """Return datetime value from self.CREATION_DATETIME"""
        return self.CREATION_DATETIME.get(pod_name)

    def is_present(self, pod_name: str) -> bool:
        """Checks Pod name in self.CREATION_DATETIME and return bool."""
        return pod_name in self.CREATION_DATETIME

    def remove(self, pod_name: str) -> None:
        """Removes pods name from collection."""
        self.CREATION_DATETIME.pop(pod_name)
