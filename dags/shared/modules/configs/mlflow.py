from dataclasses import dataclass

@dataclass(frozen=True)
class MLFlowConfig:
    CHALLENGER_ALIAS:   str = "challenger"

    TRACKING_URI:       str = "http://mlflow:5000"
    EXPERIMENT_NAME:    str = "fraud_detection"
