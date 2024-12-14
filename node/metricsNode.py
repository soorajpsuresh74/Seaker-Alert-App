import time
import psutil
import uvicorn
import node_config
from fastapi import FastAPI, HTTPException

app = FastAPI()


class GatherMetrics:
    __slots__ = ('cpu_usage', 'ram_usage', 'disk_usage', 'device_uptime', 'device_temperature')

    def __init__(self):
        self.cpu_usage = None
        self.ram_usage = None
        self.disk_usage = None
        self.device_uptime = None
        self.device_temperature = None

    def get_system_metrics(self) -> dict:
        try:
            self.cpu_usage = psutil.cpu_percent(interval=1)
            self.ram_usage = psutil.virtual_memory().used / (1024 ** 3)
            self.disk_usage = psutil.disk_usage(path='/').used / (1024 ** 3)
            self.device_uptime = (time.time() - psutil.boot_time()) / 3600

            if hasattr(psutil, 'sensors_temperatures'):
                temperature = psutil.sensors_temperatures()
                if temperature.get('coretemp'):
                    core_temp = temperature.get('coretemp')
                    self.device_temperature = core_temp[0].current

            return {
                "cpu_usage": self.cpu_usage,
                "ram_usage": self.ram_usage,
                "disk_usage": self.disk_usage,
                "device_uptime": self.device_uptime,
                "device_temperature": self.device_temperature
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred during metrics capturing: {str(e)}")


@app.get(node_config.METRICS_API)
async def metrics():
    try:
        gm = GatherMetrics()
        return gm.get_system_metrics()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


if __name__ == '__main__':
    uvicorn.run("metricsNode:app", host=node_config.HOST, port=node_config.PORT)
