"""
This file will contains code which will store and fetch
metrics data from exposed Metrics Service API of Kubernetes
cluster.
"""

from bs4 import BeautifulSoup
import requests
import json


class Metric_Data:
    """This class will store below information
    of the Pods."""
    NAME = set()
    CPU = {}
    MEMORY = {}
    DATETIME = {}
    DATATIME_LIST = {}


class MetricsCollector(Metric_Data):
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
