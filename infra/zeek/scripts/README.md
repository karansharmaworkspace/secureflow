# Zeek Scripts

Integration scripts that bridge Zeek network logs with the Kafka message bus. The bridge enables real-time streaming of HTTP metadata from Zeek to the Flink feature computation job via Kafka topic `raw-api-calls`.

## Files

### stream-to-kafka.py — Zeek → Kafka Bridge (26 lines)

**Architecture:** Simple Python stdin→Kafka pipeline script. Runs as a sidecar container in the Zeek DaemonSet pod (configured in `zeek-daemonset.yaml`).

**Entry point:** `tail -F /opt/zeek/logs/current/http.log | python /opt/zeek/bin/stream-to-kafka.py $KAFKA_BROKER`

**Logic:**
1. Reads broker address from `sys.argv[1]` (default: `kafka:9092`)
2. Creates Kafka `Producer` with bootstrap server config
3. Loops over `sys.stdin` lines (from `tail -F` of Zeek's HTTP log)
4. For each line, wraps it in a JSON record with `ts` (current time) and `line` (raw Zeek log)
5. Produces to Kafka topic `raw-api-calls` with no key (null key = round-robin partition distribution)
6. Flushes on script exit

**Usage in DaemonSet:**
```yaml
command:
- /bin/sh
- -c
- |
  pip install confluent-kafka
  tail -F /opt/zeek/logs/current/http.log | python /opt/zeek/bin/stream-to-kafka.py $KAFKA_BROKER
```
