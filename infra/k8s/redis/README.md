# Redis - In-Memory Cache

Redis Sentinel deployment providing high-availability in-memory caching for the platform. Used for feature caching, session management, and real-time data access.

## Configuration

- 3-node Sentinel cluster for automatic failover
- Persistent storage backing
- TLS encryption for data in transit
- Used by Feast feature store for low-latency feature retrieval
