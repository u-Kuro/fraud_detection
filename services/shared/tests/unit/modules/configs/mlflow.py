from services.shared.src.modules.configs.mlflow import MLFlowConfig

def test_mlflow_config_experiment_name_is_string():
    assert isinstance(MLFlowConfig.experiment_name, str)

def test_mlflow_config_model_path_is_string():
    assert isinstance(MLFlowConfig.model_path, str)

def test_mlflow_config_model_name_is_string():
    assert isinstance(MLFlowConfig.model_name, str)

def test_mlflow_config_scaler_name_is_string():
    assert isinstance(MLFlowConfig.scaler_name, str)

def test_mlflow_config_reference_dataset_path_is_string():
    assert isinstance(MLFlowConfig.reference_dataset_path, str)

def test_mlflow_config_reference_dataset_file_name_is_string():
    assert isinstance(MLFlowConfig.reference_dataset_file_name, str)