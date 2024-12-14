FROM python:3.12
WORKDIR /node
RUN pip install psutil uvicorn fastapi
COPY . .
EXPOSE 4785
CMD ["python", "metricsNode.py"]