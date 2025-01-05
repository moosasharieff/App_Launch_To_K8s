import json
import openpyxl
import pytz
from datetime import datetime

# Function to read the JSON-like log entries and extract relevant data
def extract_metrics_from_log(log_file):
    metrics_list = []

    with open(log_file, 'r') as file:
        for line in file:
            try:
                # Check if the line contains valid JSON
                if line.strip().startswith('INFO'):
                    # Extract the JSON part of the line
                    start_idx = line.find('{')
                    end_idx = line.rfind('}') + 1
                    json_data = line[start_idx:end_idx]

                    # Parse the JSON data
                    metrics = json.loads(json_data)
                    metrics_list.append(metrics)
            except Exception as e:
                print(f"Error parsing line: {line}. Error: {e}")

    return metrics_list

def convert_dub_datetime(dt):
    utc_time = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc_zone = pytz.utc
    utc_time = utc_zone.localize(utc_time)
    dublin_zone = pytz.timezone('Europe/Dublin')
    dublin_time = utc_time.astimezone(dublin_zone)
    return dublin_time.strftime('%Y-%m-%dT%H:%M:%S')

# Function to save extracted metrics to an Excel file
def save_metrics_to_excel(metrics_data, output_file):
    # Create a new workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Metrics"

    # Write headers
    headers = ['URL', 'Timestamp', 'VUs', 'Iterations', 'HTTP Request Duration',
               'HTTP Request Waiting', 'HTTP Request Failed',
               'Iteration Duration', 'HTTP Requests']
    ws.append(headers)

    # Write the metrics data to the Excel sheet
    for metrics in metrics_data:
        datetime = convert_dub_datetime(metrics.get('timestamp'))

        url = metrics.get('url'),
        url = 'Real-Time-HPA' if url[0] == 'http://127.0.0.1:7080/' else 'HPA'
        ws.append([
            url,
            datetime,
            metrics.get('vus', ''),
            metrics.get('iterations', ''),
            metrics.get('http_req_duration', ''),
            metrics.get('http_req_waiting', ''),
            metrics.get('http_req_failed', ''),
            metrics.get('iteration_duration', ''),
            metrics.get('http_reqs', '')
        ])

    # Save the workbook to the file
    wb.save(output_file)


# Main function
if __name__ == "__main__":
    log_file = "metrics_logs.json"  # Path to your log file
    output_file = "k6_metrics_Warm_Start_Test_400vm_4m.xlsx"  # Path to the output Excel file

    # Extract metrics data from the log file
    metrics_data = extract_metrics_from_log(log_file)

    # Save the extracted data to an Excel file
    save_metrics_to_excel(metrics_data, output_file)

    print(f"Metrics data has been saved to {output_file}.")
