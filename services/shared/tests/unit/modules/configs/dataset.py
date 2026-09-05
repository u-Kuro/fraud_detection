from services.shared.src.modules.configs.dataset import DatasetConfig

def test_dataset_config_values():
    assert isinstance(DatasetConfig.maximum_dataset_rows, int)
    assert isinstance(DatasetConfig.minimum_rows, int)

    assert DatasetConfig.maximum_dataset_rows > 0
    assert DatasetConfig.minimum_rows > 0
    assert DatasetConfig.maximum_dataset_rows >= DatasetConfig.minimum_rows