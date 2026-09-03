import dataclasses
import pytest
from dags.shared.modules.configs.mlflow import MLFlowConfig

def test_mlflow_config_challenger_alias():
    assert MLFlowConfig.challenger_alias == "challenger"

def test_mlflow_config_is_frozen():
    config = MLFlowConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.challenger_alias = "other"

def test_mlflow_config_instantiation():
    config = MLFlowConfig()
    assert config.challenger_alias == "challenger"
