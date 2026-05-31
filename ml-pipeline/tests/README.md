# ML Pipeline Tests

Unit tests for the machine learning pipeline components using pytest. Validates feature engineering, model training, and inference logic.

## Files

### conftest.py
Pytest fixtures and shared test configuration. Provides test data generators, mock model instances, and reusable test utilities.

### test_features.py
Tests for feature computation functions. Validates that feature columns are correctly computed from raw endpoint data.

### test_train.py
Tests for the model training pipeline. Validates training workflow, MLflow integration, and model serialization.

### test_predict.py
Tests for the prediction pipeline. Validates model loading, SHAP explanation generation, and prediction output format.
