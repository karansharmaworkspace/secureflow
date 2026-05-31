#!/bin/bash

set -euo pipefail

STAGING_URL="${STAGING_URL:-https://staging.bank.example.com}"
RATE_LIMIT="${RATE_LIMIT:-10}"
OUTPUT_DIR="${OUTPUT_DIR:-/opt/discovery/output}"

mkdir -p "$OUTPUT_DIR"

echo "=== Staging API Scanner ==="
echo "Target: $STAGING_URL"
echo "Rate limit: $RATE_LIMIT req/s"
echo "Output: $OUTPUT_DIR"

WORDLIST="/opt/discovery/wordlists/api-paths.txt"

if [ ! -f "$WORDLIST" ]; then
  cat > "$WORDLIST" << 'EOF'
/api
/api/v1
/api/v2
/api/v3
/swagger.json
/swagger/v1/swagger.json
/api-docs
/v1/api-docs
/v2/api-docs
/openapi.json
/openapi.yaml
/actuator
/actuator/health
/actuator/info
/health
/healthcheck
/version
/.well-known
/docs
/docs/api
/apidoc
/apidocs
/api/swagger
/graphql
/rest
/soap
/management
/monitor
/metrics
/prometheus
/status
/info
/oauth/token
/oauth2
/login
/logout
/register
/users
/admin
/console
/h2-console
/druid
/catalog
/inventory
/orders
/payments
/refunds
/settlements
EOF
fi

echo "=== Starting scan ==="
while IFS= read -r path; do
  [ -z "$path" ] && continue
  url="${STAGING_URL}${path}"

  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 --rate "${RATE_LIMIT}" "$url" 2>/dev/null || echo "000")

  if [ "$status" != "404" ] && [ "$status" != "000" ]; then
    echo "[$status] $url"
    echo "{\"url\":\"$url\",\"path\":\"$path\",\"status\":$status,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
      >> "$OUTPUT_DIR/findings.jsonl"
  fi
done < "$WORDLIST"

count=$(wc -l < "$OUTPUT_DIR/findings.jsonl" 2>/dev/null || echo 0)
echo "=== Scan complete: $count endpoints discovered ==="
