# Flink Job Source Root

Root source directory for the Apache Flink feature computation job. Contains 2 subdirectories: `main/` (production code) and `test/` (unit tests).

## Structure

```
src/
├── main/
│   └── java/com/logiclegion/zombie/
│       ├── ApiCallRecord.java
│       ├── EndpointFeatures.java
│       ├── FeatureComputationJob.java
│       └── SyntheticTrafficDetector.java
└── test/
    └── java/com/logiclegion/zombie/
        └── FeatureAggregatorTest.java
```
