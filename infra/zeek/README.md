# Zeek - Network Sensor

Zeek network sensor deployment for passive traffic capture. Deployed as a DaemonSet to capture all internal HTTP traffic via SPAN/TAP port mirroring at Layer 2, bypassing WAF restrictions.

## Configuration

- DaemonSet deployment for node-level coverage
- Zeek scripts for HTTP traffic analysis
- Integration with Kafka for log streaming

## Directory Structure

### scripts/
Zeek integration scripts including the Kafka streaming bridge.
