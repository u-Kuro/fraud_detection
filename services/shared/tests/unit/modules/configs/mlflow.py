from services.shared.src.modules.configs.mlflow import MLflowConfig

class TestMLflowConfig:
    def test_values(self):
        assert isinstance(MLflowConfig.experiment_name, str)
        assert isinstance(MLflowConfig.model_path, str)
        assert isinstance(MLflowConfig.model_name, str)
        assert isinstance(MLflowConfig.scaler_name, str)
        assert isinstance(MLflowConfig.reference_dataset_path, str)
        assert isinstance(MLflowConfig.reference_dataset_file_name, str)