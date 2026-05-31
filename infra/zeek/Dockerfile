FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    zeek \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install confluent-kafka

COPY config/zeek-http-log.zeek /opt/zeek/share/zeek/site/
COPY config/local.zeek /opt/zeek/share/zeek/site/local.zeek
COPY scripts/stream-to-kafka.py /opt/zeek/bin/

RUN echo '@load zeek-http-log' >> /opt/zeek/share/zeek/site/local.zeek

ENTRYPOINT ["zeek", "-i", "eth0", "local.zeek"]
