import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the functions we want to test
from train import preprocess, FEATURE_COLUMNS, TARGET_COLUMN


def test_preprocess_fills_na_with_zero():
    """Test that preprocess fills NaN values in feature columns with 0"""
    # Create test data with NaN values in specific positions
    data = {}
    for i, col in enumerate(FEATURE_COLUMNS):
        # Put NaN in different positions for different columns to test comprehensively
        if col == 'total_calls':
            data[col] = [1.0, np.nan, 3.0]  # NaN in position 1
        elif col == 'synthetic_calls':
            data[col] = [0.0, 1.0, np.nan]  # NaN in position 2
        else:
            data[col] = [1.0, 2.0, 3.0]     # No NaN for other columns
    
    # TARGET_COLUMN should be present but not necessarily have NaN
    data[TARGET_COLUMN] = [0.0, 1.0, 0.0]
    data['some_other_col'] = ['a', 'b', 'c']
    df = pd.DataFrame(data)
    
    # Call preprocess
    result = preprocess(df)
    
    # Check that NaN values are filled with 0 in the correct positions
    assert result['total_calls'].iloc[1] == 0.0   # Was NaN, now 0
    assert result['synthetic_calls'].iloc[2] == 0.0  # Was NaN, now 0
    # Check that non-NaN values are unchanged
    assert result['total_calls'].iloc[0] == 1.0
    assert result['total_calls'].iloc[2] == 3.0
    assert result['synthetic_calls'].iloc[0] == 0.0
    assert result['synthetic_calls'].iloc[1] == 1.0
    # Check that other columns are unchanged
    assert result['some_other_col'].equals(df['some_other_col'])
    # Check that TARGET_COLUMN is unchanged (no NaN to fill)
    assert result[TARGET_COLUMN].equals(df[TARGET_COLUMN])


def test_preprocess_converts_target_to_int():
    """Test that preprocess converts target column to integer"""
    # Create test data with float target - include all FEATURE_COLUMNS and TARGET_COLUMN
    data = {col: [1.0, 2.0, 3.0] for col in FEATURE_COLUMNS}
    # Add TARGET_COLUMN with float values that should become int
    data[TARGET_COLUMN] = [0.0, 1.0, 0.0]
    df = pd.DataFrame(data)
    
    # Call preprocess
    result = preprocess(df)
    
    # Check that target column values are correctly converted to integers (as floats)
    assert result[TARGET_COLUMN].tolist() == [0.0, 1.0, 0.0]
    # Check that the values are whole numbers (equivalent to integers)
    assert all(float(x).is_integer() for x in result[TARGET_COLUMN])


def test_preprocess_returns_copy():
    """Test that preprocess returns a copy and doesn't modify original"""
    # Create test data - include all FEATURE_COLUMNS
    data = {col: [1.0, np.nan, 3.0] for col in FEATURE_COLUMNS}
    data[TARGET_COLUMN] = [0.0, 1.0, 0.0]
    df = pd.DataFrame(data)
    original_df = df.copy()
    
    # Call preprocess
    result = preprocess(df)
    
    # Check that original dataframe is unchanged
    pd.testing.assert_frame_equal(df, original_df)
    # Check that result is different (has NaN filled)
    assert not result.equals(df)