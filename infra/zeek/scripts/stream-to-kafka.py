#!/usr/bin/env python3

import json
import sys
import time
from confluent_kafka import Producer

KAFKA_BROKER = sys.argv[1] if len(sys.argv) > 1 else "kafka:9092"
TOPIC = "raw-api-calls"

producer = Producer({"bootstrap.servers": KAFKA_BROKER})

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    record = {
        "ts": time.time(),
        "line": line
    }

    producer.produce(TOPIC, key=None, value=json.dumps(record))
    producer.poll(0)

producer.flush()
