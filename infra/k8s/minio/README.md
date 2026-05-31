# MinIO — Object Storage

S3-compatible object storage in the `remember` namespace. Stores feature snapshots (Parquet), ML model artifacts (MLflow), and compliance documentation. Exposes both S3 API (port 9000) and web console (port 9001).

## Files

### minio-deployment.yaml — MinIO Server (81 lines)

**Resources:**
- **PVC:** 100Gi `ReadWriteOnce` persistent volume for data
- **Deployment:** Single `minio/minio:latest` container
- **Args:** `server /data --console-address :9001`
- **Credentials:** From Kubernetes Secret (`minio-credentials`) — root-user/minioadmin, root-password/minioadmin123
- **Ports:** 9000 (S3 API), 9001 (Web Console)
- **Service:** ClusterIP exposing both ports

### minio-buckets.yaml — Bucket Initialization Job (24 lines)

Kubernetes Job using `minio/mc:latest` (MinIO Client) image. Creates 3 buckets with download policies:
- `historical-logs` — Raw Zeek/WAF logs (30-day retention)
- `model-artifacts` — MLflow model binaries and artifacts
- `feature-snapshots` — Parquet feature files for Feast offline store (90-day retention)

Uses hardcoded credentials (`minioadmin`/`minioadmin123`) — acceptable for demo/development only.
