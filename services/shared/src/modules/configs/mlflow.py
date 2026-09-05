from dataclasses import dataclass

@dataclass(frozen=True)
class MLflowConfig:
    experiment_name: str = "fraud_detection"

    model_path:  str = "model"
    model_name:  str = "xgboost"
    scaler_name: str = "robust_scaler"

    reference_dataset_path:      str = "reference_dataset"
    reference_dataset_file_name: str = "reference.parquet"