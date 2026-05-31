# Feast - Feature Store

Feast feature store deployment providing centralized feature management for the ML pipeline. Serves as the bridge between raw traffic data and ML model features.

## Configuration

- Online store backed by Redis for real-time feature serving
- Offline store backed by MinIO for batch feature computation
- Feature registry for versioning and discovery
- Integration with Flink for streaming feature computation
