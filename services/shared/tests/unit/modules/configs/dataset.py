from services.shared.src.modules.configs.dataset import DatasetConfig

def test_dataset_config_maximum_dataset_rows_is_int():
    assert isinstance(DatasetConfig.maximum_dataset_rows, int)

def test_dataset_config_maximum_dataset_rows_is_positive():
    assert DatasetConfig.maximum_dataset_rows > 0

def test_dataset_config_minimum_rows_is_int():
    assert isinstance(DatasetConfig.minimum_rows, int)

def test_dataset_config_minimum_rows_is_positive():
    assert DatasetConfig.minimum_rows > 0

def test_dataset_config_maximum_dataset_rows_is_greater_than_or_equal_to_minimum_rows():
    assert DatasetConfig.maximum_dataset_rows >= DatasetConfig.minimum_rows