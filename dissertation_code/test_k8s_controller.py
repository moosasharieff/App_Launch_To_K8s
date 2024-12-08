import unittest
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

    def test_get_deployment_name(self):
        # Initiation
        pod_names = self.pod_name_collector.get_all()
        pod_names = list(pod_names)

        namespace = self.k8s_controller.get_namespace(pod_names[0])

        # Test
        deployment_name = self.k8s_controller.get_deployment_name(namespace)

        # Assertions
        self.assertEqual(deployment_name, 'my-app-deployment')

    def test_scale_deployment(self):
        # Initiation
        pod_names = self.pod_name_collector.get_all()
        pod_names = list(pod_names)

        namespace = self.k8s_controller.get_namespace(pod_names[0])
        deployment_name = self.k8s_controller.get_deployment_name(namespace)

        # Test
        replica_count = 3
        response = self.k8s_controller.scale_deployment(namespace,
                                                        deployment_name,
                                                        replica_count)

        # Assertions
        self.assertEqual(replica_count, response.spec.replicas)


if __name__ == '__main__':
    unittest.main()
