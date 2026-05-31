import json
import logging
import os
import time
from datetime import datetime

import requests
from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WAF_API_URL = os.getenv("WAF_API_URL", "https://waf.bank.example.com/api/v1/logs")
WAF_API_KEY = os.getenv("WAF_API_KEY", "")
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-cluster-kafka-bootstrap.listen.svc:9092")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
TOPIC = "raw-api-calls"


def fetch_waf_logs(cursor=None):
    params = {"limit": 1000}
    if cursor:
        params["cursor"] = cursor

    headers = {"Authorization": f"Bearer {WAF_API_KEY}"} if WAF_API_KEY else {}

    resp = requests.get(WAF_API_URL, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize_waf_record(waf_record):
    return {
        "ts": waf_record.get("timestamp", time.time()),
        "method": waf_record.get("method", "GET"),
        "path": waf_record.get("path", "/"),
        "status": waf_record.get("status_code", 200),
        "user_agent": waf_record.get("user_agent", ""),
        "host": waf_record.get("host", ""),
        "source_ip": waf_record.get("client_ip", ""),
        "response_size": waf_record.get("response_size", 0),
        "auth_header": "Bearer ***" if waf_record.get("authenticated") else "",
        "source": "waf",
        "discovery_method": "waf_log_integration",
    }


def main():
    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    cursor = None

    logger.info(f"Starting WAF poller — interval: {POLL_INTERVAL}s, topic: {TOPIC}")

    while True:
        try:
            data = fetch_waf_logs(cursor)
            records = data.get("records", [])
            cursor = data.get("next_cursor")

            for record in records:
                normalized = normalize_waf_record(record)
                producer.produce(
                    TOPIC,
                    key=normalized["host"].encode(),
                    value=json.dumps(normalized).encode(),
                )

            producer.flush()
            logger.info(f"Published {len(records)} WAF records to {TOPIC}")

        except Exception as e:
            logger.error(f"Poll error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
