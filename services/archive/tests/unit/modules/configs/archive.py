from services.archive.src.modules.configs.archive import ArchiveConfig

def test_archive_config_batch_size_is_int():
    config = ArchiveConfig()
    assert isinstance(config.batch_size, int)

def test_archive_config_batch_size_is_positive():
    assert ArchiveConfig.batch_size > 0