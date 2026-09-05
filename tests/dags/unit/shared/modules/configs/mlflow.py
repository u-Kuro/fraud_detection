import dataclasses
import pytest
from dags.shared.modules.configs.mlflow import MLflowConfig

def test_mlflow_config_challenger_alias():
    assert MLflowConfig.challenger_alias == "challenger"

def test_mlflow_config_is_frozen():
    config = MLflowConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.challenger_alias = "other"

def test_mlflow_config_instantiation():
    config = MLflowConfig()
    assert config.challenger_alias == "challenger"
