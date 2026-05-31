import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from features import FEATURE_COLUMNS, TARGET_COLUMN


def test_feature_columns_exist():
    """Test that FEATURE_COLUMNS is defined and contains expected features"""
    assert isinstance(FEATURE_COLUMNS, list)
    assert len(FEATURE_COLUMNS) > 0
    assert "total_calls" in FEATURE_COLUMNS
    assert "is_100pct_synthetic" in FEATURE_COLUMNS


def test_target_column_defined():
    """Test that TARGET_COLUMN is defined"""
    assert isinstance(TARGET_COLUMN, str)
    assert TARGET_COLUMN == "is_zombie"