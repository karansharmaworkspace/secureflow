# Flink Job

Apache Flink stream processing job for real-time feature computation.

## Files

| File | Purpose |
|------|---------|
| `pom.xml` | Maven build configuration. Dependencies: Flink 1.19.0 (streaming, Kafka connector, Avro), Jackson 2.17.0. Java 11 target. Uses maven-shade-plugin for fat JAR. |
| `src/main/java/com/logiclegion/zombie/ApiCallRecord.java` | Avro/POJO for incoming API call records from Kafka. Fields: timestamp, method, path, status, user_agent, host, source_ip, response_size. |
| `src/main/java/com/logiclegion/zombie/EndpointFeatures.java` | POJO for computed endpoint features. 16 feature fields matching the ML pipeline schema. |
| `src/main/java/com/logiclegion/zombie/FeatureComputationJob.java` | Main Flink job. Consumes from `raw-api-calls` Kafka topic. Windows events by endpoint key. Computes 16 features per window (call counts, synthetic ratio, auth ratio, status distribution, timing stats). Writes to MinIO as parquet. |
| `src/main/java/com/logiclegion/zombie/SyntheticTrafficDetector.java` | Identifies synthetic traffic by detecting known monitoring user-agents and regular call intervals. |
| `src/test/java/com/logiclegion/zombie/FeatureAggregatorTest.java` | Unit tests for feature aggregation logic. |

## Build

```bash
cd flink-job
mvn clean package
```
