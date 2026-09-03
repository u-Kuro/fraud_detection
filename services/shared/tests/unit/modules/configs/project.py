import dataclasses

import pytest

from services.shared.src.modules.configs.project import ProjectConfig

def test_project_config_project_name():
    assert ProjectConfig.project_name == "fraud_detection"

def test_project_config_instantiation():
    config = ProjectConfig()
    assert config.project_name == "fraud_detection"

def test_project_config_is_frozen():
    config = ProjectConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.project_name = "other"
