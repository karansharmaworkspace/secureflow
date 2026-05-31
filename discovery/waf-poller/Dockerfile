FROM python:3.11-slim

RUN pip install requests confluent-kafka

COPY main.py /opt/discovery/

ENTRYPOINT ["python", "/opt/discovery/main.py"]
