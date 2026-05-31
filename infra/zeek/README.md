# Zeek — Network Sensor

Zeek IDS deployment as a Kubernetes DaemonSet for passive network traffic capture. Captures internal HTTP traffic via SPAN/TAP port mirroring at Layer 2, bypassing WAF restrictions entirely. **Metadata-only capture** — no payloads, no PII. Exports HTTP metadata to Kafka for downstream processing.

## Files

### zeek-daemonset.yaml — Zeek Sensor Pod (119 lines)

**DaemonSet** running in `listen` namespace with `app: zeek-sensor` label.

**Node Selection:** `node-role.kubernetes.io/zeek: ""` — only runs on nodes with the zeek label.

**Host networking:** `hostNetwork: true` — required for raw packet capture.

**Sidecar Architecture (2 containers per pod):**

*Container 1 — `zeek` (Zeek IDS engine):*
- Image: `zombie-platform/zeek-sensor:latest`
- `privileged: true` with `NET_ADMIN` + `SYS_ADMIN` capabilities (required for promiscuous mode)
- Mounts: `/opt/zeek/logs` (shared volume) and Zeek config from ConfigMap
- Writes parsed HTTP logs to `/opt/zeek/logs/current/http.log`

*Container 2 — `kafka-producer` (Python streaming bridge):*
- Image: `python:3.11-slim`
- On startup: `pip install confluent-kafka`
- Continuous command: `tail -F /opt/zeek/logs/current/http.log | python /opt/zeek/bin/stream-to-kafka.py $KAFKA_BROKER`
- Environment: `KAFKA_BROKER` = `kafka-cluster-kafka-bootstrap.kafka:9092`
- Same shared log volume mount

**Embedded Zeek Config (ConfigMap `zeek-config`):**

`zeek-http-log.zeek` — Custom Zeek script that extends `Conn::Info` with:
- `http_method`, `http_path`, `http_status` — request/response metadata
- `http_user_agent`, `http_host`, `http_referrer` — client identity (UA + origin)
- `http_response_size` — payload size (captured at `http_endpoint` event)

Events hooked: `http_request` (captures method + URI), `http_reply` (status code), `http_header` (UA, host, referrer), `http_endpoint` (response size).

`local.zeek` — Zeek script loader:
- Loads base frameworks: `logging`, `conn`, `http` protocols
- Loads custom `config/zeek-http-log` script
- **Disables default HTTP log** (`HTTP::LOG`), **enables custom minimal log** (`HTTPLog::LOG`) — this ensures only metadata fields are logged, no payload content

### scripts/
Zeek integration scripts including `stream-to-kafka.py` (the Python bridge that reads Zeek JSON logs and produces to Kafka).

### config/
Zeek configuration files: `local.zeek` (main config loader) and `zeek-http-log.zeek` (custom HTTP metadata extraction).

### Dockerfile
Custom Zeek Docker image build. Based on a Zeek base image with Python installed for the Kafka bridge.
