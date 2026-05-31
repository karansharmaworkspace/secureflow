# logiclegion Package

Package root for Logic Legion team's code. Contains the `zombie` sub-package with all Flink job source files:

- `ApiCallRecord.java` — Kafka input deserialization
- `EndpointFeatures.java` — Feature vector computation
- `FeatureComputationJob.java` — Main Flink pipeline
- `SyntheticTrafficDetector.java` — Heuristic classifier
