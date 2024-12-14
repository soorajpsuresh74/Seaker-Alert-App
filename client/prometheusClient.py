import time
from prometheus_client import start_http_server, Gauge, Counter
import requests
import client_config
from storeMetrics import StoreMetrics

CPU_USAGE = Gauge('cpu_usage', 'CPU usage percentage')
RAM_USAGE = Gauge('ram_usage', 'RAM usage in GB')
DISK_USAGE = Gauge('disk_usage', 'Disk usage in GB')

CPU_HIGH_USAGE_ALERT = Counter('cpu_high_usage_alerts', 'Count of high CPU usage alerts')
RAM_HIGH_USAGE_ALERT = Counter('ram_high_usage_alerts', 'Count of high RAM usage alerts')
DISK_HIGH_USAGE_ALERT = Counter('disk_high_usage_alerts', 'Count of high Disk usage alerts')
UPTIME_ALERT = Counter('memory_low_alerts', 'Count of low memory usage alerts')

if __name__ == "__main__":
    start_http_server(port=client_config.PORT)
    node_url = f"{client_config.PROTOCOL}://{client_config.NODE_HOSTNAME}:{client_config.NODE_PORT}/{client_config.NODE_METRICS_API}"
    store = StoreMetrics()
    try:
        while True:
            time.sleep(2)
            response = requests.get(node_url)
            response_json = response.json()

            CPU_USAGE.set(response_json["cpu_usage"])
            RAM_USAGE.set(response_json["ram_usage"])
            DISK_USAGE.set(response_json["disk_usage"])

            if response_json["cpu_usage"] > 80:
                CPU_HIGH_USAGE_ALERT.inc()
                print("ALERT: High CPU usage detected!")

            if response_json["ram_usage"] > 80:
                RAM_HIGH_USAGE_ALERT.inc()
                print("ALERT: High RAM usage detected!")

            if response_json["disk_usage"] > 9:
                DISK_HIGH_USAGE_ALERT.inc()
                print("ALERT: High Disk usage detected!")

            if response_json["device_uptime"] > 3:
                UPTIME_ALERT.inc()
                print("ALERT: Less than 3 min")

            if response.status_code == 200:
                print(response_json)
                store.store_metrics(response_json)
            else:
                print("Something occurred")

    except Exception as err:
        raise Exception(f"Error occurred - {err}")
