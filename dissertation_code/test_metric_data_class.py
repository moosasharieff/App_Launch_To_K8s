import unittest

from metric_data_class import MetricsCollector
from bs4 import BeautifulSoup
import requests
import json


class TestMetricsCollector(unittest.TestCase):
    """This class will test various methods in
    cls: MetricsCollector"""
    METRICS_URL = "http://localhost:8001/apis/metrics.k8s.io/v1beta1/namespaces/my-app-namespace/pods"

    def test_get_metrics(self):
        # Initiation
        mc = MetricsCollector(self.METRICS_URL)
        metrics = mc.get_metrics()

        # Assertions
        self.assertEqual(type(metrics), list)
        self.assertEqual(metrics[0]['metadata']['namespace'], 'my-app-namespace')



if __name__ == '__main__':
    unittest.main()
