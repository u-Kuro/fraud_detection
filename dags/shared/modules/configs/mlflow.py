from dataclasses import dataclass

@dataclass(frozen=True)
class MLFlowConfig:

    # MLFLOW_ARCHIVED_ALIAS:          str = "archived"
    CHALLENGER_ALIAS:   str = "challenger"

    TRACKING_URI:       str = "http://mlflow:5000"
    EXPERIMENT_NAME:    str = "fraud_detection"

    # MODEL_PATH:         str = "model"
    # MODEL_NAME:         str = "xgboost"
    # SCALER_NAME:        str = "robust_scaler"
    # CHAMPION_ALIAS:     str = "champion"

    # @property
    # def MODEL_URI(self) -> str:
    #     return f"models:/{self.MODEL_NAME}@{self.CHAMPION_ALIAS}"
    #
    # REFERENCE_DATASET_PATH:         str = "reference_dataset"
    # REFERENCE_DATASET_FILE_NAME:    str = "reference.parquet"
    #
    # @property
    # def REFERENCE_DATASET_URI(self) -> str:
    #     return f"{self.MODEL_URI}/{self.REFERENCE_DATASET_PATH}/{self.REFERENCE_DATASET_FILE_NAME}"
