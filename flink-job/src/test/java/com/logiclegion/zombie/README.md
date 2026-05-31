# Zombie Detection Flink Job — Tests

JUnit 5 test suite for the Flink feature computation job. Contains 8 tests for the `FeatureAggregator` inner class of `FeatureComputationJob.java`.

## Files

### FeatureAggregatorTest.java — Aggregator Unit Tests (187 lines)

Tests the custom `AggregateFunction<ApiCallRecord, EndpointFeatures, EndpointFeatures>`:

1. **`testCreateAccumulator()`** — Verifies all counters initialize to 0, `isOneHundredPercentSynthetic` defaults to `false`
2. **`testAddRealCall()`** — Creates a real browser call (Mozilla/5.0 UA, auth token, status 200). Verifies: totalCalls=1, syntheticCalls=0, realCalls=1, authTokenCount=1, count2xx=1
3. **`testAddSyntheticCall()`** — Creates a monitoring call (Prometheus/2.0 UA). Verifies: syntheticCalls=1, realCalls=0 (monitor UA classification)
4. **`testAddCallWithoutAuth()`** — Creates a call with `authHeader=null` and status 404. Verifies: noAuthCount=1, authTokenCount=0, count4xx=1
5. **`testGetResultAllSynthetic()`** — Sets totalCalls=100, syntheticCalls=100, realCalls=0. Verifies `isOneHundredPercentSynthetic=true`
6. **`testGetResultNotSynthetic()`** — Sets 50/50 split. Verifies `isOneHundredPercentSynthetic=false`
7. **`testMerge()`** — Creates 2 partial accumulators with different counts, merges them. Verifies all counters summed correctly and `isOneHundredPercentSynthetic=false` (not 100% synthetic since realCalls > 0)
