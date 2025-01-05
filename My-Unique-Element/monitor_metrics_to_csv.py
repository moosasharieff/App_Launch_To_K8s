

import time
import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment
from k8s_controller import K8s_Controller

# Initialize Excel Workbook and Sheet
workbook = Workbook()
sheet = workbook.active
sheet.title = "K8s Pod Metrics 100 VMs"

# Add Header Row
headers = ["Count", "Datetime", "Pod Count", "CPU Usage (%)", "Revised Replica Count"]
sheet.append(headers)

# Center align headers
for cell in sheet[1]:
    cell.alignment = Alignment(horizontal="center")

# File to save results
excel_file_name = "k8s_Pod_metrics_100Vms.xlsx"


if __name__ == '__main__':
    count = 1
    namespace = ['fast-api-hpa-namespace', 'my-app-namespace']
    use_namespace = namespace[1]
    print("Count  |         Datetime             |  Current Pod Count  |  Curr. Pod Usage  |  Revised Replica Count")
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # Collect Pod Details
        # print("Initiated cls: K8s_Controller()")
        k8s_controller = K8s_Controller()

        pod_count = k8s_controller.pod_count(use_namespace)
        cpu_usage = k8s_controller.pod_cpu_usage(use_namespace)

        desired_replica_count = k8s_controller.calculate_desired_replicas(pod_count, cpu_usage, 50)

        # Log data to Excel
        sheet.append([count, current_time, pod_count, cpu_usage, desired_replica_count])

        print(f"  {count}           {current_time}             {pod_count}                    {cpu_usage}                  {desired_replica_count}")

        time.sleep(0.5)
        count += 1

        # Save the Excel file after each iteration to ensure data is not lost
        workbook.save(excel_file_name)
