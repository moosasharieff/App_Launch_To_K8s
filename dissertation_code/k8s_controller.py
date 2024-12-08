
from typing import Optional

from kubernetes import client, config


class K8s_Controller:
    CPU = '50m'
    REPLICA_COUNT = 1

    def __init__(self):
        """
        This class will have all the methods to scale Pods.

        :param replica_count: len(Pod_CPU_Collector.get_cpu())
        """
        # Load Kubernetes configuration
        config.load_kube_config()

        # API Clients
        self.core_v1 = client.CoreV1Api()  # Manage resources
        self.apps_v1 = client.AppsV1Api()  # Manage Deployments

    def get_namespace(self, pod_name) -> Optional[str]:
        """
        :param pod_name: Name of the pod.
        :return: namespace of the pod or None if not found.
        """
        pods = self.core_v1.list_pod_for_all_namespaces()
        for pod in pods.items:
            if pod.metadata.name == pod_name:
                return pod.metadata.namespace
        raise None  # Pod not found

    def get_label(self):
        pass

    def deploy_pod(self):
        pass
