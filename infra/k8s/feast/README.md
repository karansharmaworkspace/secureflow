# Feast — Feature Store

Feast 0.39.0 feature store with 2-replica deployment in `remember` namespace. Provides the canonical feature definitions for the ML pipeline. Online store via Redis, offline store via MinIO Parquet files.

## Files

### feast-deployment.yaml — Feast Serving Layer (127 lines)

**Deployment:** 2 replicas of `feastdev/feature-server:0.39.0` with service account `feast-sa`.

**Ports:** 6566 (gRPC), 6567 (HTTP)

**Feature Store Config (ConfigMap `feast-config`):**
- Project: `zombie_platform`
- Provider: `local`
- Online store: Redis at `redis-master.remember.svc:6379`
- Offline store: File-based (MinIO Parquet)
- Registry: File-based at `/opt/feast/repo/registry.db` with 60s cache TTL

**Feature Definition (ConfigMap `feast-repo` → `features.py`):**

Defines 1 Entity + 1 FeatureView:

**Entity:** `endpoint_key` (String) — Composite key: `host|method|path`

**FeatureView:** `endpoint_features` with 90-day TTL, online serving enabled:
| Feature | Type | Source |
|---------|------|--------|
| total_calls | Int64 | Traffic simulator |
| synthetic_calls | Int64 | Bot/monitor count |
| real_calls | Int64 | Real user calls |
| days_since_last_real_call | Int64 | Staleness |
| unique_user_agents | Int64 | UA diversity |
| unique_source_ips | Int64 | IP diversity |
| auth_ratio | Float64 | Auth coverage |
| ratio_2xx / 4xx / 5xx | Float64 | Status distribution |
| response_size_mean / stddev | Float64 | Payload stats |
| interarrival_mean_ms / stddev_ms | Float64 | Timing patterns |
| unique_hours_of_day | Int64 | Time spread |
| is_100pct_synthetic | Bool | Bot flag |

**Source:** FileSource at `s3://feature-snapshots/endpoint_features.parquet` (MinIO backing).
