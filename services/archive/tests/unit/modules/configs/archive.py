from services.archive.src.modules.configs.archive import ArchiveConfig

class TestArchiveConfig:
    def test_values(self):
        assert isinstance(ArchiveConfig.batch_size, int)
        assert ArchiveConfig.batch_size > 0