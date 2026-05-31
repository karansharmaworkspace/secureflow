import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the functions we want to test
from predict import FEATURE_COLUMNS, predict, ensemble_predict


def test_predict_featureselection():
    """Test that predict selects only the FEATURE_COLUMNS"""
    # Create test data with extra columns - include all FEATURE_COLUMNS
    data = {col: [10.0, 5.0] for col in FEATURE_COLUMNS}
    data['extra_col'] = ['should', 'be ignored']
    data['endpoint_key'] = ['endpoint1', 'endpoint2']
    features = pd.DataFrame(data)
    
    # Mock model and explainer
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8], [0.6, 0.4]])
    
    mock_explainer = MagicMock()
    # Return proper shaped SHAP values (2 samples, 16 features each)
    mock_explainer.shap_values.return_value = np.array([
        [0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.3, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ])
    
    # Call predict
    result = predict(mock_model, mock_explainer, features)
    
    # Verify that endpoint_key is preserved
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['endpoint_key'] == 'endpoint1'
    assert result[1]['endpoint_key'] == 'endpoint2'
    assert 'zombie_probability' in result[0]
    assert 'classification' in result[0]
    assert 'explanation' in result[0]
    assert 'confidence' in result[0]


def test_ensemble_predict_shape():
    """Test that ensemble_predict returns correct shaped results"""
    # Create test features
    features = pd.DataFrame({
        'total_calls': [10.0, 5.0],
        'synthetic_calls': [2.0, 1.0]
    })
    
    # Mock models and explainers
    mock_model1 = MagicMock()
    mock_model1.predict_proba.return_value = np.array([[0.2, 0.8], [0.6, 0.4]])
    mock_explainer1 = MagicMock()
    mock_explainer1.shap_values.return_value = np.array([[[0.1, 0.2]], [[0.3, 0.4]]])
    
    mock_model2 = MagicMock()
    mock_model2.predict_proba.return_value = np.array([[0.3, 0.7], [0.4, 0.6]])
    mock_explainer2 = MagicMock()
    mock_explainer2.shap_values.return_value = np.array([[[0.2, 0.1]], [[0.1, 0.5]]])
    
    models = [(mock_model1, mock_explainer1), (mock_model2, mock_explainer2)]
    
    # Call ensemble_predict
    result = ensemble_predict(models, features)
    
    # Check result structure
    assert isinstance(result, dict)
    assert 'probabilities' in result
    assert 'predictions' in result
    assert 'ensemble_disagreement' in result
    assert 'needs_human_review' in result
    
    # Check shapes
    assert len(result['probabilities']) == 2  # Two data points
    assert len(result['predictions']) == 2
    assert isinstance(result['ensemble_disagreement'], float)
    assert isinstance(result['needs_human_review'], bool)


def test_ensemble_predict_disagreement_threshold():
    """Test that ensemble_predict correctly identifies when disagreement exceeds threshold"""
    # Create test features
    features = pd.DataFrame({
        'total_calls': [10.0],
        'synthetic_calls': [2.0]
    })
    
    # Mock models that disagree significantly (> 0.3 threshold)
    mock_model1 = MagicMock()
    mock_model1.predict_proba.return_value = np.array([[0.1, 0.9]])  # 90% zombie
    mock_explainer1 = MagicMock()
    mock_explainer1.shap_values.return_value = np.array([[[0.1, 0.2]]])
    
    mock_model2 = MagicMock()
    mock_model2.predict_proba.return_value = np.array([[0.8, 0.2]])  # 20% zombie
    mock_explainer2 = MagicMock()
    mock_explainer2.shap_values.return_value = np.array([[[0.3, 0.4]]])
    
    models = [(mock_model1, mock_explainer1), (mock_model2, mock_explainer2)]
    
    # Call ensemble_predict
    result = ensemble_predict(models, features)
    
    # Should detect disagreement and flag for human review
    assert result['needs_human_review'] == True
    assert result['ensemble_disagreement'] > 0.3