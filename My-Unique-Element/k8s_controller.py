from typing import Optional

from kubernetes import client, config

import math

class K8s_Controller:

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

    def pod_count(self, namespace: str) -> int:
        """
        :param namespace: Namespace attached to the Pods.
        :return: Return the count of pods in the namespace
        """
        pods = self.core_v1.list_namespaced_pod(namespace=namespace)

        running_pods = [pod for pod in pods.items if pod.status.phase == "Running"]

        return len(running_pods)

    def pod_cpu_usage(self, namespace):
        """
        Get the CPU usage for each Pod in a namespace.

        Parameters:
            namespace (str): The namespace to fetch Pod CPU usage from (default is "default").

        Returns:
            dict: A dictionary where the keys are Pod names and values are CPU usage in millicores.
        """
        # Load Kubernetes configuration
        config.load_kube_config()  # Use config.load_incluster_config() if running inside a cluster.

        # Create Metrics API client
        api = client.CustomObjectsApi()

        # Query metrics.k8s.io API for Pod metrics
        pod_metrics = api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods"
        )

        pod_cpu_usage = {}
        for pod in pod_metrics["items"]:
            pod_name = pod["metadata"]["name"]
            total_cpu = 0

            # Sum CPU usage of all containers in the Pod
            for container in pod["containers"]:
                cpu_usage = container["usage"]["cpu"]

                # Convert CPU usage to millicores
                if cpu_usage.endswith("n"):
                    total_cpu += int(cpu_usage[:-1]) / 1_000_000  # Convert nanocores to millicores
                elif cpu_usage.endswith("u"):
                    total_cpu += int(cpu_usage[:-1]) / 1_000  # Convert microcores to millicores
                elif cpu_usage.endswith("m"):
                    total_cpu += int(cpu_usage[:-1])  # Already in millicores
                else:
                    total_cpu += int(cpu_usage) * 1_000  # Convert cores to millicores

            pod_cpu_usage[pod_name] = total_cpu

        cpu_sum = 1
        for pod, cpu in pod_cpu_usage.items():
            cpu_sum += cpu

        cpu_avg = cpu_sum // len(pod_cpu_usage)

        return cpu_avg

    def calculate_desired_replicas(self, current_replicas,
                                   current_metric_value, desired_metric_value):
        """
        Calculate the desired number of replicas based on current and desired metric values.

        :param current_replicas: Current number of replicas.
        :param current_metric_value: Current metric value.
        :param desired_metric_value: Desired metric value.
        :return: The calculated desired number of replicas.
        """
        if desired_metric_value == 0:
            raise ValueError("desiredMetricValue cannot be zero to avoid division by zero.")

        scaling_factor = current_metric_value / desired_metric_value
        desired_replicas = math.ceil(current_replicas * scaling_factor)
        return desired_replicas
