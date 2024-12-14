FROM python:3.12
WORKDIR /client
RUN pip install prometheus_client requests sqlalchemy psycopg2
COPY . .
EXPOSE 8777
CMD ["python", "prometheusClient.py"]