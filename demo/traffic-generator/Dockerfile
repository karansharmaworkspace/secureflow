FROM python:3.11-slim

RUN pip install pandas pyarrow numpy

COPY simulate.py /opt/demo/simulate.py

ENTRYPOINT ["python", "/opt/demo/simulate.py"]
