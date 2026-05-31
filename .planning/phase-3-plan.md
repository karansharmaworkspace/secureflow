# Phase 3 Plan: Feature Store & Cache Layer

**Goal:** Deploy Feast feature store with feature definitions, Redis HA cluster (Sentinel), and MinIO object storage.

## Tasks

### 3.1 Deploy MinIO Object Storage
- Deploy MinIO on K8s with persistent volumes (100Gi)
- Create buckets: `historical-logs`, `model-artifacts`, `feature-snapshots`
- Configure lifecycle policies (30d logs, 90d features)
- Enable TLS and access keys

### 3.2 Deploy Redis HA with Sentinel
- Deploy 3-node Redis cluster with Sentinel auto-failover
- Configure for sub-millisecond feature lookups
- Set eviction policy: allkeys-lru
- Enable persistence (AOF + RDB)

### 3.3 Deploy Feast Feature Store
- Deploy Feast Serving (gRPC endpoint for online features)
- Deploy Feast Core/Registry for feature definitions
- Configure Feast to use Redis for online serving
- Configure Feast to use MinIO for historical storage

### 3.4 Define Feast Feature Definitions
- Create feature definitions for all 20+ signals
- Source from `enriched-features` Kafka topic
- Define feature view: `endpoint_features` with all signals
- Register entity: `endpoint_key` (host|method|path composite)

### 3.5 Integration Testing
- Verify Flink job output feeds into Feast feature rows
- Verify Redis returns features in < 10ms
- Verify MinIO stores historical snapshots
- End-to-end: Zeek → Kafka → Flink → Feast → Redis

## Success Criteria
1. MinIO buckets created and accessible
2. Redis Sentinel cluster operational with auto-failover working
3. Feast Serving endpoint returning features in < 10ms
4. Feature definitions registered for all 20+ signals
5. End-to-end flow verified: feature computation → Feast → Redis

---
*Created: 2026-05-26*
