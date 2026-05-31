# WAF Poller

WAF (Web Application Firewall) log integration service that polls the WAF API for access logs. Captures external-facing API traffic data to supplement internal network monitoring from Zeek.

## Files

### main.py
Python-based poller service that:
- Authenticates with the WAF API using configured credentials
- Polls for access logs at configurable intervals
- Parses and normalizes log entries
- Streams processed data to Kafka for downstream analysis

### Dockerfile
Container build for the poller service with Python dependencies.
