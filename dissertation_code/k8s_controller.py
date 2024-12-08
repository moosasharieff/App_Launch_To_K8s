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

    def get_deployment_name(self, namespace) -> Optional[str]:
        """
        :param namespace: Namespace of the pod.
        :return: Deployment name of the pod.
        """
        deployments = (self.apps_v1.
                       list_namespaced_deployment(namespace=namespace))

        return deployments.items[0].metadata.name if (
            deployments.items[0].metadata.name) else None

    def scale_deployment(self, namespace: str,
                         deployment_name: str,
                         replicas: int):
        """
        Scale the Deployment to the desired number of replicas.
        :param namespace: The namespace of the Deployment.
        :param deployment_name: The name of the Deployment.
        :param replicas: The desired number of replicas.
        """
        # Define the patch with the desired replicas
        scale_patch = {
            "metadata": {
                "namespace": namespace
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": "my-app"
                    }
                }
            }
        }

        try:
            # Patch the Deployment with the new replica count
            response = self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=scale_patch
            )
            return response
        except client.exceptions.ApiException as e:
            print(f"Exception occurred: {e}")
