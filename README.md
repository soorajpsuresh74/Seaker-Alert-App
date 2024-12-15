# Monitoring Stack with Prometheus, Grafana, PostgreSQL, and FastAPI

This repository sets up a monitoring stack that includes PostgreSQL, Prometheus, Grafana, a FastAPI application, and a client application for monitoring metrics, as well as custom alert rules. It uses Docker Compose to define the services and networks.

## Services

### 1. **FastAPI Service (`fastapi`)**
- **Build Context**: `./fastapi`
- **Port Mapping**: `8080:80`
- **Network**: `starnet`
- **Volumes**: `./fastapi:/app`
- **Depends On**: `postgres_server`

This service represents a FastAPI application and exposes it on port `8080`. FastAPI will be responsible for serving APIs and exposing metrics that Prometheus will scrape.

### 2. **PostgreSQL Service (`postgres_server`)**
- **Image**: `postgres:alpine`
- **Port Mapping**: `8082:5432`
- **Network**: `starnet`
- **Environment Variables**:
  - `POSTGRES_USER`: `postgres`
  - `POSTGRES_PASSWORD`: `admin`
  - `POSTGRES_DB`: `metrics_db`
- **Volumes**: `postgres_data:/var/lib/postgresql/data`

This service sets up a PostgreSQL database, used for storing metrics data.

### 3. **PostgreSQL Exporter (`postgres_exporter`)**
- **Image**: `quay.io/prometheuscommunity/postgres-exporter`
- **Port Mapping**: `9187:9187`
- **Environment**: `DATA_SOURCE_NAME="postgresql://postgres:admin@postgres_server:5432/metrics_db"`
- **Depends On**: `postgres_server`
- **Network**: `starnet`

This service exports PostgreSQL metrics for Prometheus.

### 4. **Client Service (`client`)**
- **Build Context**: `./client`
- **Port Mapping**: `8081:8777`
- **Network**: `starnet`
- **Volumes**: `./client:/client`

This service represents the client application that exposes metrics on port `8081`.

### 5. **Node Service (`node`)**
- **Build Context**: `./node`
- **Port Mapping**: `4785:4785`
- **Network**: `starnet`
- **Volumes**: `./node:/node`

This service represents a node application that exposes metrics on port `4785`.

### 6. **Prometheus Service (`prometheus`)**
- **Image**: `prom/prometheus`
- **Port Mapping**: `9090:9090`
- **Volumes**:
  - `./prometheus.yml:/etc/prometheus/prometheus.yml`
  - `./alert_rules.yml:/etc/prometheus/alert_rules.yml`
- **Network**: `starnet`
- **Depends On**: `postgres_exporter`, `client`, `node`

Prometheus is used for scraping and storing metrics from the FastAPI, PostgreSQL, and client services.

### 7. **Grafana Service (`grafana`)**
- **Image**: `grafana/grafana`
- **Port Mapping**: `3000:3000`
- **Network**: `starnet`
- **Volumes**: `grafana_data:/var/lib/grafana`
- **Environment**:
  - `GF_SECURITY_ADMIN_USER`: `admin`
  - `GF_SECURITY_ADMIN_PASSWORD`: `admin`
- **Depends On**: `prometheus`
- **Healthcheck**: Checks that Prometheus is running before starting Grafana

Grafana is used for visualizing the metrics collected by Prometheus.

## Alerts

This setup includes a set of alerts that can be triggered based on system metrics:

- **High CPU Usage**: Triggered when CPU usage exceeds 80% for more than 1 minute.
- **High RAM Usage**: Triggered when RAM usage exceeds 80% for more than 1 minute.
- **High Disk Usage**: Triggered when disk usage exceeds 9 GB for more than 1 minute.
- **Low Device Uptime**: Triggered when the system uptime is less than 3 minutes, indicating potential instability.

## Configuration Files

- **Prometheus Configuration (`prometheus.yml`)**: Configures Prometheus to scrape metrics from the `client`, `node`, and `postgres_exporter` services.
- **Alert Rules (`alert_rules.yml`)**: Defines the alerting rules that Prometheus uses to evaluate the system metrics.

## FastAPI Application Metrics

Ensure that your FastAPI application is exposing metrics in a format that Prometheus can scrape. You can use libraries like `prometheus_fastapi_instrumentator` to instrument your FastAPI application.

## Client Service Dockerfile

The client service is built using the following Dockerfile, which installs necessary libraries and runs the client application:

```dockerfile
FROM python:3.12
WORKDIR /client
RUN pip install prometheus_client requests sqlalchemy psycopg2
COPY . .
EXPOSE 8777
CMD ["python", "prometheusClient.py"]
```
## Node Service Dockerfile

The node service is built using the following Dockerfile, which installs the necessary libraries and runs the node application:
```dockerfile
FROM python:3.12
WORKDIR /node
RUN pip install psutil uvicorn fastapi
COPY . .
EXPOSE 4785
CMD ["python", "metricsNode.py"]
```