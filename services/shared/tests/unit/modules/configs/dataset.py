import dataclasses

import pytest

from services.shared.src.modules.configs.dataset import DatasetConfig

def test_dataset_config_default_maximum_dataset_rows():
    assert DatasetConfig.maximum_dataset_rows == 500_000

def test_dataset_config_default_minimum_rows():
    assert DatasetConfig.minimum_rows == 100_000

def test_dataset_config_instantiation():
    config = DatasetConfig()
    assert config.maximum_dataset_rows == 500_000
    assert config.minimum_rows == 100_000

def test_dataset_config_is_frozen():
    config = DatasetConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.maximum_dataset_rows = 1

def test_dataset_config_minimum_less_than_maximum():
    assert DatasetConfig.minimum_rows < DatasetConfig.maximum_dataset_rows
