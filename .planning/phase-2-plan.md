# Phase 2 Plan: Streaming Pipeline & Feature Computation

**Goal:** Deploy Apache Flink with exactly-once semantics, compute 20+ features per endpoint (including synthetic traffic detection), consuming from Kafka topic `raw-api-calls`.

## Tasks

### 2.1 Deploy Flink Cluster on K8s
- Deploy Apache Flink 1.19+ using Flink Kubernetes Operator
- Configure: JobManager HA, TaskManager auto-scaling, checkpointing to MinIO (Phase 3, use local for now)
- Enable exactly-once semantics with Kafka source

### 2.2 Build Flink Feature Computation Job
- Consume from `raw-api-calls` topic
- Key by endpoint (host + path + method composite key)
- Compute sliding window features over 7, 30, 90-day windows
- Write to sink (Kafka topic `enriched-features` for Phase 3)

### 2.3 Feature Computation Pipeline
Compute all 20+ signals per endpoint:
1. Request frequency (7/30/90 day windows)
2. Days since last call (non-synthetic)
3. Auth token presence (look for Authorization header)
4. Response code distribution (2xx/4xx/5xx ratios)
5. User-agent diversity (unique agent count)
6. Payload entropy (response_size variance)
7. Time-of-day clustering (hour distribution)
8. Call interval regularity (stddev of inter-arrival times)
9. API version drift (extract version from path pattern)
10-20. Additional computed signals from enriched data

### 2.4 Synthetic Traffic Detection
- Detect synthetic vs real traffic using 7 signals:
  1. Perfectly regular intervals (stddev < 1s)
  2. Known monitoring user-agents (Prometheus, kube-probe, Datadog)
  3. Low payload entropy (identical response size every call)
  4. Single source IP
  5. Always 200 status code
  6. Time clustering (same time every day)
  7. Call frequency (exactly every N seconds)
- Flag endpoint as `100% synthetic` = treated as zero real calls

### 2.5 Flink Job Output Schema
- Define enriched feature Avro schema
- Sink to Kafka topic `enriched-features`
- Include: endpoint key, feature vector, synthetic flag, timestamp

## Success Criteria
1. Flink cluster deployed and consuming from `raw-api-calls`
2. All 20+ features computed per endpoint with < 100ms latency
3. Synthetic traffic detector operational with 7 signals
4. Enriched features flowing to `enriched-features` topic
5. Exactly-once semantics verified (no duplicates in failure scenario)

---
*Created: 2026-05-26*
