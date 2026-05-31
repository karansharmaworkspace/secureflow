# Infrastructure — Phase 1

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Core Switch                          │
│  SPAN/TAP port mirrors ALL internal traffic              │
└────────────┬─────────────────────────────────────────────┘
             │ (Layer 2 — bypasses WAF)
┌────────────▼─────────────────────────────────────────────┐
│  Zeek Sensor (DaemonSet, hostNetwork)                    │
│  Extracts: method, path, status, user-agent, host,       │
│            referrer, response_size                       │
│  NO payload content captured                             │
└────────────┬─────────────────────────────────────────────┘
             │ (JSON logs via stdin)
┌────────────▼─────────────────────────────────────────────┐
│  Kafka Producer (sidecar container)                      │
│  Reads Zeek log file, writes to Kafka topic              │
└────────────┬─────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────┐
│  Kafka Cluster (3 brokers, Strimzi operator)             │
│  Topic: raw-api-calls (12 partitions, RF=3)              │
│  Retention: 720 hours (30 days)                          │
└──────────────────────────────────────────────────────────┘
```

## Deploy

```bash
make all
```

## Verify

```bash
# Check logs flowing into Kafka
kubectl exec -n listen deployment/kafka-cluster-kafka-0 -- \
  bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic raw-api-calls --from-beginning --max-messages 5
```

## Data Schema

```json
{
  "ts": 1717000000.0,
  "method": "GET",
  "path": "/api/v1/users",
  "status": 200,
  "user_agent": "Mozilla/5.0 ...",
  "host": "api.bank.example.com",
  "referrer": "-",
  "response_size": 1234,
  "source_ip": "10.0.1.42"
}
```

## Compliance Notes

- **No PII**: Zeek extracts metadata only; no request/response body captured
- **PCI-DSS**: Card data never enters the pipeline (metadata only)
- **Retention**: Kafka configured for 30-day retention (tunable)
- **Access**: Kafka ACLs restrict producer/consumer access to authorized services
