from services.shared.src.modules.configs.mlflow import MLFlowConfig

def test_mlflow_config_values():
    assert isinstance(MLFlowConfig.experiment_name, str)
    assert isinstance(MLFlowConfig.model_path, str)
    assert isinstance(MLFlowConfig.model_name, str)
    assert isinstance(MLFlowConfig.scaler_name, str)
    assert isinstance(MLFlowConfig.reference_dataset_path, str)
    assert isinstance(MLFlowConfig.reference_dataset_file_name, str)