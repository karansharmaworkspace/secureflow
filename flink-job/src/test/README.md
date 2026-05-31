# Test Source Root

Root directory for Flink job test code. Contains JUnit 5 unit tests for the feature computation pipeline.

## Structure

```
test/java/com/logiclegion/zombie/
└── FeatureAggregatorTest.java    — 8 tests for FeatureAggregator logic
```

Tests use JUnit 5 (`org.junit.jupiter.api`) and cover: accumulator creation, real/synthetic call classification, auth tracking, status code counting, 100% synthetic detection, and partial aggregate merging.
