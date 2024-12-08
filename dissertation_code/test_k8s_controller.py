import unittest
from unittest import skip
from kubernetes import client

from k8s_controller import K8s_Controller
from metric_data_class import (Metrics_Collector,
                               Pod_NAME_Collector)


class Test_K8s_Controller(unittest.TestCase,
                          K8s_Controller,
                          Metrics_Collector,
                          Pod_NAME_Collector):
    """
    This Test class will test all the methods
    in the cls: K8s_Controller.
    """

    CPU = '50m'
    REPLICA_COUNT = 1

    def setUp(self):
        """
        This class will have all the methods to scale Pods.

        :param replica_count: len(Pod_CPU_Collector.get_cpu())
        API Docs: https://github.com/kubernetes-client/python
        """
        # API Clients
        # Manage resources
        self.core_v1 = client.CoreV1Api()
        # Manage Deployments
        self.apps_v1 = client.AppsV1Api()

        # Get Metrics from Metrics Server
        metrics_url = ("http://localhost:8001/apis/metrics.k8s.io/v1beta1/"
                       "namespaces/my-app-namespace/pods")
        mc = Metrics_Collector(metrics_url)
        metrics = mc.get_metrics()

        # Get controllers
        self.pod_name_collector = Pod_NAME_Collector(metrics)
        self.k8s_controller = K8s_Controller()

    def test_get_namespace(self):
        """
        :return: namespace of the pod.
        """
        # Initiation
        pod_names = self.pod_name_collector.get_all()
        pod_names = list(pod_names)

        # Test
        namespace = self.k8s_controller.get_namespace(pod_names[0])

        # Assertions
        self.assertEqual(namespace, 'my-app-namespace')

    @skip('Implement later')
    def test_get_label(self):
        pass

    @skip('Implement later')
    def test_deploy_pod(self):
        pass


if __name__ == '__main__':
    unittest.main()
