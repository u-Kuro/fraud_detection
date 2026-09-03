import dataclasses
import pytest
from dags.shared.modules.configs.github import GitHubConfig

def test_github_config_default_owner():
    assert GitHubConfig.owner == "u-Kuro"

def test_github_config_default_repository():
    assert GitHubConfig.repository == "fraud_detection_platform"

def test_github_config_is_frozen():
    config = GitHubConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.owner = "other"

def test_github_config_instantiation():
    config = GitHubConfig()
    assert config.owner == "u-Kuro"
    assert config.repository == "fraud_detection_platform"
