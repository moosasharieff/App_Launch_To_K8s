

import time
import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment
from k8s_controller import K8s_Controller

# Initialize Excel Workbook and Sheet
workbook = Workbook()
sheet = workbook.active
sheet.title = "K8s Pod Metrics"

# Add Header Row
# headers = ["Count", "Datetime", "Pod Count", "CPU Usage (%)", "Revised Replica Count"]
headers = ["Count", "Datetime", "HPA Pod Count", "Real Time HPA Pod Count", "HPA CPU Usage (%)", "Real Time HPA CPU Usage (%)", "Revised Replica Count"]
sheet.append(headers)

# Center align headers
for cell in sheet[1]:
    cell.alignment = Alignment(horizontal="center")

# File to save results
excel_file_name = "K8s_Pod_Metrics_Warm_Start_Test_400vm_4m.xlsx"


if __name__ == '__main__':
    count = 1
    namespace = ['fast-api-hpa-namespace', 'my-app-namespace']
    print("Count  |         Datetime             |  HPA Pod Count  |  Real Time HPA Pod Count  |  HPA Pod Usage  |  Real Time HPA Pod Usage  |  Revised Replica Count")
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # Collect Pod Details
        # print("Initiated cls: K8s_Controller()")
        k8s_controller = K8s_Controller()

        hpa_pod_count = k8s_controller.pod_count(namespace[0])
        real_time_hpa_pod_count = k8s_controller.pod_count(namespace[1])

        hpa_cpu_usage = k8s_controller.pod_cpu_usage(namespace[0])
        real_time_hpa_cpu_usage = k8s_controller.pod_cpu_usage(namespace[1])

        desired_replica_count = k8s_controller.calculate_desired_replicas(real_time_hpa_pod_count, real_time_hpa_cpu_usage, 50)

        # Log data to Excel
        sheet.append([count, current_time, hpa_pod_count, real_time_hpa_pod_count, hpa_cpu_usage, real_time_hpa_cpu_usage, desired_replica_count])

        print(f"  {count}           {current_time}                {hpa_pod_count}                       {real_time_hpa_pod_count}                   {hpa_cpu_usage}                        {real_time_hpa_cpu_usage}                           {desired_replica_count}")

        time.sleep(1)
        count += 1

        # Save the Excel file after each iteration to ensure data is not lost
        workbook.save(excel_file_name)
