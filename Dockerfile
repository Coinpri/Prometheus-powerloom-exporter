FROM python:3.9.19-alpine3.20

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY prometheus_exporter.py ./prometheus_exporter.py

ENTRYPOINT ["python3", "prometheus_exporter.py"]