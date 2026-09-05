from services.archive.src.modules.configs.archive import ArchiveConfig

def test_archive_config_values():
    assert isinstance(ArchiveConfig.batch_size, int)
    assert ArchiveConfig.batch_size > 0