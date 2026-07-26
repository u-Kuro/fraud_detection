from dataclasses import dataclass

@dataclass(frozen=True)
class MLFlowConfig:
    TRACKING_URI:       str = "http://mlflow:5000"
    EXPERIMENT_NAME:    str = "fraud_detection"

    MODEL_PATH:     str = "model"
    MODEL_NAME:     str = "xgboost"
    SCALER_NAME:    str = "robust_scaler"

    REFERENCE_DATASET_PATH:         str = "reference_dataset"
    REFERENCE_DATASET_FILE_NAME:    str = "reference.parquet"