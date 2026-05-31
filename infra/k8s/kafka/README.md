# Kafka - Message Bus

Apache Kafka cluster deployed using the Strimzi operator. Provides the central message bus for streaming network traffic data from Zeek sensors and WAF pollers to the Flink feature computation job.

## Configuration

- 3-broker cluster for high availability
- ACL-based access control for security
- Topics configured for Zeek event streams and WAF logs
- Persistent storage with PVCs
