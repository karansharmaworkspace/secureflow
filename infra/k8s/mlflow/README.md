# MLflow — Experiment Tracking

MLflow v2.13.2 tracking server + model registry + PostgreSQL backend, deployed in the `detect` namespace. Stores ML experiments, model artifacts, and the model registry used by the `train.py` and `predict.py` pipeline.

## Files

### mlflow-deployment.yaml — MLflow Server + DB (100 lines)

**2 Deployments:**

**`mlflow` (MLflow Server):**
- Image: `ghcr.io/mlflow/mlflow:v2.13.2`
- Args: `mlflow server --host 0.0.0.0 --port 5000`
- Backend store: PostgreSQL at `mlflow-db.detect.svc:5432` (user/pass: mlflow)
- Artifact store: MinIO bucket `s3://model-artifacts/`
- Env: `MLFLOW_S3_ENDPOINT_URL=http://minio.remember.svc:9000` (uses MinIO in remember namespace)
- Credentials from `minio-credentials` Secret (cross-namespace reference)
- Port: 5000

**`mlflow-db` (PostgreSQL 16):**
- Image: `postgres:16-alpine`
- Env: POSTGRES_USER=mlflow, PASSWORD=mlflow, DB=mlflow
- Port: 5432

**Service:** ClusterIP exposing port 5000 for MLflow API/UI.

**Integration:** Train script uses `MLFLOW_TRACKING_URI=http://mlflow.detect.svc:5000` to log params (tree count, depth, learning rate), metrics (F1, AUC, precision, recall), the model binary, and SHAP feature importance plots.
