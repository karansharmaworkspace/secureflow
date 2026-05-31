# Zombie Detection Flink Job — Main Source

Apache Flink 1.19 streaming job for real-time feature computation. Consumes raw API call records from Kafka topic `raw-api-calls`, windows them by endpoint key at 3 time scales (7d, 30d, 90d), and publishes enriched feature vectors to `enriched-features` topic.

## Files

### ApiCallRecord.java — Input Record POJO (46 lines)

Simple Java POJO with Jackson JSON deserialization (`fromJson()`). Fields: `ts` (double timestamp), `method`, `path`, `status` (int), `userAgent`, `host`, `referrer`, `responseSize` (long), `sourceIp`, `authHeader`.

Key methods:
- `endpointKey()` — Constructs composite key: `host|method|path`
- `hasAuth()` — True if authHeader is non-null and non-empty
- `isKnownMonitor()` — Checks userAgent against known monitoring tools: prometheus, kube-probe, datadog agent, healthcheck, uptimerobot

### EndpointFeatures.java — Feature Output POJO (58 lines)

Aggregated feature vector with 16 feature fields + metadata. `toMap()` computes derived features from raw counts:
- `auth_ratio` = `authTokenCount / totalCalls`
- `ratio_2xx/4xx/5xx` = status code ratios
- `is_100pct_synthetic` = `syntheticCalls > 0 && realCalls == 0`

Schema matches the ML pipeline's `FEATURE_COLUMNS` in `features.py`.

### FeatureComputationJob.java — Main Flink Pipeline (132 lines)

**Entry point:** Reads 3 env vars: `KAFKA_BOOTSTRAP_SERVERS` (default localhost:9092), `KAFKA_RAW_TOPIC` (default raw-api-calls), `KAFKA_OUTPUT_TOPIC` (default enriched-features).

**Execution environment:**
- Checkpointing every 60s with 120s timeout
- Watermark strategy: bounded out-of-orderness (10s), timestamp extractor from `record.ts * 1000`

**Source:** Kafka source with `SimpleStringSchema` deserialization, consumer group `flink-feature-job`

**Processing pipeline:**
1. `map(json -> ApiCallRecord.fromJson(json))` — Parse JSON to POJO
2. `filter(record != null)` — Drop parse failures
3. `assignTimestampsAndWatermarks` — Event-time processing

**3 parallel window streams:**

| Stream | Window | Slide | Output |
|--------|--------|-------|--------|
| 7-day | `SlidingEventTimeWindows.of(7 days, 1 hour)` | Hourly | Short-term patterns |
| 30-day | `SlidingEventTimeWindows.of(30 days, 6 hours)` | Every 6h | Medium-term trends |
| 90-day | `SlidingEventTimeWindows.of(90 days, 1 day)` | Daily | Long-term staleness |

Each window uses `FeatureAggregator` (custom `AggregateFunction`), then `map` serializes to JSON.

**Aggregator logic (inner class):**
- `add()`: Increments totalCalls, classifies synthetic vs real via `record.isKnownMonitor()`, tracks auth presence, counts status code ranges
- `merge()`: Sums all counters from partial aggregates (for parallel processing)
- `getResult()`: Computes `isOneHundredPercentSynthetic` flag

**Sink:** All 3 streams merged via `.union()` → Kafka sink to `enriched-features` topic

### SyntheticTrafficDetector.java — ML Feature Logic (101 lines)

Standalone synthetic traffic classifier with 7 heuristic signals:

| Signal | Method | Description |
|--------|--------|-------------|
| Regular interval | `isRegularInterval()` | Stddev of inter-arrival times < 1.0s |
| Monitor UA | `isMonitorUserAgent()` | All UAs match known monitoring tools |
| Low-entropy payload | `isLowEntropyPayload()` | All response sizes identical |
| Single source IP | `isSingleSourceIp()` | Only 1 unique client IP |
| Always 200 | `isAlways200()` | 100% success rate (no errors) |
| Time-clustered | `isTimeClustered()` | Calls in ≤ 2 distinct hours |
| Exactly periodic | `isExactlyPeriodic()` | All intervals within 1s of each other |

**Detection:** If >= 4/7 signals trigger (confidence >= 0.6), classified as synthetic.
**Reason string:** e.g., `"5/7 synthetic signals (71%)"`

**DetectionResult** inner class: `isSynthetic` (boolean), `confidence` (double 0.0-1.0), `reason` (human-readable string).
