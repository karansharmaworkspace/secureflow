import json
import logging
import os
import sys

import mlflow
import numpy as np
import pandas as pd
import shap

from features import FEATURE_COLUMNS

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.remember.svc:5000")
MODEL_URI = os.getenv("MODEL_URI", "models:/zombie-classifier/latest")

ENSEMBLE_DISAGREEMENT_THRESHOLD = 0.3


def load_model(model_uri):
    logger.info(f"Loading model from {model_uri}")
    model = mlflow.xgboost.load_model(model_uri)
    explainer = shap.TreeExplainer(model)
    return model, explainer


def predict(model, explainer, features: pd.DataFrame):
    # Preserve endpoint_key before column selection
    endpoint_keys = features.get("endpoint_key", None)
    features = features[FEATURE_COLUMNS].fillna(0)

    proba = model.predict_proba(features)[:, 1]
    prediction = (proba >= 0.5).astype(int)

    shap_values = explainer.shap_values(features)

    explanations = []
    for i in range(len(features)):
        parts = []
        for j, val in sorted(
            enumerate(shap_values[i]), key=lambda x: abs(x[1]), reverse=True
        ):
            if abs(val) < 0.01:
                continue
            fname = FEATURE_COLUMNS[j]
            fval = features.iloc[i][fname]
            direction = "high" if val > 0 else "low"
            parts.append(f"{fname}={fval:.2f} ({direction}, {val:+.2f})")

        explanations.append({
            "endpoint_key": endpoint_keys.iloc[i] if endpoint_keys is not None else str(i),
            "zombie_probability": float(proba[i]),
            "classification": "zombie" if prediction[i] else "active",
            "explanation": "; ".join(parts[:5]),
            "confidence": float(abs(proba[i] - 0.5) * 2),
        })

    return explanations


def ensemble_predict(models, features):
    all_probas = []
    all_explanations = []

    for model, explainer in models:
        proba = model.predict_proba(features)[:, 1]
        all_probas.append(proba)

        shap_values = explainer.shap_values(features)
        all_explanations.append(shap_values)

    mean_proba = np.mean(all_probas, axis=0)
    max_disagreement = np.max(np.std(all_probas, axis=0))

    final_prediction = (mean_proba >= 0.5).astype(int)
    needs_review = max_disagreement > ENSEMBLE_DISAGREEMENT_THRESHOLD

    return {
        "probabilities": mean_proba.tolist(),
        "predictions": final_prediction.tolist(),
        "ensemble_disagreement": float(max_disagreement),
        "needs_human_review": bool(needs_review),
    }


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model_uri = os.getenv("MODEL_URI", "models:/zombie-classifier/latest")
    
    # Use file-based model path if MLFLOW_TRACKING_URI uses file: scheme
    if MLFLOW_TRACKING_URI.startswith("file:") and model_uri.startswith("models:/"):
        # Extract run_id from the registry and build direct path to model
        client = mlflow.MlflowClient()
        try:
            mv = client.get_latest_versions("zombie-classifier", stages=["None"])
            if mv:
                run_id = mv[0].run_id
                model_uri = f"runs:/{run_id}/model"
        except Exception:
            pass
    
    model, explainer = load_model(model_uri)
    
    # Read JSON with explicit orient='records' for list of objects format
    features = pd.read_json(input_path, orient='records')

    explanations = predict(model, explainer, features)
    print(json.dumps(explanations, indent=2))


if __name__ == "__main__":
    main()
