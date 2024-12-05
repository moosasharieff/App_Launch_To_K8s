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
