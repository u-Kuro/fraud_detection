import dataclasses

import pytest

from services.shared.src.modules.configs.mlflow import MLFlowConfig

def test_mlflow_config_experiment_name():
    assert MLFlowConfig.experiment_name == "fraud_detection"

def test_mlflow_config_model_path():
    assert MLFlowConfig.model_path == "model"

def test_mlflow_config_model_name():
    assert MLFlowConfig.model_name == "xgboost"

def test_mlflow_config_scaler_name():
    assert MLFlowConfig.scaler_name == "robust_scaler"

def test_mlflow_config_reference_dataset_path():
    assert MLFlowConfig.reference_dataset_path == "reference_dataset"

def test_mlflow_config_reference_dataset_file_name():
    assert MLFlowConfig.reference_dataset_file_name == "reference.parquet"

def test_mlflow_config_instantiation():
    config = MLFlowConfig()
    assert config.experiment_name == "fraud_detection"
    assert config.model_name == "xgboost"

def test_mlflow_config_is_frozen():
    config = MLFlowConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.model_name = "other"
