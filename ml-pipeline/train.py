import json
import logging
import os
import sys
import tempfile
from datetime import datetime

import mlflow
from mlflow.exceptions import MlflowException
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score
)
from sklearn.model_selection import train_test_split

from features import FEATURE_COLUMNS, TARGET_COLUMN

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.remember.svc:5000")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio.remember.svc:9000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "zombie-classification")
DATA_PATH = os.getenv("DATA_PATH", "s3://feature-snapshots/endpoint_features.parquet")


def load_data(path):
    logger.info(f"Loading data from {path}")
    df = pd.read_parquet(path)
    logger.info(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
    return df


def preprocess(df):
    df = df.copy()
    df.loc[:, FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(0)
    df.loc[:, TARGET_COLUMN] = df[TARGET_COLUMN].fillna(0).astype(int)
    return df


def train_xgboost(X_train, y_train, X_val, y_val):
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
        eval_metric=["logloss", "error"],
        random_state=42,
        early_stopping_rounds=20,
        verbosity=1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    return model


def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "accuracy": accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    logger.info(f"Test metrics: {json.dumps(metrics, indent=2)}")
    logger.info(f"\n{classification_report(y_test, y_pred)}")
    logger.info(f"Confusion matrix:\n{confusion_matrix(y_test, y_pred)}")

    return metrics, y_pred, y_proba


def compute_shap(model, X_test):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    feature_importance = np.abs(shap_values).mean(axis=0)
    top_features = sorted(
        zip(FEATURE_COLUMNS, feature_importance),
        key=lambda x: x[1],
        reverse=True,
    )

    logger.info("Top 10 features by SHAP importance:")
    for name, imp in top_features[:10]:
        logger.info(f"  {name}: {imp:.4f}")

    return explainer, shap_values, top_features


def generate_explanation(shap_values, row_idx, features):
    parts = []
    values = shap_values[row_idx]
    for i, val in sorted(enumerate(values), key=lambda x: abs(x[1]), reverse=True):
        if abs(val) < 0.01:
            continue
        feature_name = FEATURE_COLUMNS[i]
        fval = features.iloc[row_idx][feature_name]
        direction = "high" if val > 0 else "low"
        parts.append(f"{feature_name}={fval:.2f} ({direction}, {val:+.2f})")

    return "; ".join(parts[:5])


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    df = load_data(DATA_PATH)
    df = preprocess(df)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    with mlflow.start_run(run_name=f"xgb_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_params({
            "model_type": "XGBoost",
            "n_estimators": 500,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "early_stopping_rounds": 20,
            "feature_count": len(FEATURE_COLUMNS),
            "train_samples": len(X_train),
        })

        model = train_xgboost(X_train, y_train, X_val, y_val)

        metrics, y_pred, y_proba = evaluate(model, X_test, y_test)
        mlflow.log_metrics(metrics)

        explainer, shap_values, top_features = compute_shap(model, X_test)

        sample_explanations = []
        for i in range(min(5, len(X_test))):
            explanation = generate_explanation(shap_values, i, X_test)
            row = X_test.iloc[i]
            sample_explanations.append({
                "sample_idx": i,
                "true_label": int(y_test.iloc[i]),
                "predicted_label": int(y_pred[i]),
                "probability": float(y_proba[i]),
                "explanation": explanation,
            })

        mlflow.log_dict({"sample_explanations": sample_explanations}, "sample_explanations.json")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"top_features": [(name, float(imp)) for name, imp in top_features]}, f)
            mlflow.log_artifact(f.name, "feature_importance")

        mlflow.xgboost.log_model(model, "model")
        logger.info(f"Model logged to MLflow run: {mlflow.active_run().info.run_id}")

        if metrics["f1"] >= 0.85:
            logger.info("F1 >= 0.85 — model ready for production")
            mlflow.set_tag("stage", "ready")
        else:
            logger.warning(f"F1 = {metrics['f1']:.3f} < 0.85 — needs improvement")
            mlflow.set_tag("stage", "needs_improvement")

        # Register model in registry so models:/zombie-classifier/latest resolves
        run_id = mlflow.active_run().info.run_id
        client = mlflow.MlflowClient()
        try:
            client.create_registered_model("zombie-classifier")
            logger.info("Created registered model 'zombie-classifier'")
        except MlflowException:
            logger.info("Registered model 'zombie-classifier' already exists — creating new version")
        client.create_model_version("zombie-classifier", f"runs:/{run_id}/model", run_id)
        logger.info(f"Registered model version for run {run_id}")

    logger.info("Training complete")


if __name__ == "__main__":
    main()
