# ML Pipeline Tests

pytest unit tests for the machine learning pipeline. Covers feature definitions, data preprocessing, training, prediction, and ensemble disagreement detection.

## Files

### conftest.py — Pytest Configuration (6 lines)

Adds the parent `ml-pipeline/` directory to `sys.path` so test files can import `from features import ...`, `from train import ...`, and `from predict import ...`.

### test_features.py — Feature Definition Tests (19 lines)

3 tests:
- `test_feature_columns_exist` — Verifies `FEATURE_COLUMNS` is a non-empty list containing expected features like `total_calls` and `is_100pct_synthetic`
- `test_target_column_defined` — Verifies `TARGET_COLUMN == "is_zombie"`

### test_train.py — Training Pipeline Tests (81 lines)

3 tests for the `preprocess()` function from `train.py`:
- `test_preprocess_fills_na_with_zero` — Creates test DataFrame with NaN in specific positions, verifies NaN filled with 0, non-NaN values unchanged, extra columns preserved
- `test_preprocess_converts_target_to_int` — Verifies target column values are whole numbers (ready for classification)
- `test_preprocess_returns_copy` — Verifies preprocessing doesn't mutate the original DataFrame (immutability)

### test_predict.py — Prediction Pipeline Tests (112 lines)

3 tests for `predict()` and `ensemble_predict()` from `predict.py`:
- `test_predict_featureselection` — Verifies `predict()` selects only feature columns (ignores extra_col, endpoint_key), returns list with correct keys (endpoint_key, zombie_probability, classification, explanation, confidence)
- `test_ensemble_predict_shape` — Tests `ensemble_predict()` with 2 mock models. Verifies result dict has probabilities, predictions, ensemble_disagreement (float), needs_human_review (bool)
- `test_ensemble_predict_disagreement_threshold` — Creates models that disagree significantly (90% zombie vs 20% zombie = 0.7 disagreement). Verifies `needs_human_review == True` and `ensemble_disagreement > 0.3` threshold
