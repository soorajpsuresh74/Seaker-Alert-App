import time
from prometheus_client import start_http_server, Gauge, Counter
import requests
import client_config
from storeMetrics import StoreMetrics

CPU_USAGE = Gauge('cpu_usage', 'CPU usage percentage')
RAM_USAGE = Gauge('ram_usage', 'RAM usage in GB')
DISK_USAGE = Gauge('disk_usage', 'Disk usage in GB')
UPTIME = Gauge('device_uptime', 'Uptime in Minutes')
TEMPERATURE = Gauge('device_temperature', 'Temperature in Celsius')

CPU_HIGH_USAGE_ALERT = Counter('cpu_high_usage_alerts', 'Count of high CPU usage alerts')
RAM_HIGH_USAGE_ALERT = Counter('ram_high_usage_alerts', 'Count of high RAM usage alerts')
DISK_HIGH_USAGE_ALERT = Counter('disk_high_usage_alerts', 'Count of high Disk usage alerts')
UPTIME_ALERT = Counter('uptime_low_alerts', 'Count of low uptime alerts')
TEMPERATURE_ALERT = Counter('temperature_high_alerts', 'Count of high temperature alerts')

if __name__ == "__main__":
    start_http_server(port=client_config.PORT)
    node_url = f"{client_config.PROTOCOL}://{client_config.NODE_HOSTNAME}:{client_config.NODE_PORT}/{client_config.NODE_METRICS_API}"
    store = StoreMetrics()

    try:
        while True:
            time.sleep(2)
            try:
                response = requests.get(node_url)
                response.raise_for_status()  # raise error for bad responses
            except requests.exceptions.RequestException as err:
                print(f"Request failed: {err}")
                continue

            if response.status_code == 200:
                response_json = response.json()

                # Set metrics
                cpu_usage = response_json.get("cpu_usage")
                if cpu_usage is not None:
                    CPU_USAGE.set(cpu_usage)
                    if cpu_usage > 50:
                        CPU_HIGH_USAGE_ALERT.inc()
                        print("ALERT: High CPU usage detected!")

                ram_usage = response_json.get("ram_usage")
                if ram_usage is not None:
                    RAM_USAGE.set(ram_usage)
                    if ram_usage > 1:
                        RAM_HIGH_USAGE_ALERT.inc()
                        print("ALERT: High RAM usage detected!")

                disk_usage = response_json.get("disk_usage")
                if disk_usage is not None:
                    DISK_USAGE.set(disk_usage)
                    if disk_usage > 7:
                        DISK_HIGH_USAGE_ALERT.inc()
                        print("ALERT: High Disk usage detected!")

                uptime = response_json.get("device_uptime")
                if uptime is not None:
                    UPTIME.set(uptime)
                    if uptime < 3:
                        UPTIME_ALERT.inc()
                        print("ALERT: Less than 3 min uptime detected")

                temperature = response_json.get("device_temperature")
                if temperature is not None:
                    TEMPERATURE.set(temperature)
                    if temperature > 75:
                        TEMPERATURE_ALERT.inc()
                        print("ALERT: High temperature detected")

                store.store_metrics(response_json)

            else:
                print(f"Error: Received status code {response.status_code}")

    except Exception as err:
        raise Exception(f"Error occurred - {err}")
