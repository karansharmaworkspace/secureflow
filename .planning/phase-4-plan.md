# Phase 4 Plan: ML Classification Engine

**Goal:** Train XGBoost classifier, integrate SHAP explanations, track via MLflow, calibrate to F1 >= 0.85.

## Tasks

### 4.1 Deploy MLflow
- Deploy MLflow Tracking Server on K8s with MinIO as artifact store
- Create experiment `zombie-classification` with tag `team: logic-legion`
- Configure model registry for version management

### 4.2 Build Training Pipeline
- Load feature snapshots from MinIO (historical endpoint_features.parquet)
- Preprocess: handle missing values, normalize numeric features
- Train/val/test split (70/15/15)
- Train XGBoost classifier with hyperparameter tuning (Optuna/RandomSearch)
- Optimize for F1 score, track all runs in MLflow

### 4.3 SHAP Integration
- Compute SHAP values for test set predictions
- Generate plain-English explanation template:
  "Zero real calls in 30 days (-1.92), 100% synthetic traffic (-1.64), no auth token in 90 days (-1.40)"
- Store SHAP baseline values with model artifact

### 4.4 Ensemble Safety Mechanism
- Train 3 XGBoost models with different seeds
- Ensemble disagreement > 0.3 triggers auto human review
- Store per-model predictions and disagreement score with each classification

### 4.5 F1 Calibration (Stage 1)
- Run in evaluation-only mode (no automated actions)
- Collect human-labeled ground truth for Stage 1
- Iterate until F1 >= 0.85 on held-out test set
- Exit criteria: F1 >= 0.85 AND charter signed (Phase 8)

## Success Criteria
1. MLflow tracking all training runs with metrics
2. XGBoost model achieves F1 >= 0.85
3. SHAP produces interpretable explanations for every prediction
4. Ensemble mechanism triggers human review on disagreement > 0.3
5. Model artifact stored in MLflow Model Registry + MinIO

---
*Created: 2026-05-26*
