# Zeek Scripts

Integration scripts for the Zeek network sensor deployment. Bridges Zeek network logs with the Kafka message bus for downstream processing.

## Files

### stream-to-kafka.py
Python bridge script that reads Zeek log output and streams it to Kafka topics. Enables real-time processing of network traffic data by the Flink feature computation job.
