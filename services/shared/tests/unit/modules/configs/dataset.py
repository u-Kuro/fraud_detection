from services.shared.src.modules.configs.dataset import DatasetConfig

class TestDatasetConfig:
    def test_dataset_config_values(self):
        assert isinstance(DatasetConfig.maximum_dataset_rows, int)
        assert isinstance(DatasetConfig.minimum_rows, int)

        assert DatasetConfig.maximum_dataset_rows >= DatasetConfig.minimum_rows > 0