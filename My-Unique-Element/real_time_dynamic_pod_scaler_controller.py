"""
This is the main python file where Kubernetes cluster will be controlled.
"""
import time
from k8s_controller import K8s_Controller

if __name__ == "__main__":
    count = 1

    base_time = 10  # Minimum sleep time in seconds
    adjustment_factor = 0.2  # How much the sleep time adjusts based on CPU usage

    print('Running at...')
    while True:

        # Collect Pod Details
        k8s_controller = K8s_Controller()
        pod_count = k8s_controller.pod_count('my-app-namespace')
        cpu_usage = k8s_controller.pod_cpu_usage('my-app-namespace')

        # Calculate desired replicas
        desired_replica_count = k8s_controller.calculate_desired_replicas(pod_count, cpu_usage, 50)
        desired_replica_count = 1 if desired_replica_count < 1 else desired_replica_count

        # Deployment Initiation
        if desired_replica_count != pod_count:
            deployment_name = k8s_controller.get_deployment_name('my-app-namespace')
            response = k8s_controller.scale_deployment('my-app-namespace', deployment_name, desired_replica_count)

            count += 1

            sleep_time = max(1, base_time - adjustment_factor * (cpu_usage / 10))  # Ensure sleep_time >= 1 second

            time.sleep(sleep_time)
