# Redis — In-Memory Cache (Sentinel HA)

Redis 7-alpine deployment with Sentinel-based high availability. 3-node StatefulSet in the `remember` namespace. Used as Feast online store backend for low-latency feature retrieval and general session caching.

## Files

### redis-sentinel.yaml — Sentinel Cluster (122 lines)

**Architecture:** Each pod runs 2 containers:
- **redis** (port 6379) — Redis server, configurable via `redis.conf` ConfigMap
- **sentinel** (port 26379) — Redis Sentinel for automatic failover

**Sentinel Config:**
- Monitors `mymaster` at `redis-0.redis.remember.svc:6379`
- Requires 2 Sentinels to agree on failover (`quorum: 2`)
- Down after 5000ms, failover timeout 60000ms
- Parallel syncs: 1

**Redis Config:**
- Binds 0.0.0.0, maxmemory 4GB with `allkeys-lru` eviction
- AOF persistence with `everysec` fsync
- RDB snapshots: every 900s if 1 key changed, 300s if 10, 60s if 10000

**Replication Strategy:**
- `redis-0` starts as master (`redis-server /etc/redis/redis.conf`)
- `redis-1` and `redis-2` start as slaves (`--slaveof redis-0.redis.remember.svc 6379`)
- Sentinel handles automatic promotion if master fails

**Pod Anti-Affinity:** Prefers scheduling replicas on different nodes for HA.

**Persistent Storage:** 10Gi per replica via `volumeClaimTemplates` with `ReadWriteOnce` access.

**Services:**
- `redis` (ClusterIP: None — headless) — For DNS-based pod discovery
- `redis-master` — Points specifically to `redis-0` for direct master access by Feast
