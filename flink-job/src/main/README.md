# Main Source

Root directory for the main Flink job source code. The full package path is `com.logiclegion.zombie`, containing 4 Java files that implement the real-time streaming feature computation pipeline.

## Directory Structure

```
src/main/java/com/logiclegion/zombie/
├── ApiCallRecord.java            — Kafka input record POJO
├── EndpointFeatures.java         — Feature vector POJO (16 features)
├── FeatureComputationJob.java    — Main Flink streaming pipeline (3 windows)
└── SyntheticTrafficDetector.java — Heuristic synthetic traffic classifier (7 signals)
```

**Data flow:** Kafka `raw-api-calls` → Flink source → keyBy endpoint → 3 sliding windows (7d/30d/90d) → FeatureAggregator → JSON serialize → Kafka `enriched-features`
