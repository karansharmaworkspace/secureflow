# Kafka — Message Bus

Apache Kafka cluster deployed using the Strimzi operator (v0.41.0). Central message bus for streaming network traffic from Zeek sensors and WAF pollers to the Flink feature computation job. 3-broker cluster in the `listen` namespace.

## Files

### strimzi-operator.yaml — Operator Installation (18 lines)

HelmChart resource (Rancher-style) that installs Strimzi Kafka Operator. Installed in `kafka` namespace, watches `targetNamespace: listen`. Uses operator version 0.41.0 from `https://strimzi.io/charts/`. Feature gate: `+UseStrimziPodSets`.

### kafka-cluster.yaml — Cluster + Raw Topic (53 lines)

**Kafka CR** — Strimzi `Kafka` custom resource defining:
- **Version:** 3.7.0
- **Replicas:** 3 (HA across nodes)
- **Listeners:** Plain (9092, internal, no TLS) + TLS (9093, internal, TLS-enabled)
- **Config:** 3x replication factor for offsets/transactions. `min.insync.replicas: 2`. Retention: 720 hours (30 days), max 100GB per partition.
- **Storage:** 100Gi persistent-claim per broker, `deleteClaim: false` (survives cluster deletion)
- **ZooKeeper:** 3 replicas, 10Gi each

**KafkaTopic CR** — `raw-api-calls` topic:
- **Partitions:** 12 (parallelism for Zeek/WAF producers)
- **Replicas:** 3
- **Retention:** 2,592,000,000 ms = 30 days
- **Segment:** 1GB segments

### kafka-acls.yaml — Access Control (58 lines)

Defines 2 KafkaUser resources with TLS authentication and `simple` authorization:

**`zeek-producer`** (Write access):
- `Write` + `Describe` on `raw-api-calls` topic
- `DescribeConfigs` on cluster (for metadata)

**`flink-consumer`** (Read access):
- `Read` + `Describe` on `raw-api-calls` topic
- `Read` + `Describe` on consumer group `flink-consumer-group`

Both use TLS client authentication via Strimzi User operator.
