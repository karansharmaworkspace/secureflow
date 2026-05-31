# Flink — Stream Processing

Apache Flink operator (v1.9.0) and FlinkDeployment (v1_19) for real-time feature computation. Consumes raw API call records from Kafka topic `raw-api-calls` and outputs enriched feature vectors to `enriched-features` topic.

## Files

### flink-operator.yaml — Operator Installation (18 lines)

HelmChart resource installing Flink Kubernetes Operator v1.9.0 from `https://apache.github.io/flink-kubernetes-operator`. Installed in `flink` namespace, watches `targetNamespace: listen` only.

### kafka-topics.yaml — Enriched Features Topic (13 lines)

Defines the `enriched-features` Kafka topic:
- **Partitions:** 6 (less than raw topic since aggregated data volume is smaller)
- **Replicas:** 3
- **Retention:** 7,776,000,000 ms = 90 days (features retained longer than raw logs)
- **Segment:** 1GB

### flink-deployment.yaml — Feature Computation Job (41 lines)

FlinkDeployment CR (API `flink.apache.org/v1beta1`) defining:

**Image:** `zombie-platform/flink-feature-job:latest` (Java Flink job)

**Flink Config:**
- Parallelism: default 4, 4 task slots
- JobManager: 2048m memory, 1 CPU
- TaskManager: 4096m memory, 2 CPU × 2 replicas
- Checkpointing: every 60s, exactly-once, 30s min pause, tolerate 3 failures
- Checkpoints: file-based at `/opt/flink/checkpoints`
- ServiceAccount: `flink-sa`

**Environment Variables (passed to container):**
- `KAFKA_BOOTSTRAP_SERVERS` → `kafka-cluster-kafka-bootstrap.listen.svc:9092`
- `KAFKA_RAW_TOPIC` → `raw-api-calls`
- `KAFKA_OUTPUT_TOPIC` → `enriched-features`

### Dockerfile
Builds the Flink job JAR from Java source using Maven, then packages into a Flink base image for deployment.
