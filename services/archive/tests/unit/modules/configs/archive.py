import dataclasses

import pytest

from services.archive.src.modules.configs.archive import ArchiveConfig

def test_archive_config_default_batch_size():
    assert ArchiveConfig.batch_size == 50_000

def test_archive_config_instantiation():
    config = ArchiveConfig()
    assert config.batch_size == 50_000

def test_archive_config_is_frozen():
    config = ArchiveConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.batch_size = 1

def test_archive_config_batch_size_positive():
    assert ArchiveConfig.batch_size > 0
