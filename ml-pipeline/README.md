# ML Pipeline

XGBoost-based zombie API classifier with MLflow experiment tracking and SHAP explainability.

## Files

| File | Purpose |
|------|---------|
| `train.py` | Trains XGBoost classifier (500 trees, depth 8) on 16 features. Logs params/metrics to MLflow. Registers model as `zombie-classifier`. Generates SHAP explanations for top features. |
| `predict.py` | Loads trained model from MLflow registry. Predicts zombie probability for input features. Returns classification (active/zombie) with SHAP explanation text. Supports ensemble mode with disagreement detection. |
| `features.py` | Defines the 16 feature columns used for classification: traffic volume, synthetic ratio, auth patterns, HTTP status, payload stats, timing regularity. |
| `requirements.txt` | Python dependencies: xgboost, shap, mlflow, pandas, numpy, scikit-learn, pyarrow, boto3, optuna, cloudpickle. |
| `Dockerfile` | Container image for running training/prediction in Kubernetes. Based on python:3.11-slim. |
| `tests/` | Unit tests for feature definitions, training pipeline, and prediction output format. |

## Usage

```bash
# Train
MLFLOW_TRACKING_URI=http://localhost:5000 python train.py

# Predict
python predict.py features.json
```
