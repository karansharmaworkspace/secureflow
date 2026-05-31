# WAF Poller

WAF (Web Application Firewall) log integration service that polls the WAF API for external-facing API traffic. Supplements internal Zeek monitoring by capturing traffic that enters through the WAF.

## Files

### main.py — Kafka WAF Poller (78 lines)

**Architecture:** Single Python script with infinite polling loop. Uses `requests` for HTTP polling and `confluent_kafka.Producer` for streaming to Kafka.

**Config (all from env vars):**
- `WAF_API_URL` — WAF API endpoint (default: `https://waf.bank.example.com/api/v1/logs`)
- `WAF_API_KEY` — Auth token for WAF API (default: empty)
- `KAFKA_BOOTSTRAP_SERVERS` — Kafka broker (default: `kafka-cluster-kafka-bootstrap.listen.svc:9092`)
- `POLL_INTERVAL_SECONDS` — Poll frequency (default: 300s = 5 minutes)
- Kafka topic: hardcoded as `raw-api-calls`

**`fetch_waf_logs(cursor)` (lines 20-29):**
- Accepts an optional cursor for pagination
- Sets `Authorization: Bearer {WAF_API_KEY}` header if key is configured
- Requests 1000 records per call with `timeout=30`
- Uses `raise_for_status()` for HTTP error handling

**`normalize_waf_record(waf_record)` (lines 32-45):**
Transforms raw WAF log format into standardized schema:
- `ts` — Timestamp (original or current time)
- `method` — HTTP method (default: GET)
- `path` — API path (default: /)
- `status` — HTTP status code (default: 200)
- `user_agent` — Client UA string
- `host` — Target host
- `source_ip` — Client IP address
- `response_size` — Response payload size
- `auth_header` — Redacted auth header ("Bearer ***") if authenticated
- `source` — Always `"waf"`
- `discovery_method` — Always `"waf_log_integration"`

**`main()` (lines 48-74):**
1. Creates Kafka `Producer` with bootstrap server config
2. Enters infinite loop:
   - Calls `fetch_waf_logs(cursor)` for current batch
   - Extracts `records` list and `next_cursor` for pagination
   - Publishes each normalized record to Kafka topic `raw-api-calls` with host as key
   - Flushes producer after each batch
   - Sleeps for `POLL_INTERVAL` seconds before next poll
3. Error handling: catches all exceptions, logs error, continues loop (resilient)

### Dockerfile
Container build with Python base image. Installs `requests` and `confluent-kafka` dependencies. Designed for running as a Kubernetes Deployment or CronJob.
