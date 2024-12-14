import time
from prometheus_client import start_http_server, Gauge
import requests
import client_config
from storeMetrics import StoreMetrics

CPU_USAGE = Gauge('cpu_usage', 'CPU usage percentage')
RAM_USAGE = Gauge('ram_usage', 'RAM usage in GB')
DISK_USAGE = Gauge('disk_usage', 'Disk usage in GB')

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

            if response.status_code == 200:
                print(response_json)
                store.store_metrics(response_json)
            else:
                print("Something occurred")

    except Exception as err:
        raise Exception(f"Error occurred - {err}")
