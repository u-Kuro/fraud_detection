import dataclasses
import pytest
from dags.shared.modules.configs.airflow.airflow import AirflowConfig

def test_airflow_config_default_environment_prefix():
    assert AirflowConfig.environment_prefix == "AIRFLOW_VAR_"

def test_airflow_config_is_frozen():
    config = AirflowConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.environment_prefix = "other"

def test_airflow_config_instantiation():
    config = AirflowConfig()
    assert config.environment_prefix == "AIRFLOW_VAR_"
